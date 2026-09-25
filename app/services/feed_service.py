from typing import List, Dict, Any, Optional
from app.services.location_service import LocationService
from app.services.job_service import JobService
from app.services.worker_service import WorkerService
from app.database import get_db


class FeedService:
    @staticmethod
    def get_job_feed(
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        city: Optional[str] = None,
        trade: Optional[str] = None,
        urgency: Optional[str] = None,
        max_distance_km: Optional[float] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Curated job feed for workers seeking nearby opportunities.
        """
        # Resolve user coordinate if only city is given
        if (user_lat is None or user_lon is None) and city:
            lat, lon, _ = LocationService.resolve_city_coords(city)
            user_lat = lat
            user_lon = lon

        jobs = JobService.list_jobs(
            trade=trade,
            city=city if not (user_lat and user_lon) else None,
            status="open",
            urgency=urgency,
            limit=100
        )

        feed_items = []
        for j in jobs:
            item = dict(j)
            dist_km = None
            if user_lat is not None and user_lon is not None:
                dist_km = LocationService.haversine_distance(
                    user_lat, user_lon, j["latitude"], j["longitude"]
                )
                if max_distance_km and dist_km > max_distance_km:
                    continue
            item["distance_km"] = dist_km
            feed_items.append(item)

        # Sort: urgent jobs first, then by closest distance if coords provided, else recent
        if user_lat is not None and user_lon is not None:
            feed_items.sort(key=lambda x: (
                0 if x["urgency"] == "urgent" else 1,
                x["distance_km"] if x["distance_km"] is not None else 9999
            ))
        else:
            feed_items.sort(key=lambda x: (
                0 if x["urgency"] == "urgent" else 1,
                x["created_at"]
            ), reverse=True)

        return feed_items[:limit]

    @staticmethod
    def get_worker_feed(
        employer_lat: Optional[float] = None,
        employer_lon: Optional[float] = None,
        city: Optional[str] = None,
        trade: Optional[str] = None,
        max_daily_rate: Optional[float] = None,
        max_distance_km: Optional[float] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Curated workers feed for employers seeking talent.
        """
        if (employer_lat is None or employer_lon is None) and city:
            lat, lon, _ = LocationService.resolve_city_coords(city)
            employer_lat = lat
            employer_lon = lon

        workers = WorkerService.list_workers(
            trade=trade,
            city=city if not (employer_lat and employer_lon) else None,
            availability="available",
            max_daily_rate=max_daily_rate,
            limit=100
        )

        feed_items = []
        for w in workers:
            item = dict(w)
            dist_km = None
            if employer_lat is not None and employer_lon is not None:
                dist_km = LocationService.haversine_distance(
                    employer_lat, employer_lon, w["latitude"], w["longitude"]
                )
                if max_distance_km and dist_km > max_distance_km:
                    continue
            item["distance_km"] = dist_km
            feed_items.append(item)

        if employer_lat is not None and employer_lon is not None:
            feed_items.sort(key=lambda x: (
                x["distance_km"] if x["distance_km"] is not None else 9999,
                -x["rating"]
            ))
        else:
            feed_items.sort(key=lambda x: (-x["rating"], -x["jobs_completed"]))

        return feed_items[:limit]

    @staticmethod
    def get_platform_insights() -> Dict[str, Any]:
        """
        Real-time statistical overview of the platform.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as c FROM workers")
            total_workers = cursor.fetchone()["c"]

            cursor.execute("SELECT COUNT(*) as c FROM jobs WHERE status = 'open'")
            open_jobs = cursor.fetchone()["c"]

            cursor.execute("SELECT COUNT(*) as c FROM contacts")
            total_contacts = cursor.fetchone()["c"]

            cursor.execute("SELECT trade, COUNT(*) as count, AVG(daily_rate) as avg_rate FROM workers GROUP BY trade ORDER BY count DESC LIMIT 6")
            top_trades = cursor.fetchall()

            cursor.execute("SELECT city, COUNT(*) as count FROM workers GROUP BY city ORDER BY count DESC LIMIT 6")
            top_cities = cursor.fetchall()

            return {
                "total_workers": total_workers,
                "open_jobs": open_jobs,
                "total_contacts": total_contacts,
                "top_trades": top_trades,
                "top_cities": top_cities
            }
