from typing import List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from app.services.location_service import LocationService

router = APIRouter(prefix="/api/v1/location", tags=["Location Microservice"])


@router.get("/cities")
def get_supported_cities():
    """
    List of supported hubs and towns across Karnataka and Hindi speaking regions with economic tiers.
    """
    return LocationService.list_supported_cities()


@router.get("/distance")
def calculate_distance(
    lat1: float = Query(..., description="Origin latitude"),
    lon1: float = Query(..., description="Origin longitude"),
    lat2: float = Query(..., description="Destination latitude"),
    lon2: float = Query(..., description="Destination longitude")
):
    """
    Compute geodesic distance between two locations in kilometers.
    """
    dist = LocationService.haversine_distance(lat1, lon1, lat2, lon2)
    return {
        "origin": {"lat": lat1, "lon": lon1},
        "destination": {"lat": lat2, "lon": lon2},
        "distance_km": dist
    }


@router.get("/geocode")
def geocode_city(city: str = Query(..., description="City or district name")):
    """
    Resolve city name to coordinates, state, and tier classification.
    """
    info = LocationService.get_city_info(city)
    if info:
        return info
    lat, lon, tier = LocationService.resolve_city_coords(city)
    return {
        "name": city,
        "lat": lat,
        "lon": lon,
        "tier": tier,
        "is_default_fallback": True
    }
