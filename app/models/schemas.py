from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# Worker Schemas
# ==========================================
class WorkerBase(BaseModel):
    name: str = Field(..., examples=["Ramesh Gowda"])
    phone: str = Field(..., examples=["9845011223"])
    trade: str = Field(..., examples=["Electrician"])
    secondary_skills: Optional[str] = Field(None, examples=["Wiring, Inverter, MCB"])
    experience_years: int = Field(default=1, ge=0, le=50, examples=[5])
    daily_rate: Optional[float] = Field(default=None, gt=0, examples=[850.0])
    hourly_rate: Optional[float] = Field(None, gt=0, examples=[150.0])
    city: str = Field(..., examples=["Bengaluru"])
    area: Optional[str] = Field(None, examples=["Rajajinagar"])
    latitude: Optional[float] = Field(None, examples=[12.9904])
    longitude: Optional[float] = Field(None, examples=[77.5530])
    availability: str = Field(default="available", examples=["available"])  # available, busy, on_call
    language_pref: str = Field(default="kannada", examples=["kannada"])    # kannada, hindi, english
    source: str = Field(default="web", examples=["web"])                   # web, ivr


class WorkerCreate(WorkerBase):
    pass


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    trade: Optional[str] = None
    secondary_skills: Optional[str] = None
    experience_years: Optional[int] = None
    daily_rate: Optional[float] = None
    hourly_rate: Optional[float] = None
    city: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability: Optional[str] = None
    language_pref: Optional[str] = None


class WorkerResponse(WorkerBase):
    id: int
    rating: float = 4.5
    jobs_completed: int = 0
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Job Schemas
# ==========================================
class JobBase(BaseModel):
    title: str = Field(..., examples=["Shop Electrical Wiring"])
    trade: str = Field(..., examples=["Electrician"])
    description: Optional[str] = Field(None, examples=["3-Phase wiring for commercial establishment"])
    employer_name: str = Field(..., examples=["Shree Manjunatha Traders"])
    employer_phone: str = Field(..., examples=["9900112233"])
    city: str = Field(..., examples=["Bengaluru"])
    area: Optional[str] = Field(None, examples=["Rajajinagar"])
    latitude: Optional[float] = Field(None, examples=[12.9900])
    longitude: Optional[float] = Field(None, examples=[77.5520])
    duration_days: int = Field(default=1, ge=1, examples=[2])
    wage_offered: float = Field(..., gt=0, examples=[900.0])
    payment_type: str = Field(default="daily", examples=["daily"])  # daily, total, task
    urgency: str = Field(default="normal", examples=["urgent"])      # normal, urgent, scheduled
    workers_needed: int = Field(default=1, ge=1, examples=[2])


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    trade: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    wage_offered: Optional[float] = None
    urgency: Optional[str] = None
    workers_needed: Optional[int] = None
    status: Optional[str] = None


class JobResponse(JobBase):
    id: int
    status: str = "open"
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Contact Schemas
# ==========================================
class ContactCreate(BaseModel):
    sender_type: str = Field(..., examples=["worker"])  # 'worker' or 'employer'
    sender_id: int = Field(..., examples=[1])
    receiver_type: str = Field(..., examples=["employer"])
    receiver_id: int = Field(..., examples=[1])
    job_id: Optional[int] = Field(None, examples=[1])
    message: Optional[str] = Field(None, examples=["ನಮಸ್ಕಾರ, ನಾನು ಈ ಕೆಲಸ ಮಾಡಲು ಆಸಕ್ತನಾಗಿದ್ದೇನೆ."])


class ContactResponse(BaseModel):
    id: int
    sender_type: str
    sender_id: int
    receiver_type: str
    receiver_id: int
    job_id: Optional[int]
    message: Optional[str]
    status: str  # pending, accepted, declined
    phone_shared: int
    created_at: str
    sender_name: Optional[str] = None
    sender_phone: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None


class ContactStatusUpdate(BaseModel):
    status: str = Field(..., examples=["accepted"])  # accepted or declined


# ==========================================
# Matching Schemas
# ==========================================
class MatchScoreBreakdown(BaseModel):
    skill_score: float
    distance_score: float
    wage_score: float
    experience_score: float
    availability_score: float
    total_score: float
    distance_km: float
    explanation: str


class JobMatch(BaseModel):
    job: JobResponse
    match_score: float
    breakdown: MatchScoreBreakdown


class WorkerMatch(BaseModel):
    worker: WorkerResponse
    match_score: float
    breakdown: MatchScoreBreakdown


# ==========================================
# Fair Wage Prediction Schemas
# ==========================================
class FairWageRequest(BaseModel):
    trade: str = Field(..., examples=["Electrician"])
    city: str = Field(..., examples=["Bengaluru"])
    experience_years: int = Field(default=3, ge=0, le=40, examples=[5])
    has_own_tools: bool = Field(default=True, examples=[True])
    is_urgent: bool = Field(default=False, examples=[False])
    hours_per_day: int = Field(default=8, ge=1, le=14, examples=[8])


class FairWageResponse(BaseModel):
    trade: str
    city: str
    city_tier: str
    experience_years: int
    recommended_daily_wage: float
    recommended_hourly_wage: float
    fair_wage_min: float
    fair_wage_max: float
    wage_bracket: str
    factors: Dict[str, Any]
    regional_explanations: Dict[str, str]  # english, kannada, hindi


# ==========================================
# Telecom (IVR Voice) Schemas
# ==========================================
class IVRRequest(BaseModel):
    call_sid: str = Field(..., examples=["CA_ivr_102"])
    caller_phone: str = Field(default="9845011223", examples=["9845011223"])
    digits: Optional[str] = Field(default="", examples=["1"])
    speech_result: Optional[str] = Field(default=None, examples=["Plumber"])


class IVRResponse(BaseModel):
    call_sid: str
    twiml_xml: str
    prompt_text: str
    prompt_audio_text: str
    prompt_romanized: Optional[str] = None
    language: str
    action: str  # 'gather' or 'hangup'
    options: List[Dict[str, str]]


# ==========================================
# Authentication & User Profile Schemas
# ==========================================
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["ramesh_worker"])
    phone: str = Field(..., min_length=10, max_length=15, examples=["9845011223"])
    password: str = Field(..., min_length=4, examples=["password123"])
    role: str = Field(..., examples=["worker"])  # 'worker' or 'employer'
    full_name: str = Field(..., examples=["Ramesh Gowda"])
    city: Optional[str] = Field(default="Bengaluru", examples=["Bengaluru"])
    trade: Optional[str] = Field(default="Electrician", examples=["Electrician"])  # for worker
    daily_rate: Optional[float] = Field(default=None, examples=[800.0])          # for worker, auto-computed via fair wage if omitted
    experience_years: Optional[int] = Field(default=3, examples=[3])              # for worker
    company_name: Optional[str] = Field(default=None, examples=["Shree Traders"]) # for employer


class UserLoginRequest(BaseModel):
    username_or_phone: str = Field(..., examples=["ramesh_worker"])
    password: str = Field(..., examples=["password123"])


class UserResponse(BaseModel):
    id: int
    username: str
    phone: str
    role: str
    full_name: str
    worker_id: Optional[int] = None
    city: Optional[str] = None
    trade: Optional[str] = None
    company_name: Optional[str] = None


class AuthTokenResponse(BaseModel):
    token: str
    user: UserResponse
    message: str = "Authenticated successfully"


# ==========================================
# Real Private Chat & Messaging Schemas
# ==========================================
class MessageSendRequest(BaseModel):
    receiver_id: int
    message_text: str = Field(..., min_length=1, max_length=2000)
    job_id: Optional[int] = None


class MessageItem(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    job_id: Optional[int] = None
    message_text: str
    is_read: bool = False
    is_mine: bool = False
    created_at: str
    sender_name: Optional[str] = None
    sender_role: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_role: Optional[str] = None


class ConversationItem(BaseModel):
    other_user_id: int
    partner_id: int
    other_user_name: str
    partner_name: str
    other_user_role: str
    partner_role: str
    other_user_phone: str
    partner_phone: str
    other_user_trade: Optional[str] = None
    other_user_company: Optional[str] = None
    last_message: str
    last_message_at: str
    unread_count: int = 0
    job_id: Optional[int] = None
    job_title: Optional[str] = None


class ChatInitiateRequest(BaseModel):
    target_type: str  # 'job' or 'worker'
    target_id: int


class ChatInitiateResponse(BaseModel):
    partner_id: int
    partner_name: str
    partner_role: str
    partner_phone: str
    job_id: Optional[int] = None
    job_title: Optional[str] = None
    trade: Optional[str] = None
    other_user: Optional[Dict[str, Any]] = None

