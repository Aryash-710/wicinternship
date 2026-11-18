from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Header
from app.models.schemas import JobCreate, JobUpdate, JobResponse
from app.services.job_service import JobService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs Microservice"])


@router.post("/", response_model=JobResponse, status_code=201)
def post_job(job: JobCreate):
    """
    Employers post work vacancies with trade requirements, location, duration, and wages.
    """
    return JobService.create_job(job)


@router.get("/", response_model=List[JobResponse])
def list_jobs(
    trade: Optional[str] = Query(None, description="Trade needed e.g. Electrician"),
    city: Optional[str] = Query(None, description="City location"),
    status: Optional[str] = Query("open", description="Job status: open, in_progress, completed"),
    urgency: Optional[str] = Query(None, description="normal, urgent"),
    min_wage: Optional[float] = Query(None, description="Minimum daily wage offered"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List and filter active job opportunities.
    """
    return JobService.list_jobs(
        trade=trade,
        city=city,
        status=status,
        urgency=urgency,
        min_wage=min_wage,
        limit=limit,
        offset=offset
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int):
    """
    Get job posting details by ID.
    """
    job = JobService.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, updates: JobUpdate):
    """
    Update job parameters or status (e.g. mark as completed or filled).
    """
    job = JobService.update_job(job_id, updates)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.delete("/{job_id}", status_code=200)
def delete_job(
    job_id: int,
    authorization: Optional[str] = Header(None),
    employer_phone: Optional[str] = Query(None)
):
    """
    Employers can remove/delete their own job posting after hiring a worker or fulfilling work.
    Workers and non-owner employers are forbidden from deleting job postings.
    """
    job = JobService.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    user = None
    if authorization:
        user = AuthService.get_user_by_token(authorization)

    if user:
        if user.get("role") == "worker":
            raise HTTPException(
                status_code=403,
                detail="Workers are not authorized to remove job postings."
            )
        if user.get("role") == "employer":
            user_phone = (user.get("phone") or "").strip()
            job_emp_phone = (job.get("employer_phone") or "").strip()
            user_comp = (user.get("company_name") or user.get("full_name") or "").strip().lower()
            job_emp_name = (job.get("employer_name") or "").strip().lower()

            is_owner = (user_phone and user_phone == job_emp_phone) or (user_comp and user_comp == job_emp_name)
            if not is_owner:
                raise HTTPException(
                    status_code=403,
                    detail="Employers can only remove their own job postings, not those of other employers."
                )
    elif employer_phone and isinstance(employer_phone, str):
        job_emp_phone = (job.get("employer_phone") or "").strip()
        if employer_phone.strip() != job_emp_phone:
            raise HTTPException(
                status_code=403,
                detail="Employers can only remove their own job postings, not those of other employers."
            )

    success = JobService.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=500, detail="Could not delete job posting")
    return {
        "status": "success",
        "message": f"Work vacancy '{job['title']}' removed successfully.",
        "job_id": job_id
    }


@router.post("/{job_id}/hire/{worker_id}", status_code=200)
def hire_worker_for_job(
    job_id: int,
    worker_id: int,
    remove_job: bool = Query(True, description="Whether to remove the job listing after hiring"),
    authorization: Optional[str] = Header(None),
    employer_phone: Optional[str] = Query(None)
):
    """
    Employer hires a worker for a job:
    1. Sets worker availability to 'busy' (showing worker is busy in work).
    2. Increments worker's jobs_completed count.
    3. If remove_job is True, deletes/removes the job listing from the marketplace.
    Only the owning employer can hire for this job and remove it. Workers are forbidden.
    """
    job = JobService.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    user = None
    if authorization:
        user = AuthService.get_user_by_token(authorization)

    if user:
        if user.get("role") == "worker":
            raise HTTPException(
                status_code=403,
                detail="Workers are not authorized to hire or remove job postings."
            )
        if user.get("role") == "employer":
            user_phone = (user.get("phone") or "").strip()
            job_emp_phone = (job.get("employer_phone") or "").strip()
            user_comp = (user.get("company_name") or user.get("full_name") or "").strip().lower()
            job_emp_name = (job.get("employer_name") or "").strip().lower()

            is_owner = (user_phone and user_phone == job_emp_phone) or (user_comp and user_comp == job_emp_name)
            if not is_owner:
                raise HTTPException(
                    status_code=403,
                    detail="Employers can only hire and remove their own job postings."
                )
    elif employer_phone and isinstance(employer_phone, str):
        job_emp_phone = (job.get("employer_phone") or "").strip()
        if employer_phone.strip() != job_emp_phone:
            raise HTTPException(
                status_code=403,
                detail="Employers can only hire and remove their own job postings."
            )

    result = JobService.hire_worker_for_job(job_id=job_id, worker_id=worker_id, remove_job=remove_job)
    if not result:
        raise HTTPException(status_code=404, detail="Job or Worker not found")
    return result
