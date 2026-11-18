from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header
from app.models.schemas import WorkerCreate, WorkerUpdate, WorkerResponse
from app.services.worker_service import WorkerService
from app.services.auth_service import AuthService

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
    availability: str = Query(..., description="'available', 'busy', or 'on_call'"),
    authorization: Optional[str] = Header(None),
    worker_phone: Optional[str] = Query(None)
):
    """
    Directly update a worker's status (e.g. mark as busy in work or available again).
    Only the worker themselves can change their own availability. Employers cannot alter worker status.
    """
    if availability not in ("available", "busy", "on_call"):
        raise HTTPException(status_code=400, detail="Invalid availability. Must be 'available', 'busy', or 'on_call'.")

    worker = WorkerService.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker profile not found")

    user = None
    if authorization:
        user = AuthService.get_user_by_token(authorization)

    if user:
        if user.get("role") == "employer":
            raise HTTPException(
                status_code=403,
                detail="Employers cannot manually change worker availability status. Only workers can set their own status."
            )
        if user.get("role") == "worker":
            user_worker_id = user.get("worker_id")
            user_phone = (user.get("phone") or "").strip()
            worker_phone_db = (worker.get("phone") or "").strip()

            is_owner = (user_worker_id == worker_id) or (user_phone and user_phone == worker_phone_db)
            if not is_owner:
                raise HTTPException(
                    status_code=403,
                    detail="Workers can only update their own availability status."
                )
    elif worker_phone and isinstance(worker_phone, str):
        worker_phone_db = (worker.get("phone") or "").strip()
        if worker_phone.strip() != worker_phone_db:
            raise HTTPException(
                status_code=403,
                detail="Workers can only update their own availability status."
            )

    updated = WorkerService.set_worker_availability(worker_id, availability)
    return updated
