from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query
from app.services.feed_service import FeedService

router = APIRouter(prefix="/api/v1/feeds", tags=["Feeds & Insights Microservice"])


@router.get("/jobs")
def get_job_feed(
    lat: Optional[float] = Query(None, description="User latitude"),
    lon: Optional[float] = Query(None, description="User longitude"),
    city: Optional[str] = Query(None, description="User city name"),
    trade: Optional[str] = Query(None, description="Trade filter"),
    urgency: Optional[str] = Query(None, description="Filter urgent postings"),
    max_distance_km: Optional[float] = Query(None, description="Filter within km radius"),
    limit: int = Query(30, ge=1, le=100)
):
    """
    Personalized job feed for workers with proximity distance and urgency sorting.
    """
    return FeedService.get_job_feed(
        user_lat=lat,
        user_lon=lon,
        city=city,
        trade=trade,
        urgency=urgency,
        max_distance_km=max_distance_km,
        limit=limit
    )


@router.get("/workers")
def get_worker_feed(
    lat: Optional[float] = Query(None, description="Employer latitude"),
    lon: Optional[float] = Query(None, description="Employer longitude"),
    city: Optional[str] = Query(None, description="Employer city name"),
    trade: Optional[str] = Query(None, description="Trade filter"),
    availability: Optional[str] = Query(None, description="Filter: available, busy"),
    max_daily_rate: Optional[float] = Query(None, description="Max daily rate"),
    max_distance_km: Optional[float] = Query(None, description="Filter within km radius"),
    limit: int = Query(30, ge=1, le=100)
):
    """
    Curated worker feed for employers to browse nearby rated talent.
    """
    return FeedService.get_worker_feed(
        employer_lat=lat,
        employer_lon=lon,
        city=city,
        trade=trade,
        availability=availability,
        max_daily_rate=max_daily_rate,
        max_distance_km=max_distance_km,
        limit=limit
    )


@router.get("/insights")
def get_insights():
    """
    Marketplace metrics: active workers, open jobs, top trades, and city breakdowns.
    """
    return FeedService.get_platform_insights()
