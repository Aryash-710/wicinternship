from fastapi import APIRouter, Form, Response, Request
from typing import Optional
from app.models.schemas import IVRRequest, IVRResponse
from app.services.ivr_service import IVRService

router = APIRouter(prefix="/api/v1/telecom", tags=["IVR Voice Call Regional Microservice"])


@router.post("/ivr", response_model=IVRResponse)
def process_ivr(req: IVRRequest):
    """
    IVR Voice Call Webhook: processes DTMF and Voice Speech inputs and returns bilingual voice prompts
    in Kannada and Hindi for worker registration, job discovery, and fair wage calculation.
    """
    res = IVRService.handle_ivr_call(
        call_sid=req.call_sid,
        phone=req.caller_phone,
        digits=req.digits,
        speech_result=req.speech_result,
        action_url="/api/v1/telecom/ivr/twiml"
    )
    return IVRResponse(**res)


@router.post("/ivr/twiml")
def process_ivr_twiml(
    CallSid: str = Form(...),
    From: str = Form(""),
    Digits: Optional[str] = Form(None),
    SpeechResult: Optional[str] = Form(None)
):
    """
    Direct Twilio Voice XML webhook endpoint responding with TwiML (application/xml).
    Supports both DTMF digits and Speech input (SpeechResult).
    """
    res = IVRService.handle_ivr_call(
        call_sid=CallSid,
        phone=From,
        digits=Digits,
        speech_result=SpeechResult,
        action_url="/api/v1/telecom/ivr/twiml"
    )
    return Response(content=res["twiml_xml"], media_type="application/xml")


@router.post("/ivr/exotel")
def process_ivr_exotel(
    CallSid: str = Form(...),
    From: str = Form(""),
    Digits: Optional[str] = Form(None),
    SpeechResult: Optional[str] = Form(None)
):
    """
    Direct Exotel Voice XML webhook endpoint responding with Exotel/TwiML XML.
    """
    res = IVRService.handle_ivr_call(
        call_sid=CallSid,
        phone=From,
        digits=Digits,
        speech_result=SpeechResult,
        action_url="/api/v1/telecom/ivr/exotel"
    )
    return Response(content=res["twiml_xml"], media_type="application/xml")


@router.post("/ivr/reset")
def reset_ivr_session(call_sid: str):
    """
    Manually clear/reset an active IVR call session.
    """
    IVRService.delete_call_session(call_sid)
    return {"status": "success", "call_sid": call_sid, "message": "IVR call session reset"}
