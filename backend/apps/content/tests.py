import io
import re
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient, APITestCase

from apps.fleet.models import Vehicle

from .models import (
    BlogPost,
    BlogPostLink,
    ContentPage,
    FixedRoute,
    FixedRoutePhoto,
    FixedRouteVehiclePrice,
    Tour,
    TourVehiclePrice,
)


def _make_test_image_upload(name="photo.png", size=(800, 600), color=(200, 50, 50)) -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class VehiclePhotosInPricingTests(APITestCase):
    """The booking form shows the vehicle's gallery next to its cover photo."""

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_route_and_tour_prices_carry_the_vehicles_gallery_in_order(self):
        from apps.fleet.models import VehiclePhoto

        vehicle = Vehicle.objects.create(name="Volkswagen", plate="GAL1", seats=6)
        second = VehiclePhoto.objects.create(vehicle=vehicle, image=_make_test_image_upload("b.png"), order=2)
        first = VehiclePhoto.objects.create(vehicle=vehicle, image=_make_test_image_upload("a.png"), order=1)
        route = FixedRoute.objects.create(site="transfer247", slug="gal-route", name_pl="G", name_en="G")
        FixedRouteVehiclePrice.objects.create(route=route, vehicle=vehicle, price=100)
        tour = Tour.objects.create(site="transfer247", slug="gal-tour", title_pl="G", title_en="G")
        TourVehiclePrice.objects.create(tour=tour, vehicle=vehicle, price=100)

        for url in ("/api/fixed-routes/gal-route/", "/api/tours/gal-tour/"):
            photos = self.client.get(url, HTTP_X_SITE="transfer247").data["vehicle_prices"][0]["vehicle_photos"]
            self.assertEqual([p["order"] for p in photos], [1, 2], url)
            self.assertTrue(photos[0]["image"].endswith(".webp") and photos[0]["thumbnail"].endswith(".webp"))

    def test_no_extra_queries_per_vehicle_price(self):
        vehicles = [Vehicle.objects.create(name=f"V{i}", plate=f"Q{i}") for i in range(3)]
        route = FixedRoute.objects.create(site="transfer247", slug="q-route", name_pl="Q", name_en="Q")
        for v in vehicles:
            FixedRouteVehiclePrice.objects.create(route=route, vehicle=v, price=100)
        with self.assertNumQueries(5):  # constant — would grow per vehicle without the photos prefetch
            self.client.get("/api/fixed-routes/q-route/", HTTP_X_SITE="transfer247")


class VehiclePricingTests(APITestCase):
    """Price is per real vehicle from the fleet — however many vehicles a
    route/tour has been priced for, not a hardcoded pair of fields. See
    migration 0019 for why this replaced price_from/price_large_vehicle."""

    def setUp(self):
        self.client = APIClient()
        self.route = FixedRoute.objects.create(
            site="transfer247", slug="test-route", name_pl="Test", name_en="Test",
        )

    def test_route_with_no_prices_reports_none(self):
        res = self.client.get("/api/fixed-routes/test-route/", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.data["price_from"])
        self.assertEqual(res.data["vehicle_prices"], [])

    def test_adding_a_third_vehicle_just_adds_a_third_price_row(self):
        """The whole point: this isn't capped at two."""
        names = ["Toyota Auris Hybrid", "Ford Tourneo Custom", "Mercedes Vito"]
        for i, name in enumerate(names):
            vehicle = Vehicle.objects.create(name=name, plate=f"TEST{i}")
            FixedRouteVehiclePrice.objects.create(route=self.route, vehicle=vehicle, price=100 + i * 50)

        res = self.client.get("/api/fixed-routes/test-route/", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["vehicle_prices"]), 3)
        self.assertEqual({vp["vehicle_name"] for vp in res.data["vehicle_prices"]}, set(names))
        self.assertEqual(float(res.data["price_from"]), 100.0)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImageProcessingTests(TestCase):
    """Every upload goes through the same WebP + thumbnail pipeline — see
    common/imaging.py. No model should be able to opt out. Uses an isolated
    MEDIA_ROOT so test uploads don't land in the real media/ directory."""

    def test_gallery_photo_is_converted_to_webp_with_a_thumbnail(self):
        route = FixedRoute.objects.create(
            site="transfer247", slug="img-route", name_pl="Test", name_en="Test",
        )
        photo = FixedRoutePhoto.objects.create(route=route, image=_make_test_image_upload())

        self.assertTrue(photo.image.name.endswith(".webp"))
        self.assertTrue(photo.thumbnail.name.endswith(".webp"))

        thumb = Image.open(photo.thumbnail)
        self.assertLessEqual(thumb.width, 480)
        self.assertLessEqual(thumb.height, 480)


class SiteScopingTests(APITestCase):
    """The two brands share one backend — a request is scoped to a site by
    the X-Site header (SiteMiddleware), defaulting to dowieziemycie when the
    header is missing so the not-yet-updated frontend keeps working."""

    def setUp(self):
        self.client = APIClient()

    def test_home_content_defaults_to_dowieziemycie_without_header(self):
        res = self.client.get("/api/home-content/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Bezpieczny", res.data["headline_pl"])

    def test_home_content_switches_with_x_site_header(self):
        res = self.client.get("/api/home-content/", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 200)
        self.assertIn("lotniska", res.data["headline_pl"])

    def test_home_content_unknown_site_header_falls_back_to_default(self):
        res = self.client.get("/api/home-content/", HTTP_X_SITE="not-a-real-site")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Bezpieczny", res.data["headline_pl"])

    def test_fixed_routes_only_visible_for_transfer247(self):
        res_default = self.client.get("/api/fixed-routes/")
        self.assertEqual(res_default.status_code, 200)
        self.assertEqual(len(res_default.data), 0)

        res_transfer247 = self.client.get("/api/fixed-routes/", HTTP_X_SITE="transfer247")
        self.assertEqual(res_transfer247.status_code, 200)
        self.assertEqual(len(res_transfer247.data), 8)  # incl. krakow-zakopane (migration 0067)

    def test_tours_are_scoped_per_site(self):
        res_default = self.client.get("/api/tours/")
        default_slugs = {t["slug"] for t in res_default.data}
        self.assertNotIn("auschwitz-birkenau-transfer247", default_slugs)

        res_transfer247 = self.client.get("/api/tours/", HTTP_X_SITE="transfer247")
        transfer_slugs = {t["slug"] for t in res_transfer247.data}
        self.assertIn("auschwitz-birkenau-transfer247", transfer_slugs)
        self.assertIn("wieliczka-transfer247", transfer_slugs)

    def test_blog_posts_are_scoped_per_site(self):
        res_default = self.client.get("/api/blog/")
        default_slugs = {p["slug"] for p in res_default.data}
        self.assertIn("transport-z-imprezy-do-domu-krakow", default_slugs)
        self.assertNotIn("krakow-airport-transfer-to-hotel-guide", default_slugs)

        res_transfer247 = self.client.get("/api/blog/", HTTP_X_SITE="transfer247")
        transfer_slugs = {p["slug"] for p in res_transfer247.data}
        self.assertIn("krakow-airport-transfer-to-hotel-guide", transfer_slugs)
        self.assertNotIn("transport-z-imprezy-do-domu-krakow", transfer_slugs)


class InternalCmsLinkIntegrityTests(TestCase):
    """Catches the class of bug behind migration 0063: a CMS markdown link
    (route/tour/blog/page body, or a BlogPostLink) pointing at an internal
    page that was since renamed, re-categorized (the /transfery <->
    /transfery-lotniskowe split), or deleted — the exact 404/redirect churn
    GSC's coverage report keeps flagging. Runs against whatever the
    migrations have actually seeded, computed live from the DB (not a
    hardcoded slug list), so it fails the moment ANY future migration or
    Admin edit introduces a dead internal link, without waiting for a GSC
    report or a live crawl to notice.

    This only covers slug-addressable content (/transfery/<slug>,
    /wycieczki/<slug>, /blog/<slug>, ...) that this backend actually knows
    about. Static single-segment pages (/kontakt, /flota, ...) and
    everything else server-rendered are covered instead by
    scripts/check-internal-links.mjs in the frontend repo, which crawls the
    real deployed site."""

    LINK_RE = re.compile(r"\]\((/[a-z0-9/_-]+)\)")

    TEXT_FIELDS = {
        FixedRoute: ["body_pl", "body_en", "body_de"],
        Tour: ["body_pl", "body_en", "body_de"],
        BlogPost: ["body_pl", "body_en", "body_de"],
        ContentPage: ["body_pl", "body_en"],
    }

    SECTION_RE = re.compile(r"^/(transfery-lotniskowe|transfery|wycieczki|blog)/([a-z0-9-]+)$")

    def _all_internal_links(self):
        """Yields (source_label, path) for every markdown link found."""
        for model, fields in self.TEXT_FIELDS.items():
            for obj in model.objects.all():
                for field in fields:
                    text = getattr(obj, field, None) or ""
                    for match in self.LINK_RE.finditer(text):
                        yield f"{model.__name__}:{obj.site}:{obj.slug}:{field}", match.group(1)
        for link in BlogPostLink.objects.select_related("post").all():
            if link.url.startswith("/"):
                yield f"BlogPostLink:{link.post.site}:{link.post.slug}", link.url

    def test_no_locale_prefixed_markdown_links(self):
        """Bodies are authored locale-agnostic — MarkdownContent adds the
        /pl /en /de prefix at render time (see frontend commit d45f46e). A
        link that already hardcodes one would get double-prefixed
        (/pl/pl/...) instead."""
        offenders = [
            (src, path) for src, path in self._all_internal_links() if re.match(r"^/(pl|en|de)(/|$)", path)
        ]
        self.assertEqual(offenders, [], f"CMS links must not hardcode a locale prefix: {offenders}")

    def test_internal_links_resolve_to_a_real_page(self):
        routes_by_site: dict[str, dict[str, str]] = {}
        tours_by_site: dict[str, set[str]] = {}
        posts_by_site: dict[str, set[str]] = {}

        for r in FixedRoute.objects.all():
            routes_by_site.setdefault(r.site, {})[r.slug] = r.category
        for t in Tour.objects.all():
            tours_by_site.setdefault(t.site, set()).add(t.slug)
        for p in BlogPost.objects.all():
            posts_by_site.setdefault(p.site, set()).add(p.slug)

        offenders = []
        for source, path in self._all_internal_links():
            site = source.split(":", 2)[1]
            match = self.SECTION_RE.match(path)
            if not match:
                continue  # static page, out of scope for this DB-level check
            section, slug = match.groups()
            if section == "transfery-lotniskowe":
                ok = routes_by_site.get(site, {}).get(slug) == FixedRoute.Category.LOTNISKO
            elif section == "transfery":
                ok = routes_by_site.get(site, {}).get(slug) == FixedRoute.Category.TRANSFER
            elif section == "wycieczki":
                ok = slug in tours_by_site.get(site, set())
            else:
                ok = slug in posts_by_site.get(site, set())
            if not ok:
                offenders.append((source, path))

        self.assertEqual(
            offenders,
            [],
            f"CMS content links to a page that doesn't exist under that exact URL "
            f"(deleted, renamed, or filed under the wrong category): {offenders}",
        )


class FixedRouteDefaultPinsTests(APITestCase):
    """Admin-pinned start/end for a fixed route — pre-fills the booking form
    (the customer can still change either). All optional."""

    def setUp(self):
        self.route = FixedRoute.objects.create(
            site="transfer247", slug="pins-route", name_pl="Pins", name_en="Pins",
        )

    def test_api_returns_null_when_no_pins_are_set(self):
        res = self.client.get("/api/fixed-routes/pins-route/", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.data["default_pickup"])
        self.assertIsNone(res.data["default_dropoff"])

    def test_api_returns_label_and_numeric_coordinates(self):
        self.route.default_pickup_label = "Lotnisko Katowice"
        self.route.default_pickup_lat = "50.474311"
        self.route.default_pickup_lng = "19.080156"
        self.route.save()
        res = self.client.get("/api/fixed-routes/pins-route/", HTTP_X_SITE="transfer247")
        self.assertEqual(
            res.data["default_pickup"], {"label": "Lotnisko Katowice", "lat": 50.474311, "lng": 19.080156},
        )
        self.assertIsNone(res.data["default_dropoff"])  # one pin can be set without the other

    def test_half_a_coordinate_pair_is_rejected(self):
        from django.core.exceptions import ValidationError

        self.route.default_dropoff_lat = "50.05"
        with self.assertRaises(ValidationError) as ctx:
            self.route.full_clean()
        self.assertIn("default_dropoff_lat", ctx.exception.message_dict)

    def test_admin_change_page_renders_the_pin_map(self):
        from django.contrib.auth.models import User

        User.objects.create_superuser("pin-admin", "a@b.pl", "pw")
        self.client.login(username="pin-admin", password="pw")
        res = self.client.get(f"/admin/content/fixedroute/{self.route.id}/change/")
        self.assertEqual(res.status_code, 200)
        html = res.content.decode()
        for needle in ("id=\"rp-map\"", "id_default_pickup_lat", "id_default_dropoff_lng", "Ustaw START"):
            self.assertIn(needle, html)


class KrakowZakopaneTransferTests(TestCase):
    """The Kraków – Zakopane transfer page, seeded by migration 0067."""

    def setUp(self):
        self.route = FixedRoute.objects.get(slug="krakow-zakopane")

    def test_is_a_published_transfer247_transfer_with_its_own_url_section(self):
        self.assertEqual((self.route.site, self.route.category, self.route.is_published), ("transfer247", "TRANSFER", True))

    def test_price_is_599_pln_and_136_eur_per_vehicle(self):
        prices = list(self.route.vehicle_prices.all())
        self.assertTrue(prices, "no vehicle was priced — is there an active fleet vehicle?")
        for price in prices:
            self.assertEqual((str(price.price), str(price.price_eur)), ("599.00", "136.00"))

    def test_copy_uses_the_required_phrases_in_every_language(self):
        expectations = {
            "pl": ("mikrobus dla 6 pasażerów", "Volkswagen Multivan", "fotelami kapitańskimi", "klimatyzacją"),
            "en": ("minibus for 6 passengers", "Volkswagen Multivan", "captain's chairs", "air conditioning"),
            "de": ("Kleinbus für 6 Personen", "Volkswagen Multivan", "Captain Chairs", "Klimaanlage"),
        }
        for lang, phrases in expectations.items():
            haystacks = {
                "body": getattr(self.route, f"body_{lang}"),
                "h1+seo": " ".join(getattr(self.route, f"{f}_{lang}") for f in ("h1", "seo_title", "seo_description")),
            }
            body = haystacks["body"].lower()
            for phrase in phrases:
                self.assertIn(phrase.lower(), body, f"{lang}: '{phrase}' missing from the body")
            seo = haystacks["h1+seo"].lower()
            self.assertIn(phrases[0].lower(), seo, f"{lang}: main phrase missing from h1/seo")

    def test_every_language_has_name_h1_seo_and_a_full_body_with_faq(self):
        for lang in ("pl", "en", "de"):
            for field in ("name", "h1", "seo_title", "seo_description", "body"):
                self.assertTrue(getattr(self.route, f"{field}_{lang}"), f"{field}_{lang} is empty")
            self.assertIn("## FAQ", getattr(self.route, f"body_{lang}"))
            self.assertLessEqual(len(getattr(self.route, f"seo_title_{lang}")), 70)
            self.assertLessEqual(len(getattr(self.route, f"seo_description_{lang}")), 320)

    def test_no_hardcoded_price_in_the_copy_or_seo(self):
        """The price table is the single source — an amount typed into the text
        goes stale the day the price changes."""
        for lang in ("pl", "en", "de"):
            text = " ".join(
                getattr(self.route, f"{f}_{lang}") for f in ("body", "h1", "seo_title", "seo_description")
            )
            for amount in ("599", "136", "zł", "PLN", "EUR", "€"):
                self.assertNotIn(amount, text, f"{lang}: '{amount}' hardcoded in the copy")

    def test_api_exposes_it_for_transfer247_only(self):
        res = self.client.get("/api/fixed-routes/krakow-zakopane/", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["category"], "TRANSFER")
        self.assertEqual(self.client.get("/api/fixed-routes/krakow-zakopane/").status_code, 404)  # not on dowieziemycie

    def test_default_pins_are_a_complete_pair(self):
        self.route.full_clean()  # lat+lng must come together
        self.assertIsNotNone(self.route.default_pickup)
        self.assertIsNotNone(self.route.default_dropoff)


class EventDriverPricingTests(APITestCase):
    """Hourly driver-rental rates for /imprezy and /cennik (weddings, etc.)."""

    def test_api_auto_creates_and_returns_the_sites_rates(self):
        res = self.client.get("/api/event-driver-pricing/")  # no X-Site -> defaults to dowieziemycie
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            (res.data["day_hourly_rate"], res.data["night_hourly_rate"], res.data["price_per_100km"]),
            ("90.00", "120.00", "100.00"),
        )
        self.assertEqual((res.data["day_starts_at"], res.data["night_starts_at"]), ("06:00:00", "22:00:00"))

    def test_rates_are_scoped_per_site(self):
        from .models import EventDriverPricing

        pricing = EventDriverPricing.for_site("transfer247")
        pricing.day_hourly_rate = 150
        pricing.save(update_fields=["day_hourly_rate"])

        res_t247 = self.client.get("/api/event-driver-pricing/", HTTP_X_SITE="transfer247")
        self.assertEqual(res_t247.data["day_hourly_rate"], "150.00")
        res_dwz = self.client.get("/api/event-driver-pricing/")
        self.assertEqual(res_dwz.data["day_hourly_rate"], "90.00")

    def test_inactive_pricing_returns_null_instead_of_stale_numbers(self):
        from .models import EventDriverPricing

        pricing = EventDriverPricing.for_site("dowieziemycie")
        pricing.is_active = False
        pricing.save(update_fields=["is_active"])

        res = self.client.get("/api/event-driver-pricing/")
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.data)

    def test_migration_seeded_both_brands(self):
        from .models import EventDriverPricing

        self.assertEqual(
            {(p.site, str(p.day_hourly_rate), str(p.night_hourly_rate), str(p.price_per_100km))
             for p in EventDriverPricing.objects.all()},
            {("dowieziemycie", "90.00", "120.00", "100.00"), ("transfer247", "90.00", "120.00", "100.00")},
        )


class VehicleDeletionIsProtectedTests(TestCase):
    """Regression test for a real incident (2026-10-02): deleting the fleet's
    only Vehicle from the admin cascaded away every FixedRouteVehiclePrice/
    TourVehiclePrice/VehiclePhoto row with it, breaking every booking form
    until manually restored from a backup. Vehicle's FKs from these models
    must now be PROTECT, not CASCADE — deleting a still-referenced vehicle
    should raise, not silently wipe pricing/gallery data."""

    def setUp(self):
        self.vehicle = Vehicle.objects.create(name="Test Van", plate="TEST001", seats=6)

    def test_cannot_delete_a_vehicle_still_priced_for_a_route(self):
        from django.db.models import ProtectedError

        route = FixedRoute.objects.create(site="transfer247", slug="protect-route", name_pl="R", name_en="R")
        FixedRouteVehiclePrice.objects.create(route=route, vehicle=self.vehicle, price=100)
        with self.assertRaises(ProtectedError):
            self.vehicle.delete()
        self.assertTrue(Vehicle.objects.filter(id=self.vehicle.id).exists())
        self.assertEqual(FixedRouteVehiclePrice.objects.filter(route=route).count(), 1)

    def test_cannot_delete_a_vehicle_still_priced_for_a_tour(self):
        from django.db.models import ProtectedError

        tour = Tour.objects.create(site="transfer247", slug="protect-tour", title_pl="T", title_en="T")
        TourVehiclePrice.objects.create(tour=tour, vehicle=self.vehicle, price=100)
        with self.assertRaises(ProtectedError):
            self.vehicle.delete()
        self.assertEqual(TourVehiclePrice.objects.filter(tour=tour).count(), 1)

    def test_cannot_delete_a_vehicle_with_gallery_photos(self):
        from django.db.models import ProtectedError

        from apps.fleet.models import VehiclePhoto

        VehiclePhoto.objects.create(vehicle=self.vehicle, image=_make_test_image_upload())
        with self.assertRaises(ProtectedError):
            self.vehicle.delete()
        self.assertEqual(VehiclePhoto.objects.filter(vehicle=self.vehicle).count(), 1)

    def test_an_unreferenced_vehicle_can_still_be_deleted(self):
        self.vehicle.delete()
        self.assertFalse(Vehicle.objects.filter(id=self.vehicle.id).exists())


class MarkdownTranslationCheckTests(TestCase):
    """An EN/DE body pasted from the rendered page (no ## headings) must be
    flagged in Admin, or that language's page silently loses its H2s, FAQ
    and links again."""

    def _warnings_on_save(self, **bodies):
        from unittest import mock

        from django.contrib.admin.sites import site

        from .admin import FixedRouteAdmin

        route = FixedRoute(slug="check-route", name_pl="Trasa", name_en="Route", **bodies)
        model_admin = FixedRouteAdmin(FixedRoute, site)
        with mock.patch.object(model_admin, "message_user") as message_user:
            model_admin.save_model(request=None, obj=route, form=None, change=False)
        return [call.args[1] for call in message_user.call_args_list]

    def test_plain_text_translation_of_a_markdown_body_is_flagged(self):
        warnings = self._warnings_on_save(
            body_pl="Wstęp\n\n## Cena\n\nTekst", body_en="Intro\n\nPrice\n\nText", body_de="Intro\n\n## Preis\n\nText",
        )
        self.assertEqual(len(warnings), 1)
        self.assertIn("EN", warnings[0])

    def test_markdown_translations_and_empty_fields_pass(self):
        warnings = self._warnings_on_save(body_pl="Wstęp\n\n## Cena", body_en="Intro\n\n## Price", body_de="")
        self.assertEqual(warnings, [])


class FrontendRevalidationTests(TestCase):
    """Content edits revalidate the cache of the right brand's frontend:
    one request per brand per transaction, after commit, with the secret."""

    def _sent_on_commit(self, change):
        from unittest import mock

        from django.db import transaction

        from . import revalidation

        sent = []
        timers = []

        class ManualTimer:  # fired by hand below instead of after a delay
            def __init__(self, delay, function):
                self.function = function
                timers.append(self)

            def start(self):
                pass

        with mock.patch.object(revalidation.threading, "Timer", ManualTimer), \
                mock.patch.object(revalidation, "send", side_effect=lambda site, tags: sent.append((site, tags))):
            with self.captureOnCommitCallbacks(execute=True):
                with transaction.atomic():
                    change()
                self.assertEqual(timers, [], "nothing may be queued before the transaction commits")
            self.assertEqual(len(timers), 1, "one flush per batch of committed changes")
            timers[0].function()
        return sent

    def test_route_and_its_inline_rows_send_one_request_to_their_brand_only(self):
        vehicle = Vehicle.objects.create(name="Volkswagen", plate="RV1", seats=6)

        def change():
            route = FixedRoute.objects.create(site="transfer247", slug="rv-route", name_pl="R", name_en="R")
            FixedRouteVehiclePrice.objects.create(route=route, vehicle=vehicle, price=100)

        self.assertEqual(self._sent_on_commit(change), [("transfer247", ["fixed-routes"])])

    def test_a_shared_vehicle_revalidates_both_brands_and_the_pages_embedding_it(self):
        sent = self._sent_on_commit(lambda: Vehicle.objects.create(name="Bus", plate="RV2", seats=8))
        self.assertEqual(
            sent,
            [("dowieziemycie", ["fixed-routes", "fleet", "tours"]), ("transfer247", ["fixed-routes", "fleet", "tours"])],
        )

    @override_settings(FRONTEND_REVALIDATE_URLS={"transfer247": "http://frontend/api/revalidate"}, REVALIDATE_SECRET="s3cret")
    def test_send_posts_the_tags_with_the_secret(self):
        from unittest import mock

        from .revalidation import send

        response = mock.MagicMock(status=200)
        response.__enter__.return_value = response
        with mock.patch("urllib.request.urlopen", return_value=response) as urlopen:
            self.assertTrue(send("transfer247", ["blog", "tours"]))
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://frontend/api/revalidate")
        self.assertEqual(request.get_header("Authorization"), "Bearer s3cret")
        self.assertEqual(request.data, b'{"tags": ["blog", "tours"]}')

    @override_settings(FRONTEND_REVALIDATE_URLS={"transfer247": ""}, REVALIDATE_SECRET="")
    def test_send_is_a_no_op_when_not_configured(self):
        from unittest import mock

        from .revalidation import send

        with mock.patch("urllib.request.urlopen") as urlopen:
            self.assertFalse(send("transfer247", ["blog"]))
        urlopen.assert_not_called()
