from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.schemas import WorkerCreate, WorkerUpdate
from app.services.location_service import LocationService


class WorkerService:
    @staticmethod
    def create_worker(worker: WorkerCreate) -> Dict[str, Any]:
        lat = worker.latitude
        lon = worker.longitude

        # Resolve coordinates if not provided
        if lat is None or lon is None or (lat == 0 and lon == 0):
            resolved_lat, resolved_lon, _ = LocationService.resolve_city_coords(worker.city)
            lat = resolved_lat
            lon = resolved_lon

        # Auto-compute fair wage if daily_rate is not provided
        daily = worker.daily_rate
        if daily is None or daily <= 0:
            from app.services.wage_service import FairWageService
            pred = FairWageService.predict_fair_wage(worker.trade, worker.city, worker.experience_years)
            daily = float(pred.get("recommended_daily_wage", 750.0))

        hourly = worker.hourly_rate
        if hourly is None:
            hourly = round(daily / 8.0, 1)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workers (
                    name, phone, trade, secondary_skills, experience_years, daily_rate, hourly_rate,
                    city, area, latitude, longitude, availability, language_pref, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                worker.name, worker.phone, worker.trade, worker.secondary_skills,
                worker.experience_years, daily, hourly,
                worker.city, worker.area or worker.city, lat, lon,
                worker.availability, worker.language_pref, worker.source
            ))
            worker_id = cursor.lastrowid

            cursor.execute("SELECT * FROM workers WHERE id = ?", (worker_id,))
            return cursor.fetchone()

    @staticmethod
    def get_worker(worker_id: int) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workers WHERE id = ?", (worker_id,))
            return cursor.fetchone()

    @staticmethod
    def get_worker_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workers WHERE phone = ?", (phone.strip(),))
            return cursor.fetchone()

    @staticmethod
    def list_workers(
        trade: Optional[str] = None,
        city: Optional[str] = None,
        availability: Optional[str] = None,
        max_daily_rate: Optional[float] = None,
        min_experience: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM workers WHERE 1=1"
        params = []

        if trade:
            query += " AND LOWER(trade) LIKE LOWER(?)"
            params.append(f"%{trade.strip()}%")

        if city:
            query += " AND LOWER(city) LIKE LOWER(?)"
            params.append(f"%{city.strip()}%")

        if availability:
            query += " AND availability = ?"
            params.append(availability.strip())

        if max_daily_rate:
            query += " AND daily_rate <= ?"
            params.append(max_daily_rate)

        if min_experience:
            query += " AND experience_years >= ?"
            params.append(min_experience)

        query += " ORDER BY rating DESC, jobs_completed DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def update_worker(worker_id: int, updates: WorkerUpdate) -> Optional[Dict[str, Any]]:
        fields = []
        values = []
        for key, val in updates.model_dump(exclude_unset=True).items():
            if val is not None:
                fields.append(f"{key} = ?")
                values.append(val)

        if not fields:
            return WorkerService.get_worker(worker_id)

        values.append(worker_id)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE workers SET {', '.join(fields)} WHERE id = ?", values)
            cursor.execute("SELECT * FROM workers WHERE id = ?", (worker_id,))
            return cursor.fetchone()

    @staticmethod
    def set_worker_availability(worker_id: int, availability: str) -> Optional[Dict[str, Any]]:
        """
        Directly update worker availability between 'available' and 'busy'.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE workers SET availability = ? WHERE id = ?", (availability.strip(), worker_id))
            if cursor.rowcount == 0:
                return None
            cursor.execute("SELECT * FROM workers WHERE id = ?", (worker_id,))
            return cursor.fetchone()
