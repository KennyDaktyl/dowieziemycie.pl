from django.contrib import admin

from .models import (
    BlogPost,
    BlogPostLink,
    BlogPostPhoto,
    ContactInfo,
    ContentPage,
    EventOffer,
    EventOfferPhoto,
    FixedRoute,
    FixedRoutePhoto,
    FixedRouteVehiclePrice,
    HomeContent,
    LocalRoute,
    SiteShowcasePhoto,
    Tour,
    TourPhoto,
    TourVehiclePrice,
)


@admin.register(HomeContent)
class HomeContentAdmin(admin.ModelAdmin):
    """One row per site (config.sites.SITE_CHOICES) — `site` has a unique
    constraint, so the admin form itself blocks a second row for the same
    site rather than needing a custom singleton guard here."""

    list_display = ("site", "headline_pl")
    fieldsets = (
        (None, {"fields": ("site",)}),
        (
            "Polski",
            {"fields": ("eyebrow_pl", "headline_pl", "headline_highlight_pl", "lead_pl", "footnote_pl", "about_pl")},
        ),
        (
            "English",
            {"fields": ("eyebrow_en", "headline_en", "headline_highlight_en", "lead_en", "footnote_en", "about_en")},
        ),
        (
            "Deutsch",
            {"fields": ("eyebrow_de", "headline_de", "headline_highlight_de", "lead_de", "footnote_de", "about_de")},
        ),
    )


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """One row per site — `site` has a unique constraint, so the admin form
    itself blocks a second row for the same site. Edit this instead of
    hunting for hardcoded phone numbers/emails in frontend code — the
    header, footer, WhatsApp button and JSON-LD on both sites all read from
    here."""

    list_display = ("site", "phone_display", "email")
    fieldsets = (
        (None, {"fields": ("site", "phone", "phone_display", "email")}),
        (
            "Firma (stopka, JSON-LD)",
            {"fields": ("legal_name", "nip", "address_street", "address_postal_code", "address_city", "address_country")},
        ),
    )


@admin.register(SiteShowcasePhoto)
class SiteShowcasePhotoAdmin(admin.ModelAdmin):
    """Homepage photos per site and category — Kierowca (zwykle jedno
    zdjęcie), Samochód (dowolna liczba), Z wycieczek / Aktualności (rosnący
    z czasem feed). Upload jest automatycznie kompresowany do WebP i
    skalowany (patrz common/imaging.py) — nie trzeba samodzielnie
    optymalizować zdjęć przed wgraniem."""

    list_display = ("site", "category", "order", "is_published", "thumb_preview", "created_at")
    list_filter = ("site", "category", "is_published")
    ordering = ("site", "category", "order", "-created_at")
    fields = ("site", "category", "image", "thumb_preview", "caption_pl", "caption_en", "caption_de", "order", "is_published")
    readonly_fields = ("thumb_preview",)

    @admin.display(description="Podgląd")
    def thumb_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


class TourVehiclePriceInline(admin.TabularInline):
    """One row per real vehicle from Flota → Pojazdy — add/remove a vehicle
    there and its price row appears/disappears here, instead of a fixed
    pair of price fields that assumed there'd always be exactly two."""

    model = TourVehiclePrice
    extra = 1
    autocomplete_fields = ("vehicle",)
    fields = ("vehicle", "price", "price_eur")


class TourPhotoInline(admin.TabularInline):
    model = TourPhoto
    extra = 1
    fields = ("image", "thumbnail_preview", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    @admin.display(description="Podgląd")
    def thumbnail_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "site", "is_published", "order")
    list_editable = ("is_published", "order")
    list_filter = ("site", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "summary_pl", "summary_en")
    inlines = [TourVehiclePriceInline, TourPhotoInline]
    fieldsets = (
        (None, {"fields": (
            "site", "slug", "duration", "duration_minutes", "cover_image", "is_published", "order",
        )}),
        (
            "Polski",
            {"fields": ("title_pl", "h1_pl", "summary_pl", "body_pl", "seo_title_pl", "seo_description_pl")},
        ),
        (
            "English",
            {"fields": ("title_en", "h1_en", "summary_en", "body_en", "seo_title_en", "seo_description_en")},
        ),
        (
            "Deutsch",
            {"fields": ("title_de", "h1_de", "summary_de", "body_de", "seo_title_de", "seo_description_de")},
        ),
    )


@admin.register(LocalRoute)
class LocalRouteAdmin(admin.ModelAdmin):
    list_display = ("destination_town", "title_pl", "price_from", "show_on_homepage", "is_published", "order")
    list_editable = ("price_from", "show_on_homepage", "is_published", "order")
    list_filter = ("show_on_homepage", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("destination_town", "title_pl", "title_en", "slug")
    fieldsets = (
        (None, {"fields": (
            "slug", "destination_town", "destination_lat", "destination_lng",
            "price_from", "show_on_homepage", "is_published", "order",
        )}),
        ("Polski", {"fields": ("title_pl", "lead_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("title_en", "lead_en", "body_en", "seo_title_en", "seo_description_en")}),
    )


class FixedRouteVehiclePriceInline(admin.TabularInline):
    model = FixedRouteVehiclePrice
    extra = 1
    autocomplete_fields = ("vehicle",)
    fields = ("vehicle", "price", "price_eur")


class FixedRoutePhotoInline(admin.TabularInline):
    model = FixedRoutePhoto
    extra = 1
    fields = ("image", "thumbnail_preview", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    @admin.display(description="Podgląd")
    def thumbnail_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)



ROUTE_PINS_MAP_HTML = r"""
<div id="rp-root" style="max-width:860px">
  <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:8px">
    <button type="button" class="button" id="rp-mode-pickup" style="font-weight:600">A · Ustaw START</button>
    <button type="button" class="button" id="rp-mode-dropoff" style="font-weight:600">B · Ustaw CEL</button>
    <button type="button" class="button" id="rp-clear-pickup">Usuń start</button>
    <button type="button" class="button" id="rp-clear-dropoff">Usuń cel</button>
    <input type="text" id="rp-search" placeholder="Szukaj adresu i naciśnij Enter" style="min-width:260px;flex:1">
  </div>
  <div id="rp-status" style="margin-bottom:6px;font-size:13px;color:#555"></div>
  <div id="rp-map" style="height:440px;border:1px solid #ccc;border-radius:6px"></div>
  <p class="help" style="margin-left:0">
    Wybierz „Ustaw START” lub „Ustaw CEL”, potem kliknij na mapie (lub wyszukaj adres). Pinezki można przeciągać. Adres pod pinezką uzupełnia się sam — możesz go potem poprawić (np. dopisać numer domu).
    Klient zobaczy tę trasę w formularzu od razu i może każdy punkt zmienić na dokładny adres.
    Pola opcjonalne — bez pinezek formularz jest pusty jak dotąd.
  </p>
</div>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
(function () {
  function init() {
    if (!window.L) { document.getElementById("rp-status").textContent = "Nie udało się załadować mapy (Leaflet)."; return; }
    var NOISE = /^(gmina|powiat|województwo|Polska)\b|Metropolia/i;
    var COLORS = { pickup: "#1a7f37", dropoff: "#c1552c" };
    var LETTER = { pickup: "A", dropoff: "B" };
    var ids = {
      pickup: { lat: "id_default_pickup_lat", lng: "id_default_pickup_lng", label: "id_default_pickup_label" },
      dropoff: { lat: "id_default_dropoff_lat", lng: "id_default_dropoff_lng", label: "id_default_dropoff_label" }
    };
    var el = function (id) { return document.getElementById(id); };
    var status = el("rp-status");
    var markers = {};
    var mode = "pickup";

    var map = L.map("rp-map").setView([50.06, 19.94], 9);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "&copy; OpenStreetMap",
      // Django's default Referrer-Policy is same-origin, so no Referer would reach
      // OSM — and tile.openstreetmap.org answers 403 "Access blocked" without one.
      referrerPolicy: "strict-origin-when-cross-origin"
    }).addTo(map);

    function icon(kind) {
      return L.divIcon({
        className: "",
        html: '<div style="width:30px;height:30px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);background:' +
          COLORS[kind] + ';border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.5)"><span style="display:block;transform:rotate(45deg);' +
          'color:#fff;font:700 14px/26px sans-serif;text-align:center">' + LETTER[kind] + "</span></div>",
        iconSize: [30, 30], iconAnchor: [4, 30]
      });
    }
    function r6(n) { return Math.round(n * 1e6) / 1e6; }
    function setMode(m) {
      mode = m;
      el("rp-mode-pickup").style.outline = m === "pickup" ? "3px solid " + COLORS.pickup : "none";
      el("rp-mode-dropoff").style.outline = m === "dropoff" ? "3px solid " + COLORS.dropoff : "none";
      status.textContent = "Kliknij na mapie, aby ustawić " + (m === "pickup" ? "START (A)" : "CEL (B)") + ".";
    }
    function shorten(label) {
      return label.split(", ").filter(function (p) { return !NOISE.test(p); }).join(", ").slice(0, 190);
    }
    function reverse(kind, lat, lng) {
      fetch("https://nominatim.openstreetmap.org/reverse?format=json&zoom=18&lat=" + lat + "&lon=" + lng,
        { headers: { Accept: "application/json" } })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          // Always refresh: a pin that moved makes the old address wrong.
          // The admin can still edit the text afterwards (e.g. add a house number).
          if (d && d.display_name) el(ids[kind].label).value = shorten(d.display_name);
        })
        .catch(function () {});
    }
    function place(kind, lat, lng, geocode) {
      lat = r6(lat); lng = r6(lng);
      el(ids[kind].lat).value = lat.toFixed(6);
      el(ids[kind].lng).value = lng.toFixed(6);
      if (markers[kind]) { markers[kind].setLatLng([lat, lng]); }
      else {
        markers[kind] = L.marker([lat, lng], { draggable: true, icon: icon(kind) }).addTo(map);
        markers[kind].on("dragend", function () {
          var p = markers[kind].getLatLng();
          place(kind, p.lat, p.lng, true);
        });
      }
      if (geocode) reverse(kind, lat, lng);
    }
    function clearPoint(kind) {
      el(ids[kind].lat).value = ""; el(ids[kind].lng).value = "";
      el(ids[kind].label).value = "";
      if (markers[kind]) { map.removeLayer(markers[kind]); delete markers[kind]; }
    }
    function fit() {
      var pts = Object.keys(markers).map(function (k) { return markers[k].getLatLng(); });
      if (pts.length === 1) map.setView(pts[0], 14);
      else if (pts.length > 1) map.fitBounds(L.latLngBounds(pts), { padding: [40, 40] });
    }

    map.on("click", function (e) {
      place(mode, e.latlng.lat, e.latlng.lng, true);
      if (mode === "pickup" && !markers.dropoff) setMode("dropoff");
    });
    el("rp-mode-pickup").onclick = function () { setMode("pickup"); };
    el("rp-mode-dropoff").onclick = function () { setMode("dropoff"); };
    el("rp-clear-pickup").onclick = function () { clearPoint("pickup"); setMode("pickup"); };
    el("rp-clear-dropoff").onclick = function () { clearPoint("dropoff"); setMode("dropoff"); };

    ["pickup", "dropoff"].forEach(function (kind) {
      [ids[kind].lat, ids[kind].lng].forEach(function (id) {
        el(id).addEventListener("change", function () {
          var la = parseFloat(el(ids[kind].lat).value), ln = parseFloat(el(ids[kind].lng).value);
          if (!isNaN(la) && !isNaN(ln)) { place(kind, la, ln, false); fit(); }
        });
      });
      var la = parseFloat(el(ids[kind].lat).value), ln = parseFloat(el(ids[kind].lng).value);
      if (!isNaN(la) && !isNaN(ln)) place(kind, la, ln, false);
    });
    if (markers.pickup && !markers.dropoff) setMode("dropoff"); else setMode("pickup");
    fit();

    el("rp-search").addEventListener("keydown", function (e) {
      if (e.key !== "Enter") return;
      e.preventDefault();
      var q = this.value.trim();
      if (q.length < 3) return;
      status.textContent = "Szukam…";
      fetch("https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=pl&q=" + encodeURIComponent(q),
        { headers: { Accept: "application/json" } })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (!res.length) { status.textContent = "Nie znaleziono adresu."; return; }
          var lat = parseFloat(res[0].lat), lng = parseFloat(res[0].lon);
          map.setView([lat, lng], 16);
          place(mode, lat, lng, false);
          el(ids[mode].label).value = shorten(res[0].display_name);
          if (mode === "pickup" && !markers.dropoff) setMode("dropoff"); else setMode(mode);
        })
        .catch(function () { status.textContent = "Błąd wyszukiwania."; });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
</script>
"""

@admin.register(FixedRoute)
class FixedRouteAdmin(admin.ModelAdmin):
    list_display = ("name_pl", "category", "duration", "is_published", "order")
    list_editable = ("is_published", "order")
    list_filter = ("category", "is_published")
    prepopulated_fields = {"slug": ("name_pl",)}
    search_fields = ("name_pl", "name_en", "slug")
    inlines = [FixedRouteVehiclePriceInline, FixedRoutePhotoInline]
    readonly_fields = ("route_pins_map",)

    @admin.display(description="Mapa")
    def route_pins_map(self, obj):
        from django.utils.safestring import mark_safe

        return mark_safe(ROUTE_PINS_MAP_HTML)

    fieldsets = (
        (None, {"fields": (
            "site", "category", "slug", "duration", "duration_minutes", "is_published", "order",
        )}),
        ("Domyślny start i cel kursu (opcjonalnie) — wskaż pinezką na mapie", {"fields": (
            "route_pins_map",
            "default_pickup_label", "default_pickup_lat", "default_pickup_lng",
            "default_dropoff_label", "default_dropoff_lat", "default_dropoff_lng",
        )}),
        ("Polski", {"fields": ("name_pl", "h1_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("name_en", "h1_en", "body_en", "seo_title_en", "seo_description_en")}),
        ("Deutsch", {"fields": ("name_de", "h1_de", "body_de", "seo_title_de", "seo_description_de")}),
    )


class BlogPostPhotoInline(admin.TabularInline):
    model = BlogPostPhoto
    extra = 1
    fields = ("image", "thumbnail_preview", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    @admin.display(description="Podgląd")
    def thumbnail_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


class BlogPostLinkInline(admin.TabularInline):
    model = BlogPostLink
    extra = 1
    fields = ("label_pl", "label_en", "label_de", "url", "order")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "site", "tag_pl", "published_at", "is_published")
    list_editable = ("is_published",)
    list_filter = ("site", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "excerpt_pl", "excerpt_en", "slug")
    inlines = [BlogPostPhotoInline, BlogPostLinkInline]
    fieldsets = (
        (None, {"fields": ("site", "slug", "cover_image", "youtube_url", "published_at", "is_published")}),
        (
            "Polski",
            {"fields": ("tag_pl", "title_pl", "excerpt_pl", "body_pl", "seo_title_pl", "seo_description_pl")},
        ),
        (
            "English",
            {"fields": ("tag_en", "title_en", "excerpt_en", "body_en", "seo_title_en", "seo_description_en")},
        ),
        (
            "Deutsch",
            {"fields": ("tag_de", "title_de", "excerpt_de", "body_de", "seo_title_de", "seo_description_de")},
        ),
    )


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "title_en", "site", "page_type", "slug", "is_published")
    list_filter = ("site", "page_type", "is_published")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "slug")
    fieldsets = (
        (None, {"fields": ("site", "slug", "page_type", "is_published")}),
        ("Polski", {"fields": ("title_pl", "body_pl", "seo_title_pl", "seo_description_pl")}),
        ("English", {"fields": ("title_en", "body_en", "seo_title_en", "seo_description_en")}),
    )


class EventOfferPhotoInline(admin.TabularInline):
    model = EventOfferPhoto
    extra = 1
    fields = ("image", "thumbnail_preview", "caption", "order")
    readonly_fields = ("thumbnail_preview",)

    @admin.display(description="Podgląd")
    def thumbnail_preview(self, obj):
        if not obj.thumbnail:
            return "—"
        from django.utils.html import format_html

        return format_html('<img src="{}" style="height:60px;border-radius:6px" />', obj.thumbnail.url)


@admin.register(EventOffer)
class EventOfferAdmin(admin.ModelAdmin):
    list_display = ("title_pl", "slug", "site", "price_from", "show_on_homepage", "order", "is_published")
    list_editable = ("price_from", "show_on_homepage", "order", "is_published")
    list_filter = ("site", "show_on_homepage", "is_published")
    prepopulated_fields = {"slug": ("title_pl",)}
    search_fields = ("title_pl", "title_en", "excerpt_pl", "excerpt_en", "slug")
    inlines = [EventOfferPhotoInline]
    fieldsets = (
        (None, {
            "fields": (
                "site", "slug", "order", "icon", "cover_image", "price_from", "show_on_homepage", "is_published",
            ),
        }),
        (
            "Polski",
            {"fields": ("title_pl", "h1_pl", "excerpt_pl", "body_pl", "seo_title_pl", "seo_description_pl")},
        ),
        (
            "English",
            {"fields": ("title_en", "h1_en", "excerpt_en", "body_en", "seo_title_en", "seo_description_en")},
        ),
    )
