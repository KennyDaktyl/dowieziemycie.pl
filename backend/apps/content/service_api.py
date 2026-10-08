"""API of the service category pages ("Transport rzeczy") and of the quote
request form on them.

GET  /api/service-pages/                    published pages (?parent=<slug>, ?homepage=1, ?top=1)
GET  /api/service-pages/<slug>/             one page with pricing, gallery, subpages
GET  /api/goods-transport-pricing/          the goods-transport rates (edited in Admin)
POST /api/transport-inquiries/              multipart quote request (+ up to 5 photos)
"""

import logging
import threading
from datetime import date

from django.db import transaction
from django.db.models import Q
from PIL import Image, UnidentifiedImageError
from rest_framework import generics, serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import (
    GoodsTransportPricing,
    ServicePage,
    ServicePagePhoto,
    ServicePricingOption,
    TransportInquiry,
    TransportInquiryPhoto,
)

logger = logging.getLogger(__name__)

MAX_PHOTOS = 5
MAX_PHOTO_BYTES = 8 * 1024 * 1024
ALLOWED_PHOTO_FORMATS = {"JPEG", "PNG", "WEBP"}


# --- pages --------------------------------------------------------------------


class ServicePricingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePricingOption
        fields = [
            "code", "name_pl", "name_en", "description_pl", "description_en", "price_from",
            "price_note_pl", "price_note_en", "on_request", "order",
        ]


class ServicePagePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePagePhoto
        fields = ["image", "thumbnail", "width", "height", "alt_pl", "alt_en", "caption_pl", "caption_en", "order"]


LIST_FIELDS = [
    "slug", "parent_slug", "menu_label_pl", "menu_label_en", "title_pl", "title_en", "lead_pl", "lead_en",
    "tile_icon", "tile_title_pl", "tile_title_en", "tile_body_pl", "tile_body_en", "noindex", "updated_at",
]


class ServicePageListSerializer(serializers.ModelSerializer):
    parent_slug = serializers.CharField(source="parent.slug", default=None, read_only=True)

    class Meta:
        model = ServicePage
        fields = LIST_FIELDS


class ServicePageDetailSerializer(ServicePageListSerializer):
    parent_menu_label_pl = serializers.CharField(source="parent.menu_label_pl", default=None, read_only=True)
    parent_menu_label_en = serializers.CharField(source="parent.menu_label_en", default=None, read_only=True)
    pricing_options = ServicePricingOptionSerializer(many=True, read_only=True)
    photos = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = ServicePage
        fields = LIST_FIELDS + [
            "parent_menu_label_pl", "parent_menu_label_en", "h1_pl", "h1_en", "body_pl", "body_en",
            "seo_title_pl", "seo_title_en", "seo_description_pl", "seo_description_en", "cover_image",
            "default_item_type", "pricing_options", "photos", "children",
        ]

    def get_photos(self, page):
        photos = [photo for photo in page.photos.all() if photo.is_visible]
        return ServicePagePhotoSerializer(photos, many=True, context=self.context).data

    def get_children(self, page):
        children = page.children.filter(is_published=True)
        return ServicePageListSerializer(children, many=True, context=self.context).data


def _published(request):
    # A subpage of an unpublished category is unreachable too.
    return ServicePage.objects.filter(is_published=True, site=request.site_code).filter(
        Q(parent__isnull=True) | Q(parent__is_published=True)
    )


class ServicePageListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServicePageListSerializer

    def get_queryset(self):
        qs = _published(self.request).select_related("parent")
        params = self.request.query_params
        if params.get("parent"):
            qs = qs.filter(parent__slug=params["parent"])
        if params.get("top"):
            qs = qs.filter(parent__isnull=True)
        if params.get("homepage"):
            qs = qs.filter(show_on_homepage=True)
        return qs


class ServicePageDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServicePageDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return _published(self.request).select_related("parent").prefetch_related("pricing_options", "photos")


class GoodsTransportPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsTransportPricing
        fields = [
            "hourly_rate", "night_hourly_rate", "day_starts_at", "night_starts_at", "price_per_100km",
            "trailer_price_per_day", "loading_price_from", "updated_at",
        ]


class GoodsTransportPricingView(generics.RetrieveAPIView):
    """GET /api/goods-transport-pricing/ — this brand's goods-transport rates."""

    permission_classes = [AllowAny]
    serializer_class = GoodsTransportPricingSerializer

    def get_object(self):
        from django.shortcuts import get_object_or_404

        return get_object_or_404(GoodsTransportPricing, site=self.request.site_code)


# --- quote requests -----------------------------------------------------------


class TransportInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportInquiry
        fields = [
            "name", "phone", "email", "item_type", "description", "vehicle_option", "pickup_address",
            "dropoff_address", "preferred_date", "needs_carrying", "source_page", "utm_source", "utm_medium",
            "utm_campaign", "locale", "consent",
        ]
        extra_kwargs = {"description": {"max_length": 3000}}

    def validate_phone(self, value):
        digits = "".join(ch for ch in value if ch.isdigit())
        if not 9 <= len(digits) <= 15:
            raise serializers.ValidationError("Podaj poprawny numer telefonu.")
        return value.strip()

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError("Zgoda na przetwarzanie danych jest wymagana.")
        return value

    def validate_preferred_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError("Data nie może być w przeszłości.")
        return value


def _validate_photos(files):
    if len(files) > MAX_PHOTOS:
        raise serializers.ValidationError({"photos": [f"Możesz dodać maksymalnie {MAX_PHOTOS} zdjęć."]})
    for upload in files:
        if upload.size > MAX_PHOTO_BYTES:
            raise serializers.ValidationError({"photos": [f"Plik {upload.name} jest większy niż 8 MB."]})
        try:
            with Image.open(upload) as img:
                img.verify()
                fmt = img.format
        except (UnidentifiedImageError, OSError, SyntaxError):
            raise serializers.ValidationError({"photos": [f"Plik {upload.name} nie jest obrazem."]})
        finally:
            upload.seek(0)
        if fmt not in ALLOWED_PHOTO_FORMATS:
            raise serializers.ValidationError({"photos": ["Dozwolone formaty zdjęć: JPG, PNG, WebP."]})


class TransportInquiryCreateView(APIView):
    """Public form endpoint: honeypot (a filled `website` field gets a fake
    success and nothing is saved), 5 requests/hour per IP, photo count/size/
    type checked server-side, consent required."""

    permission_classes = [AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "transport-inquiry"

    def post(self, request):
        if request.data.get("website"):
            logger.info("Transport inquiry honeypot hit — dropped")
            return Response({"ok": True}, status=status.HTTP_201_CREATED)

        serializer = TransportInquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        files = request.FILES.getlist("photos")
        _validate_photos(files)

        with transaction.atomic():
            inquiry = serializer.save(site=request.site_code)
            for upload in files:
                TransportInquiryPhoto.objects.create(inquiry=inquiry, image=upload)

        admin_url = request.build_absolute_uri(f"/admin/content/transportinquiry/{inquiry.pk}/change/")
        transaction.on_commit(
            lambda: threading.Thread(target=notify_of_inquiry, args=(inquiry.pk, admin_url), daemon=True).start()
        )
        return Response({"ok": True, "id": inquiry.pk}, status=status.HTTP_201_CREATED)


def notify_of_inquiry(inquiry_id, admin_url):
    """Same channels as a new booking: dispatcher email + SMS + app push."""
    from apps.bookings.models import BookingSettings
    from apps.bookings.notifications import _send_email, _send_sms
    from config.sites import SITE_DISPLAY_NAMES

    try:
        inquiry = TransportInquiry.objects.get(pk=inquiry_id)
        site_name = SITE_DISPLAY_NAMES.get(inquiry.site, inquiry.site)
        booking_settings = BookingSettings.for_site(inquiry.site)
        option = inquiry.get_vehicle_option_display()
        _send_sms(
            booking_settings.dispatcher_phone,
            f"{site_name}: nowe zapytanie o transport ({inquiry.get_item_type_display()}, {option}) "
            f"od {inquiry.name}, tel. {inquiry.phone}.",
            inquiry.site,
        )
        lines = [
            f"Rodzaj: {inquiry.get_item_type_display()}",
            f"Opcja: {option}",
            f"Skąd: {inquiry.pickup_address}",
            f"Dokąd: {inquiry.dropoff_address}",
            f"Termin: {inquiry.preferred_date or 'nie podano'}",
            f"Pomoc przy wnoszeniu: {'tak' if inquiry.needs_carrying else 'nie'}",
            f"Klient: {inquiry.name}, {inquiry.phone}{', ' + inquiry.email if inquiry.email else ''}",
            f"Zdjęcia: {inquiry.photos.count()}",
            "",
            inquiry.description,
            "",
            f"Strona: {inquiry.source_page or '-'} | UTM: {inquiry.utm_source or '-'}/{inquiry.utm_medium or '-'}"
            f"/{inquiry.utm_campaign or '-'}",
            f"Szczegóły i zdjęcia: {admin_url}",
        ]
        _send_email(
            booking_settings.dispatcher_email,
            f"{site_name}: zapytanie #{inquiry.pk} — {inquiry.get_item_type_display()} ({option})",
            "\n".join(lines),
            inquiry.site,
        )

        from apps.fleet.models import Driver
        from apps.fleet.push import send_push

        tokens = Driver.objects.filter(is_dispatcher=True).exclude(expo_push_token="").values_list(
            "expo_push_token", flat=True,
        )
        for token in tokens:
            send_push(
                token,
                title="Nowe zapytanie o transport rzeczy",
                body=f"{inquiry.get_item_type_display()}: {inquiry.pickup_address} → {inquiry.dropoff_address}",
                data={"type": "transport_inquiry", "inquiry_id": inquiry.pk},
            )
    except Exception:
        logger.exception("Powiadomienie o zapytaniu #%s nie wysłane", inquiry_id)
