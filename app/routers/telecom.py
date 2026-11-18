import os
import uuid
from typing import Optional
from fastapi import APIRouter, Form, Response, Request
from app.models.schemas import IVRRequest, IVRResponse
from app.services.ivr_service import IVRService

router = APIRouter(prefix="/api/v1/telecom", tags=["IVR Voice Call Regional Microservice"])


def _resolve_action_url(request: Optional[Request], endpoint_path: str) -> str:
    """
    Constructs an absolute public HTTPS URL for Twilio/Exotel webhooks.
    This guarantees that Twilio never errors out with 'no URL' or relative URL resolution failures
    when running behind reverse proxies (Render, ngrok, Railway, Cloudflare).
    """
    # 1. Environment variable override (e.g. PUBLIC_URL, BASE_URL, TWILIO_WEBHOOK_URL)
    env_url = (
        os.environ.get("TWILIO_WEBHOOK_URL")
        or os.environ.get("PUBLIC_URL")
        or os.environ.get("BASE_URL")
    )
    if env_url:
        env_url = env_url.strip()
        if endpoint_path in env_url:
            return env_url
        return f"{env_url.rstrip('/')}{endpoint_path}"

    # 2. Extract protocol and host from request headers
    if request is not None:
        proto = request.headers.get("x-forwarded-proto") or request.url.scheme or "https"
        if "," in proto:
            proto = proto.split(",")[0].strip()

        host = (
            request.headers.get("x-forwarded-host")
            or request.headers.get("host")
            or request.url.netloc
        )
        if "," in host:
            host = host.split(",")[0].strip()

        if host:
            return f"{proto}://{host}{endpoint_path}"

    return endpoint_path


def _clean_str(val: Optional[object]) -> Optional[str]:
    """
    Safely extract a clean string from a parameter value, guarding against
    FastAPI Form default parameter objects during direct python invocations.
    """
    if val is None or not isinstance(val, (str, int, float)):
        return None
    s = str(val).strip()
    return s if s else None


@router.post("/ivr", response_model=IVRResponse)
def process_ivr(req: IVRRequest):
    """
    IVR Voice Call Webhook: processes DTMF and Voice Speech inputs.
    When req.language == 'hindi' (used by the Web Simulator), converses purely in Hindi.
    When req.language is None (used by automated bilingual testing), proceeds bilingually.
    """
    res = IVRService.handle_ivr_call(
        call_sid=req.call_sid,
        phone=req.caller_phone,
        digits=req.digits,
        speech_result=req.speech_result,
        action_url="/api/v1/telecom/ivr/twiml",
        default_language=req.language
    )
    return IVRResponse(**res)


@router.api_route("/ivr/twiml", methods=["GET", "POST"])
def process_ivr_twiml(
    request: Request,
    CallSid: Optional[str] = Form(None),
    From: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
    SpeechResult: Optional[str] = Form(None)
):
    """
    Direct Twilio Voice XML webhook endpoint responding with TwiML (application/xml).
    Supports both DTMF digits and Speech input (SpeechResult).
    Uses absolute HTTPS action_url to prevent Twilio 'no URL' redirection drops.
    """
    query = request.query_params if request else {}
    call_sid = (
        _clean_str(CallSid)
        or query.get("CallSid")
        or query.get("call_sid")
        or f"tw_{uuid.uuid4().hex[:12]}"
    )
    caller_phone = (
        _clean_str(From)
        or query.get("From")
        or query.get("caller_phone")
        or "9845000000"
    )
    digits = _clean_str(Digits) or query.get("Digits") or query.get("digits")
    speech_result = _clean_str(SpeechResult) or query.get("SpeechResult") or query.get("speech_result")

    action_url = _resolve_action_url(request, "/api/v1/telecom/ivr/twiml")

    res = IVRService.handle_ivr_call(
        call_sid=call_sid,
        phone=caller_phone,
        digits=digits,
        speech_result=speech_result,
        action_url=action_url
    )
    return Response(content=res["twiml_xml"], media_type="application/xml")


@router.api_route("/ivr/exotel", methods=["GET", "POST"])
def process_ivr_exotel(
    request: Request,
    CallSid: Optional[str] = Form(None),
    From: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
    SpeechResult: Optional[str] = Form(None)
):
    """
    Direct Exotel Voice XML webhook endpoint responding with Exotel/TwiML XML.
    """
    query = request.query_params if request else {}
    call_sid = (
        _clean_str(CallSid)
        or query.get("CallSid")
        or query.get("call_sid")
        or f"exo_{uuid.uuid4().hex[:12]}"
    )
    caller_phone = (
        _clean_str(From)
        or query.get("From")
        or query.get("caller_phone")
        or "9845000000"
    )
    digits = _clean_str(Digits) or query.get("Digits") or query.get("digits")
    speech_result = _clean_str(SpeechResult) or query.get("SpeechResult") or query.get("speech_result")

    action_url = _resolve_action_url(request, "/api/v1/telecom/ivr/exotel")

    res = IVRService.handle_ivr_call(
        call_sid=call_sid,
        phone=caller_phone,
        digits=digits,
        speech_result=speech_result,
        action_url=action_url
    )
    return Response(content=res["twiml_xml"], media_type="application/xml")


@router.post("/ivr/reset")
def reset_ivr_session(call_sid: str):
    """
    Manually clear/reset an active IVR call session.
    """
    IVRService.delete_call_session(call_sid)
    return {"status": "success", "call_sid": call_sid, "message": "IVR call session reset"}
