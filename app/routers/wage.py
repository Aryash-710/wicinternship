from typing import Optional
from fastapi import APIRouter, Query
from app.models.schemas import FairWageRequest, FairWageResponse
from app.services.wage_service import FairWageService

router = APIRouter(prefix="/api/v1/wage", tags=["Fair Wage Prediction Microservice"])


@router.post("/predict", response_model=FairWageResponse)
def predict_fair_wage(req: FairWageRequest):
    """
    Predict fair baseline and recommended daily/hourly wage with multi-factor intelligence
    and multi-lingual explanations in Kannada, Hindi, and English.
    """
    return FairWageService.predict_fair_wage(
        trade=req.trade,
        city=req.city,
        experience_years=req.experience_years,
        has_own_tools=req.has_own_tools,
        is_urgent=req.is_urgent,
        hours_per_day=req.hours_per_day
    )


@router.get("/benchmark")
def get_wage_benchmark(
    trade: str = Query(..., description="Trade e.g. Electrician, Mason, Plumber"),
    city: str = Query("Bengaluru", description="City location"),
    experience_years: int = Query(3, ge=0, le=40),
    wage_offered: Optional[float] = Query(None, description="Check fairness of an employer's offer")
):
    """
    Quick endpoint to check whether an employer's wage offer meets fair wage standards.
    """
    return FairWageService.predict_fair_wage(
        trade=trade,
        city=city,
        experience_years=experience_years,
        wage_offered=wage_offered
    )
