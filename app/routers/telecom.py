from fastapi import APIRouter, Form, Response, Request
from typing import Optional
from app.models.schemas import USSDRequest, USSDResponse, IVRRequest, IVRResponse
from app.services.ivr_ussd_service import TelecomService

router = APIRouter(prefix="/api/v1/telecom", tags=["IVR & USSD Regional Language Microservice"])


@router.post("/ussd", response_model=USSDResponse)
async def process_ussd(req: USSDRequest):
    """
    USSD Gateway endpoint: handles *345# session flows in Kannada, Hindi, and English
    to register worker profiles, find nearby jobs, and check fair wages.
    """
    action, message = TelecomService.handle_ussd(
        session_id=req.session_id,
        phone=req.phone_number,
        user_input=req.user_input
    )
    return USSDResponse(
        session_id=req.session_id,
        action=action,
        message=f"{action} {message}"
    )


@router.post("/ussd/form")
async def process_ussd_telecom_form(
    sessionId: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form("")
):
    """
    Standard Africa's Talking / Exotel USSD webhook format:
    Accepts form-encoded sessionId, phoneNumber, and text (e.g. '1*2*4').
    Returns raw plain-text response: 'CON ...' or 'END ...'.
    """
    latest_input = text.split("*")[-1] if "*" in text else text
    action, message = TelecomService.handle_ussd(
        session_id=sessionId,
        phone=phoneNumber,
        user_input=latest_input
    )
    raw_response = f"{action} {message}"
    return Response(content=raw_response, media_type="text/plain")


@router.post("/ivr", response_model=IVRResponse)
async def process_ivr(req: IVRRequest):
    """
    IVR Voice Call Webhook: returns bilingual voice prompts in Kannada and Hindi
    for worker registration and job discovery.
    """
    res = TelecomService.handle_ivr_call(
        call_sid=req.call_sid,
        phone=req.caller_phone,
        digits=req.digits
    )
    return IVRResponse(**res)


@router.post("/ivr/twiml")
async def process_ivr_twiml(
    CallSid: str = Form(...),
    From: str = Form(...),
    Digits: Optional[str] = Form(None)
):
    """
    Direct Twilio / Exotel Voice XML endpoint responding with TwiML.
    """
    res = TelecomService.handle_ivr_call(
        call_sid=CallSid,
        phone=From,
        digits=Digits
    )
    return Response(content=res["twiml_xml"], media_type="application/xml")


@router.post("/ussd/reset")
def reset_ussd_session(session_id: str):
    """
    Manually clear/reset a USSD session.
    """
    TelecomService.delete_session(session_id)
    return {"status": "success", "session_id": session_id, "message": "Session reset"}
