"""Route distance lookup — real road distance via OSRM, not straight-line.

Defaults to OSRM's public demo server (OSRM_BASE_URL) — fine for low volume;
swap OSRM_BASE_URL to a self-hosted instance (docker-compose `osrm` service,
already scaffolded) once traffic or reliability calls for it. If OSRM is
unreachable we fall back to a Haversine estimate inflated by a fixed factor
so the site still prices bookings instead of hard-failing.
"""

import logging
from dataclasses import dataclass

import requests
from django.conf import settings

from .geo import haversine_km

logger = logging.getLogger("apps.bookings.routing")

# Rough correction from straight-line to road distance when OSRM is down —
# real roads are never a straight line. Only used as a degraded fallback.
HAVERSINE_ROAD_FACTOR = 1.3
# Assumed average speed for the degraded (no-OSRM) duration estimate.
FALLBACK_AVERAGE_SPEED_KMH = 40


def get_route_distance_km(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng) -> float:
    try:
        url = (
            f"{settings.OSRM_BASE_URL}/route/v1/driving/"
            f"{pickup_lng},{pickup_lat};{dropoff_lng},{dropoff_lat}"
        )
        response = requests.get(url, params={"overview": "false"}, timeout=3)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == "Ok" and data.get("routes"):
            return round(data["routes"][0]["distance"] / 1000, 1)
    except (requests.RequestException, KeyError, ValueError, IndexError):
        logger.warning("OSRM route lookup failed, falling back to Haversine estimate", exc_info=True)

    straight_line = haversine_km(float(pickup_lat), float(pickup_lng), float(dropoff_lat), float(dropoff_lng))
    return round(straight_line * HAVERSINE_ROAD_FACTOR, 1)


@dataclass
class RouteDetails:
    distance_km: float
    duration_min: float
    geometry: list[list[float]]  # [[lat, lng], ...] — Leaflet order, not GeoJSON's [lng, lat]


def get_route_details(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng) -> RouteDetails:
    """Like get_route_distance_km, but also returns duration + the full road-following
    polyline — used where we actually draw/announce the route, not just price it."""
    try:
        url = (
            f"{settings.OSRM_BASE_URL}/route/v1/driving/"
            f"{pickup_lng},{pickup_lat};{dropoff_lng},{dropoff_lat}"
        )
        response = requests.get(
            url, params={"overview": "full", "geometries": "geojson"}, timeout=5
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            coordinates = route["geometry"]["coordinates"]
            return RouteDetails(
                distance_km=round(route["distance"] / 1000, 1),
                duration_min=round(route["duration"] / 60, 1),
                geometry=[[lat, lng] for lng, lat in coordinates],
            )
    except (requests.RequestException, KeyError, ValueError, IndexError):
        logger.warning("OSRM route lookup failed, falling back to Haversine estimate", exc_info=True)

    straight_line = haversine_km(float(pickup_lat), float(pickup_lng), float(dropoff_lat), float(dropoff_lng))
    distance_km = round(straight_line * HAVERSINE_ROAD_FACTOR, 1)
    duration_min = round(distance_km / FALLBACK_AVERAGE_SPEED_KMH * 60, 1)
    return RouteDetails(
        distance_km=distance_km,
        duration_min=duration_min,
        geometry=[[float(pickup_lat), float(pickup_lng)], [float(dropoff_lat), float(dropoff_lng)]],
    )
