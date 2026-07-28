"""Straight-line distance helper for matching a free-form address to a pricing zone.

Placeholder for the real routing distance (OSRM, Phase 4) — Haversine is a
reasonable approximation for "is this address close enough to a known flat-rate
town" at the few-kilometer radius we're matching on.
"""

from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))
