"""On-demand cache revalidation of the two Next.js frontends.

Both frontends cache every backend GET for a day, tagged with the API
resource it came from — the first path segment after /api/ (apiFetch in each
frontend's src/lib/api.ts): /api/fixed-routes/x/ -> "fixed-routes",
/api/fleet/vehicles/ -> "fleet". When content changes here, the affected tags
are POSTed to the frontend of the brand the object belongs to, so a page is
re-rendered on its next visit instead of waiting out the day.

One backend serves both brands, so each model says which brand(s) a change
affects: its `site` field, the `site` of its parent (a route's price row or
photo), or both brands for shared data (vehicles, pricing).

All changes of one Admin save (a signal per inline row) are collected and
sent once, after commit, from a background thread — an Admin save never
waits for, or fails because of, a frontend.
"""

import json
import logging
import threading
import urllib.request

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save

from config.sites import VALID_SITE_CODES

logger = logging.getLogger(__name__)

ALL_SITES = None  # marker: the change affects every brand

# Vehicle name/photo/price is embedded in route and tour price tables too.
VEHICLE_TAGS = ("fleet", "fixed-routes", "tours")


def _own_site(obj):
    return obj.site


def _parent_site(attr):
    return lambda obj: getattr(obj, attr).site


def _shared(obj):
    return ALL_SITES


def _registry():
    """(app_label, model_name) -> (tags, site_of). Built lazily so model
    imports don't happen at module import time."""
    return {
        ("content", "HomeContent"): (("home-content",), _own_site),
        ("content", "ContactInfo"): (("contact-info",), _own_site),
        ("content", "SiteShowcasePhoto"): (("showcase-photos",), _own_site),
        ("content", "Tour"): (("tours",), _own_site),
        ("content", "TourVehiclePrice"): (("tours",), _parent_site("tour")),
        ("content", "TourPhoto"): (("tours",), _parent_site("tour")),
        ("content", "LocalRoute"): (("routes",), _shared),
        ("content", "FixedRoute"): (("fixed-routes",), _own_site),
        ("content", "FixedRouteVehiclePrice"): (("fixed-routes",), _parent_site("route")),
        ("content", "FixedRoutePhoto"): (("fixed-routes",), _parent_site("route")),
        ("content", "BlogPost"): (("blog",), _own_site),
        ("content", "BlogPostPhoto"): (("blog",), _parent_site("post")),
        ("content", "BlogPostLink"): (("blog",), _parent_site("post")),
        ("content", "ContentPage"): (("content-pages",), _own_site),
        ("content", "EventDriverPricing"): (("event-driver-pricing",), _own_site),
        ("content", "EventOffer"): (("events",), _own_site),
        ("content", "EventOfferPhoto"): (("events",), _parent_site("offer")),
        ("content", "ServicePage"): (("service-pages",), _own_site),
        ("content", "ServicePricingOption"): (("service-pages",), _parent_site("page")),
        ("content", "ServicePagePhoto"): (("service-pages",), _parent_site("page")),
        ("fleet", "Vehicle"): (VEHICLE_TAGS, _shared),
        ("fleet", "VehiclePhoto"): (VEHICLE_TAGS, _shared),
        ("bookings", "PricingTier"): (("pricing-tiers",), _shared),
        ("bookings", "LocalFarePolicy"): (("local-fare-policy",), _shared),
    }


# --- collecting committed changes ---------------------------------------------

# A change only joins the batch once its transaction commits (on_commit drops
# it on rollback). The first one starts a short timer; by the time it fires,
# every row of the same Admin save (all committed together) is in the batch,
# so it's one request per brand, sent off the request thread.
FLUSH_DELAY_SECONDS = 0.5

_lock = threading.Lock()
_batch = {}
_timer = None


def _committed(sites, tags):
    global _timer
    with _lock:
        for site in sites:
            _batch.setdefault(site, set()).update(tags)
        if _timer is None:
            _timer = threading.Timer(FLUSH_DELAY_SECONDS, _flush)
            _timer.daemon = True
            _timer.start()


def _flush():
    global _timer
    with _lock:
        batch = {site: sorted(tags) for site, tags in _batch.items()}
        _batch.clear()
        _timer = None
    for site in sorted(batch):
        send(site, batch[site])


def flush_now():
    """Send whatever is queued right away — for management commands, which
    exit before the flush timer would fire."""
    global _timer
    with _lock:
        if _timer is not None:
            _timer.cancel()
    _flush()


def _on_change(sender, instance, **kwargs):
    if kwargs.get("raw"):  # loaddata — fixtures, not an edit
        return
    tags, site_of = _registry()[(sender._meta.app_label, sender.__name__)]
    try:
        site = site_of(instance)
    except Exception:  # parent already deleted in a cascade, etc.
        site = ALL_SITES
    sites = sorted(VALID_SITE_CODES) if site in (ALL_SITES, "") else [site]
    transaction.on_commit(lambda: _committed(sites, tags))


def connect_signals():
    from django.apps import apps

    for (app_label, model_name) in _registry():
        model = apps.get_model(app_label, model_name)
        uid = f"revalidate-{app_label}-{model_name}"
        post_save.connect(_on_change, sender=model, dispatch_uid=f"{uid}-save")
        post_delete.connect(_on_change, sender=model, dispatch_uid=f"{uid}-delete")


# --- sending ------------------------------------------------------------------


def all_tags():
    """Every tag any model maps to — for a full revalidation after deploy."""
    return sorted({tag for tags, _ in _registry().values() for tag in tags})


def send(site, tags, timeout=5):
    """POST the tags to one brand's frontend. Returns True on success; a
    missing URL/secret (dev, tests) is a silent no-op returning False."""
    url = settings.FRONTEND_REVALIDATE_URLS.get(site, "")
    secret = settings.REVALIDATE_SECRET
    if not url or not secret or not tags:
        return False
    request = urllib.request.Request(
        url,
        data=json.dumps({"tags": list(tags)}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {secret}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            ok = 200 <= response.status < 300
    except Exception as exc:  # a frontend being down must never break the backend
        logger.warning("Revalidation of %s %s failed: %s", site, tags, exc)
        return False
    if ok:
        logger.info("Revalidated %s: %s", site, ", ".join(tags))
    return ok
