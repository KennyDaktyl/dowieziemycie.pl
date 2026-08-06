"""Single source of truth for turning (pickup, dropoff, when) into a price.

Used by both `GET /api/route-estimate/` (live preview while filling the
booking form) and `POST /api/bookings/` (the authoritative charge) so the
number a customer sees before booking always matches what they're charged.
"""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from .models import LocalFarePolicy, PricingTier
from .routing import get_route_distance_km


@dataclass
class PriceEstimate:
    distance_km: float
    is_reserved: bool
    price: Decimal | None
    tier: PricingTier | None
    pricing_mode: str  # "local" | "tier"


def _local_fare_price(distance_km, pickup_lat, pickup_lng):
    """If a free (or soon-to-be-free) driver is already close to the pickup
    point AND the route itself is still short, price the trip like a local
    taxi run instead of looking up the Kraków-corridor tier table — see
    LocalFarePolicy's docstring."""
    policy = LocalFarePolicy.objects.filter(is_active=True).first()
    if not policy:
        return None

    if distance_km > policy.local_max_distance_km:
        return None

    # Imported here, not at module level — apps.fleet.dispatch imports
    # apps.bookings.models, so importing it back at module load time would
    # be a real circular import; safe once both apps are fully loaded.
    from apps.fleet.dispatch import nearest_driver_distance_km

    driver_distance_km = nearest_driver_distance_km(pickup_lat, pickup_lng)
    if driver_distance_km is None or driver_distance_km > float(policy.proximity_threshold_km):
        return None

    distance = Decimal(str(distance_km))
    if distance <= policy.included_km:
        return policy.minimum_fare
    return policy.minimum_fare + (distance - policy.included_km) * policy.price_per_km


def estimate_price(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, scheduled_at, distance_km=None) -> PriceEstimate:
    """`distance_km` can be passed in by callers that already fetched the route
    (e.g. the route-estimate endpoint, which also wants duration/geometry) to
    avoid a second OSRM round-trip for the same pair of points."""
    if distance_km is None:
        distance_km = get_route_distance_km(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
    lead_time = scheduled_at - timezone.now()
    is_reserved = lead_time >= timedelta(hours=settings.ADVANCE_BOOKING_THRESHOLD_HOURS)

    local_price = _local_fare_price(distance_km, pickup_lat, pickup_lng)
    if local_price is not None:
        return PriceEstimate(
            distance_km=distance_km, is_reserved=is_reserved, price=local_price, tier=None, pricing_mode="local",
        )

    tier = PricingTier.find_matching(distance_km)
    price = None
    if tier:
        price = tier.price_reserved if is_reserved else tier.price_on_demand

    return PriceEstimate(distance_km=distance_km, is_reserved=is_reserved, price=price, tier=tier, pricing_mode="tier")
