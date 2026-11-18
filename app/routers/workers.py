from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import WorkerCreate, WorkerUpdate, WorkerResponse
from app.services.worker_service import WorkerService

router = APIRouter(prefix="/api/v1/workers", tags=["Workers Microservice"])


@router.post("/", response_model=WorkerResponse, status_code=201)
def register_worker(worker: WorkerCreate):
    """
    Register a new blue-collar worker profile with trade, rate, and location.
    """
    existing = WorkerService.get_worker_by_phone(worker.phone)
    if existing:
        raise HTTPException(status_code=400, detail="Worker with this phone number already registered")
    created = WorkerService.create_worker(worker)
    return created


@router.get("/", response_model=List[WorkerResponse])
def list_workers(
    trade: Optional[str] = Query(None, description="Filter by trade / skill"),
    city: Optional[str] = Query(None, description="Filter by city"),
    availability: Optional[str] = Query(None, description="available, busy, on_call"),
    max_daily_rate: Optional[float] = Query(None, description="Maximum daily rate"),
    min_experience: Optional[int] = Query(None, description="Minimum years of experience"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search and list worker profiles with flexible filters.
    """
    return WorkerService.list_workers(
        trade=trade,
        city=city,
        availability=availability,
        max_daily_rate=max_daily_rate,
        min_experience=min_experience,
        limit=limit,
        offset=offset
    )


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: int):
    """
    Fetch a single worker profile by ID.
    """
    worker = WorkerService.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker profile not found")
    return worker


@router.patch("/{worker_id}", response_model=WorkerResponse)
def update_worker(worker_id: int, updates: WorkerUpdate):
    """
    Update worker profile details (availability, rates, trade, skills).
    """
    updated = WorkerService.update_worker(worker_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Worker profile not found")
    return updated


@router.post("/{worker_id}/status", response_model=WorkerResponse)
def set_worker_status(
    worker_id: int,
    availability: str = Query(..., description="'available', 'busy', or 'on_call'")
):
    """
    Directly update a worker's status (e.g. mark as busy in work or available again).
    """
    if availability not in ("available", "busy", "on_call"):
        raise HTTPException(status_code=400, detail="Invalid availability. Must be 'available', 'busy', or 'on_call'.")

    updated = WorkerService.set_worker_availability(worker_id, availability)
    if not updated:
        raise HTTPException(status_code=404, detail="Worker profile not found")
    return updated
