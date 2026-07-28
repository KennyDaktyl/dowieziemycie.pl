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

from .models import PricingTier
from .routing import get_route_distance_km


@dataclass
class PriceEstimate:
    distance_km: float
    is_reserved: bool
    price: Decimal | None
    tier: PricingTier | None


def estimate_price(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, scheduled_at) -> PriceEstimate:
    distance_km = get_route_distance_km(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
    lead_time = scheduled_at - timezone.now()
    is_reserved = lead_time >= timedelta(hours=settings.ADVANCE_BOOKING_THRESHOLD_HOURS)

    tier = PricingTier.find_matching(distance_km)
    price = None
    if tier:
        price = tier.price_reserved if is_reserved else tier.price_on_demand

    return PriceEstimate(distance_km=distance_km, is_reserved=is_reserved, price=price, tier=tier)
