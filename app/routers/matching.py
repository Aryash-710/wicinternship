from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import JobMatch, WorkerMatch
from app.services.matching_service import MatchingService
from app.services.worker_service import WorkerService
from app.services.job_service import JobService

router = APIRouter(prefix="/api/v1/match", tags=["Job Matching Microservice"])


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
