from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Header
from app.models.schemas import JobMatch, WorkerMatch
from app.services.matching_service import MatchingService
from app.services.worker_service import WorkerService
from app.services.job_service import JobService
from app.services.auth_service import AuthService
from app.database import get_db

router = APIRouter(prefix="/api/v1/match", tags=["Job Matching Microservice"])


@router.get("/my-queries")
def get_my_matching_queries(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    phone: Optional[str] = Query(None)
):
    """
    Returns ONLY the queries belonging to the logged-in profile:
    - Worker: Returns exclusively their own worker profile.
    - Employer: Returns exclusively the job vacancies posted by this employer.
    """
    user = None
    active_token = authorization or token
    if active_token:
        user = AuthService.get_user_by_token(active_token)

    if not user and phone:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            row = c.fetchone()
            if row:
                user = AuthService._format_user_dict(row)

    if not user:
        raise HTTPException(status_code=401, detail="Please log in to view your personalized matching queries.")

    role = user["role"]
    if role == "worker":
        worker_id = user.get("worker_id")
        worker = WorkerService.get_worker(worker_id) if worker_id else WorkerService.get_worker_by_phone(user["phone"])
        if not worker:
            return {
                "role": "worker",
                "user": user,
                "title": "My Profile",
                "queries": []
            }
        return {
            "role": "worker",
            "user": user,
            "title": f"My Profile: {worker['name']} ({worker['trade']})",
            "queries": [
                {
                    "id": worker["id"],
                    "label": f"{worker['name']} - {worker['trade']} ({worker['city']}, Rate: ₹{worker['daily_rate']:.0f}/day)",
                    "trade": worker["trade"],
                    "city": worker["city"],
                    "daily_rate": worker["daily_rate"]
                }
            ]
        }
    else:
        # Employer queries: jobs posted by this employer
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT * FROM jobs
                WHERE employer_phone = ? OR lower(employer_name) = lower(?)
                ORDER BY created_at DESC
            """, (user["phone"], user["full_name"]))
            jobs = c.fetchall()

        queries = [
            {
                "id": j["id"],
                "label": f"{j['title']} ({j['trade']} - {j.get('area') or j.get('city')}, Offer: ₹{j['wage_offered']:.0f}/day)",
                "trade": j["trade"],
                "city": j["city"],
                "wage_offered": j["wage_offered"],
                "status": j["status"]
            }
            for j in jobs
        ]

        return {
            "role": "employer",
            "user": user,
            "title": f"My Job Postings ({user['full_name']})",
            "queries": queries
        }


@router.get("/my-matches")
def get_my_matches(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    target_id: Optional[int] = Query(None),
    max_radius_km: float = Query(60.0, ge=1.0, le=200.0),
    min_score: float = Query(40.0, ge=0.0, le=100.0),
    limit: int = Query(15, ge=1, le=50)
):
    """
    Executes role-scoped matching:
    - Worker: Finds matching open jobs for this worker.
    - Employer: Finds matching qualified candidates for the selected job belonging to this employer.
    """
    user = None
    active_token = authorization or token
    if active_token:
        user = AuthService.get_user_by_token(active_token)

    if not user and phone:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            row = c.fetchone()
            if row:
                user = AuthService._format_user_dict(row)

    if not user:
        raise HTTPException(status_code=401, detail="Please log in to run your personalized matching.")

    role = user["role"]
    if role == "worker":
        worker_id = user.get("worker_id")
        worker = WorkerService.get_worker(worker_id) if worker_id else WorkerService.get_worker_by_phone(user["phone"])
        if not worker:
            raise HTTPException(status_code=404, detail="Worker profile not found.")
        matches = MatchingService.match_jobs_for_worker(
            worker_id=worker["id"],
            max_radius_km=max_radius_km,
            min_score=min_score,
            limit=limit
        )
        return {
            "mode": "worker_to_jobs",
            "target": worker,
            "matches": matches
        }
    else:
        # Employer matching
        if not target_id:
            # Pick first open job posted by this employer
            with get_db() as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT id FROM jobs
                    WHERE (employer_phone = ? OR lower(employer_name) = lower(?)) AND status = 'open'
                    LIMIT 1
                """, (user["phone"], user["full_name"]))
                first_job = c.fetchone()
                if not first_job:
                    return {
                        "mode": "job_to_workers",
                        "target": None,
                        "matches": [],
                        "message": "You haven't posted any open jobs yet. Please post a job first."
                    }
                target_id = first_job["id"]

        job = JobService.get_job(target_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        matches = MatchingService.match_workers_for_job(
            job_id=target_id,
            max_radius_km=max_radius_km,
            min_score=min_score,
            limit=limit
        )
        return {
            "mode": "job_to_workers",
            "target": job,
            "matches": matches
        }


@router.get("/worker/{worker_id}/jobs", response_model=List[JobMatch])
def match_jobs_for_worker(
    worker_id: int,
    max_radius_km: float = Query(50.0, ge=1.0, le=200.0, description="Max search radius in km"),
    min_score: float = Query(40.0, ge=0.0, le=100.0, description="Minimum composite match score %"),
    limit: int = Query(15, ge=1, le=50)
):
    """
    Intelligent job matching engine: finds and ranks open jobs for a specific worker
    based on skill overlap, distance, wage suitability, and reliability.
    """
    worker = WorkerService.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    matches = MatchingService.match_jobs_for_worker(
        worker_id=worker_id,
        max_radius_km=max_radius_km,
        min_score=min_score,
        limit=limit
    )
    return matches


@router.get("/job/{job_id}/workers", response_model=List[WorkerMatch])
def match_workers_for_job(
    job_id: int,
    max_radius_km: float = Query(50.0, ge=1.0, le=200.0, description="Max search radius in km"),
    min_score: float = Query(40.0, ge=0.0, le=100.0, description="Minimum composite match score %"),
    limit: int = Query(15, ge=1, le=50)
):
    """
    Candidate matching engine: finds and ranks qualified workers for an employer's job
    with explainability breakdown and travel distance.
    """
    job = JobService.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    matches = MatchingService.match_workers_for_job(
        job_id=job_id,
        max_radius_km=max_radius_km,
        min_score=min_score,
        limit=limit
    )
    return matches
