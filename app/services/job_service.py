from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.schemas import JobCreate, JobUpdate
from app.services.location_service import LocationService


class JobService:
    @staticmethod
    def create_job(job: JobCreate) -> Dict[str, Any]:
        lat = job.latitude
        lon = job.longitude

        if lat is None or lon is None or (lat == 0 and lon == 0):
            resolved_lat, resolved_lon, _ = LocationService.resolve_city_coords(job.city)
            lat = resolved_lat
            lon = resolved_lon

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO jobs (
                    title, trade, description, employer_name, employer_phone,
                    city, area, latitude, longitude, duration_days, wage_offered,
                    payment_type, urgency, workers_needed, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open')
            """, (
                job.title, job.trade, job.description, job.employer_name, job.employer_phone,
                job.city, job.area or job.city, lat, lon, job.duration_days, job.wage_offered,
                job.payment_type, job.urgency, job.workers_needed
            ))
            job_id = cursor.lastrowid
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            return cursor.fetchone()

    @staticmethod
    def get_job(job_id: int) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            return cursor.fetchone()

    @staticmethod
    def list_jobs(
        trade: Optional[str] = None,
        city: Optional[str] = None,
        status: Optional[str] = "open",
        urgency: Optional[str] = None,
        min_wage: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []

        if trade:
            query += " AND LOWER(trade) LIKE LOWER(?)"
            params.append(f"%{trade.strip()}%")

        if city:
            query += " AND LOWER(city) LIKE LOWER(?)"
            params.append(f"%{city.strip()}%")

        if status:
            query += " AND status = ?"
            params.append(status.strip())

        if urgency:
            query += " AND urgency = ?"
            params.append(urgency.strip())

        if min_wage:
            query += " AND wage_offered >= ?"
            params.append(min_wage)

        query += " ORDER BY CASE urgency WHEN 'urgent' THEN 1 ELSE 2 END, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def update_job(job_id: int, updates: JobUpdate) -> Optional[Dict[str, Any]]:
        fields = []
        values = []
        for key, val in updates.model_dump(exclude_unset=True).items():
            if val is not None:
                fields.append(f"{key} = ?")
                values.append(val)

        if not fields:
            return JobService.get_job(job_id)

        values.append(job_id)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?", values)
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            return cursor.fetchone()
