from typing import List
from fastapi import APIRouter, HTTPException
from app.models.schemas import ContactCreate, ContactResponse, ContactStatusUpdate
from app.services.contact_service import ContactService

router = APIRouter(prefix="/api/v1/contact", tags=["Contact & Communication Microservice"])


@router.post("/", response_model=ContactResponse, status_code=201)
def initiate_contact(contact: ContactCreate):
    """
    Initiate contact request between worker and employer (e.g. apply for job, request worker hire).
    """
    created = ContactService.create_contact(contact)
    if not created:
        raise HTTPException(status_code=400, detail="Failed to initiate contact")
    return created


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int):
    """
    Get contact details and phone number.
    """
    res = ContactService.get_contact_with_details(contact_id)
    if not res:
        raise HTTPException(status_code=404, detail="Contact record not found")
    return res


@router.patch("/{contact_id}", response_model=ContactResponse)
def update_contact_status(contact_id: int, update: ContactStatusUpdate):
    """
    Update contact status: 'accepted' or 'declined'.
    """
    res = ContactService.update_status(contact_id, update)
    if not res:
        raise HTTPException(status_code=404, detail="Contact record not found")
    return res


@router.get("/user/{user_type}/{user_id}", response_model=List[ContactResponse])
def list_user_contacts(user_type: str, user_id: int):
    """
    List all inquiries and active leads for a worker or employer.
    """
    if user_type not in ("worker", "employer"):
        raise HTTPException(status_code=400, detail="user_type must be 'worker' or 'employer'")
    return ContactService.list_contacts_for_user(user_type, user_id)


@router.post("/{contact_id}/dispatch-sms")
def dispatch_sms(contact_id: int):
    """
    Simulates sending an SMS or WhatsApp notification to the worker or employer.
    """
    result = ContactService.simulate_dispatch_sms(contact_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result
