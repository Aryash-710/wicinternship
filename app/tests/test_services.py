import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, get_db
from app.services.location_service import LocationService
from app.services.wage_service import FairWageService
from app.services.matching_service import MatchingService
from app.services.worker_service import WorkerService
from app.services.job_service import JobService
from app.services.contact_service import ContactService
from app.services.ivr_service import IVRService, TelecomService
from app.models.schemas import WorkerCreate, JobCreate, ContactCreate

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def setup_module(module):
    """Initialize clean database before running tests"""
    init_db()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["services"]["workers"] == "UP"
    assert data["services"]["matching"] == "UP"
    assert data["services"]["wage_prediction"] == "UP"
    assert data["services"]["ivr_telecom"] == "UP"
    assert data["services"]["auth"] == "UP"


def test_location_service_distance():
    # Distance between Bengaluru (12.9716, 77.5946) and Mysuru (12.2958, 76.6394) is ~128-140 km
    dist = LocationService.haversine_distance(12.9716, 77.5946, 12.2958, 76.6394)
    assert 120 < dist < 155

    # City geocode lookup
    lat, lon, tier = LocationService.resolve_city_coords("Hubballi")
    assert tier == "Tier-2"
    assert 15.0 < lat < 16.0


def test_fair_wage_prediction():
    res = FairWageService.predict_fair_wage(
        trade="Electrician",
        city="Bengaluru",
        experience_years=5,
        has_own_tools=True,
        hours_per_day=8
    )
    assert res["trade"] == "Electrician"
    assert res["city_tier"] == "Tier-1"
    assert res["recommended_daily_wage"] >= 800.0
    assert "ಕನ್ನಡ" in res["regional_explanations"]["kannada"] or "ದಿನಗೂಲಿ" in res["regional_explanations"]["kannada"]
    assert "मजदूरी" in res["regional_explanations"]["hindi"]


def test_worker_registration_and_api():
    phone = "9845999001"
    payload = {
        "name": "Sharanu Gowda",
        "phone": phone,
        "trade": "Plumber",
        "experience_years": 4,
        "daily_rate": 750.0,
        "city": "Bengaluru",
        "area": "Malleshwaram",
        "language_pref": "kannada",
        "source": "web"
    }
    # Clean up if exists
    existing = WorkerService.get_worker_by_phone(phone)
    if not existing:
        res = client.post("/api/v1/workers/", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "Sharanu Gowda"
        assert data["trade"] == "Plumber"
        assert data["daily_rate"] == 750.0


def test_job_posting_and_api(client):
    payload = {
        "title": "Apartment Kitchen Pipe Leak Fix",
        "trade": "Plumber",
        "employer_name": "Narayana Swamy",
        "employer_phone": "9900887766",
        "city": "Bengaluru",
        "area": "Rajajinagar",
        "duration_days": 1,
        "wage_offered": 850.0,
        "urgency": "urgent",
        "workers_needed": 1
    }
    res = client.post("/api/v1/jobs/", json=payload)
    assert res.status_code == 201
    job_data = res.json()
    assert job_data["title"] == payload["title"]
    assert job_data["wage_offered"] == 850.0


def test_smart_matching_service():
    # Fetch a worker
    workers = WorkerService.list_workers(trade="Electrician", limit=1)
    assert len(workers) > 0
    worker = workers[0]

    matches = MatchingService.match_jobs_for_worker(worker["id"], max_radius_km=100.0)
    assert isinstance(matches, list)
    if matches:
        first = matches[0]
        assert "match_score" in first
        assert "breakdown" in first
        assert first["match_score"] >= 40.0
        assert "skill_score" in first["breakdown"]


def test_feed_service_endpoints(client):
    res_jobs = client.get("/api/v1/feeds/jobs?city=Bengaluru")
    assert res_jobs.status_code == 200
    jobs = res_jobs.json()
    assert isinstance(jobs, list)

    res_workers = client.get("/api/v1/feeds/workers?city=Bengaluru")
    assert res_workers.status_code == 200
    workers = res_workers.json()
    assert isinstance(workers, list)


def test_contact_service_and_sms(client):
    contact = client.post("/api/v1/contact/", json={
        "sender_type": "employer",
        "sender_id": 1,
        "receiver_type": "worker",
        "receiver_id": 1,
        "message": "We have an electrical wiring project."
    })
    assert contact.status_code == 201
    c_data = contact.json()
    assert c_data["status"] == "pending"

    # Simulate SMS dispatch
    sms_res = client.post(f"/api/v1/contact/{c_data['id']}/dispatch-sms")
    assert sms_res.status_code == 200
    sms_data = sms_res.json()
    assert sms_data["dispatch_status"] == "SENT"
    assert "KaayakaSetu" in sms_data["notification_text"]


def test_ivr_service_direct_unit_flows():
    call_sid = "CALL_UNIT_TEST_99"
    phone = "9845000111"

    from app.database import get_db
    with get_db() as conn:
        conn.execute("DELETE FROM workers WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM users WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM telecom_sessions WHERE session_id = ?", (call_sid,))

    # Step 0: Initial call greeting - asks whether Kannada or Hindi
    res_welcome = IVRService.handle_ivr_call(call_sid, phone, digits=None)
    assert res_welcome["action"] == "gather"
    assert "<Gather" in res_welcome["twiml_xml"]
    assert "ಕನ್ನಡಕ್ಕಾಗಿ 1" in res_welcome["prompt_text"]
    assert "हिन्दी के लिए 2" in res_welcome["prompt_text"]
    assert len(res_welcome["options"]) == 2

    # Step 1: Select Kannada (digits="1") -> Shows Kannada main menu strictly in Kannada
    res_menu = IVRService.handle_ivr_call(call_sid, phone, digits="1")
    assert res_menu["action"] == "gather"
    assert res_menu["language"] == "kannada"
    assert "ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ" in res_menu["prompt_text"]
    assert "श्रमसेतु" not in res_menu["prompt_text"]  # Strict single language!
    assert len(res_menu["options"]) == 3

    # Step 2: Option 1 - Worker Registration -> Prompt trade in Kannada
    res_reg1 = IVRService.handle_ivr_call(call_sid, phone, digits="1")
    assert res_reg1["action"] == "gather"
    assert res_reg1["language"] == "kannada"
    assert "ವೃತ್ತಿ" in res_reg1["prompt_text"]

    # Step 3: Choose trade (e.g. 1 for Electrician) -> Prompt experience in Kannada
    res_reg2 = IVRService.handle_ivr_call(call_sid, phone, digits="1")
    assert res_reg2["action"] == "gather"
    assert res_reg2["language"] == "kannada"
    assert "ಅನುಭವ" in res_reg2["prompt_text"]

    # Step 4: Choose experience (e.g. 3 for 3 years) -> Prompt location solely by voice in Kannada
    res_reg3 = IVRService.handle_ivr_call(call_sid, phone, digits="3")
    assert res_reg3["action"] == "gather"
    assert res_reg3["language"] == "kannada"
    assert ("ಸ್ಥಳ" in res_reg3["prompt_text"] or "ನಗರ" in res_reg3["prompt_text"])
    assert res_reg3["options"] == []  # Location options removed: voice input only!
    assert res_reg3.get("prompt_romanized") is not None

    # Step 5: Enter location via voice speech ("Bengaluru") -> Finalize & hangup in Kannada
    res_reg4 = IVRService.handle_ivr_call(call_sid, phone, speech_result="Bengaluru")
    assert res_reg4["action"] == "hangup"
    assert "<Hangup/>" in res_reg4["twiml_xml"]
    assert "ನೋಂದಾಯಿಸಲಾಗಿದೆ" in res_reg4["prompt_text"]

    # Step 6: If calling again with same registered phone:
    # Select Kannada -> Select Registration -> Confirms existing registration in Kannada
    call_sid_again = "CALL_UNIT_TEST_99_AGAIN"
    IVRService.handle_ivr_call(call_sid_again, phone, digits="1")  # Lang: Kannada
    res_again = IVRService.handle_ivr_call(call_sid_again, phone, digits="1")  # Reg
    assert res_again["action"] == "hangup"
    assert "ನೋಂದಾಯಿತವಾಗಿದೆ" in res_again["prompt_text"]

    # Step 7: Hindi Language Selection Flow
    call_sid_hi = "CALL_UNIT_TEST_HI"
    # Select Hindi (digits="2")
    res_hi_menu = IVRService.handle_ivr_call(call_sid_hi, phone, digits="2")
    assert res_hi_menu["action"] == "gather"
    assert res_hi_menu["language"] == "hindi"
    assert "श्रमसेतु में आपका स्वागत है" in res_hi_menu["prompt_text"]
    assert res_hi_menu.get("prompt_romanized") is not None
    assert "ShramSetu" in res_hi_menu["prompt_romanized"]
    assert "ಕಾಯಕಸೇತು" not in res_hi_menu["prompt_text"]  # Strict Hindi!

    # Step 8: Option 3 - Fair Daily Wage in Hindi
    res_hi_wage = IVRService.handle_ivr_call(call_sid_hi, phone, digits="3")
    assert res_hi_wage["action"] == "hangup"
    assert "मजदूरी" in res_hi_wage["prompt_text"]
    assert "ಕನ್ನಡ" not in res_hi_wage["prompt_text"]


def test_ivr_voice_bilingual_api_flow():
    from app.routers.telecom import process_ivr
    from app.models.schemas import IVRRequest

    call_sid = "CALL_TEST_101"
    phone = "9845011999"

    from app.database import get_db
    with get_db() as conn:
        conn.execute("DELETE FROM workers WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM users WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM telecom_sessions WHERE session_id = ?", (call_sid,))

    # Step 0: Call greeting via API - asks language
    res = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits=""))
    assert res.action == "gather"
    assert "ಕನ್ನಡಕ್ಕಾಗಿ 1" in res.prompt_text
    assert "हिन्दी के लिए 2" in res.prompt_text

    # Step 1: Select Kannada via voice speech ("kannada")
    res_lang = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="", speech_result="kannada"))
    assert res_lang.language == "kannada"
    assert "ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ" in res_lang.prompt_text

    # Step 2: Press Digit 1 for registration -> prompts trade in Kannada
    res_reg = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="1"))
    assert res_reg.action == "gather"
    assert "ವೃತ್ತಿ" in res_reg.prompt_text

    # Step 3: Voice input for trade: "Plumber"
    res_trade = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="", speech_result="Plumber"))
    assert "ಅನುಭವ" in res_trade.prompt_text

    # Step 4: Step exp: 4 (4 years) -> asks location by voice ONLY (no options)
    res_exp = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="4"))
    assert ("ಸ್ಥಳ" in res_exp.prompt_text or "ನಗರ" in res_exp.prompt_text)
    assert res_exp.options == []  # Location options removed: purely voice input!

    # Step 5: Voice input for city: "Hassan"
    res_city = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="", speech_result="Hassan"))
    assert res_city.action == "hangup"
    assert "ನೋಂದಾಯಿಸಲಾಗಿದೆ" in res_city.prompt_text
    assert "Hassan" in res_city.prompt_text


def test_auth_service_and_roles():
    from app.services.auth_service import AuthService

    # 1. Test Demo Worker Authentication
    w_user = AuthService.authenticate("ramesh_worker", "password123")
    assert w_user is not None
    assert w_user["role"] == "worker"
    assert w_user["phone"] == "9845011223"

    # 2. Test Demo Employer Authentication
    e_user = AuthService.authenticate("manjunatha_traders", "password123")
    assert e_user is not None
    assert e_user["role"] == "employer"
    assert e_user["phone"] == "9900112233"

    # 3. Test Invalid Password
    bad = AuthService.authenticate("ramesh_worker", "wrongpassword")
    assert bad is None

    # 4. Test Session Token Creation and Retrieval
    token = AuthService.create_session(w_user["id"])
    assert token.startswith("token_")
    retrieved = AuthService.get_user_by_token(token)
    assert retrieved is not None
    assert retrieved["id"] == w_user["id"]


def test_scoped_matching_queries_worker_and_employer(client):
    from app.services.auth_service import AuthService

    # Worker Token
    w_user = AuthService.authenticate("ramesh_worker", "password123")
    w_token = AuthService.create_session(w_user["id"])

    # Employer Token
    e_user = AuthService.authenticate("manjunatha_traders", "password123")
    e_token = AuthService.create_session(e_user["id"])

    # Test Worker Scoped Queries: Should contain only their 1 profile query
    res_w = client.get("/api/v1/match/my-queries", headers={"Authorization": f"Bearer {w_token}"})
    assert res_w.status_code == 200
    data_w = res_w.json()
    assert data_w["role"] == "worker"
    assert len(data_w["queries"]) == 1
    assert "Ramesh" in data_w["queries"][0]["label"]

    # Test Employer Scoped Queries: Should contain ONLY jobs posted by this employer (phone 9900112233)
    res_e = client.get("/api/v1/match/my-queries", headers={"Authorization": f"Bearer {e_token}"})
    assert res_e.status_code == 200
    data_e = res_e.json()
    assert data_e["role"] == "employer"
    for q in data_e["queries"]:
        assert "Commercial Shop 3-Phase Wiring" in q["label"] or "Bengaluru" in q["label"]

    # Test Scoped Matching Execution for Worker
    match_w = client.get("/api/v1/match/my-matches", headers={"Authorization": f"Bearer {w_token}"})
    assert match_w.status_code == 200
    m_data = match_w.json()
    assert m_data["mode"] == "worker_to_jobs"
    assert "matches" in m_data


def test_private_chat_service_and_isolation(client):
    from app.services.auth_service import AuthService

    # 1. User 1 (Ramesh)
    u1 = AuthService.authenticate("ramesh_worker", "password123")
    t1 = AuthService.create_session(u1["id"])

    # 2. User 3 (Shree Manjunatha Traders)
    u3 = AuthService.authenticate("manjunatha_traders", "password123")
    t3 = AuthService.create_session(u3["id"])

    # 3. User 2 (Manjunath Plumber - Third party)
    u2 = AuthService.authenticate("manjunath_plumber", "password123")
    t2 = AuthService.create_session(u2["id"])

    # User 3 sends a message to User 1
    send_res = client.post(
        "/api/v1/chat/send",
        headers={"Authorization": f"Bearer {t3}"},
        json={"receiver_id": u1["id"], "message_text": "Hello Ramesh from test!", "job_id": 1}
    )
    assert send_res.status_code == 200
    msg_data = send_res.json()
    assert msg_data["sender_id"] == u3["id"]
    assert msg_data["receiver_id"] == u1["id"]
    assert msg_data["message_text"] == "Hello Ramesh from test!"

    # User 1 fetches the thread with User 3: MUST see the message
    thread_res1 = client.get(
        f"/api/v1/chat/thread/{u3['id']}",
        headers={"Authorization": f"Bearer {t1}"}
    )
    assert thread_res1.status_code == 200
    msgs = thread_res1.json()
    assert any(m["message_text"] == "Hello Ramesh from test!" for m in msgs)

    # User 3 fetches the thread with User 1: MUST see the message
    thread_res3 = client.get(
        f"/api/v1/chat/thread/{u1['id']}",
        headers={"Authorization": f"Bearer {t3}"}
    )
    assert thread_res3.status_code == 200
    assert any(m["message_text"] == "Hello Ramesh from test!" for m in thread_res3.json())

    # PRIVACY ISOLATION TEST: User 2 (Third party) requests messages with User 1
    # User 2 MUST NOT see the conversation between User 1 and User 3!
    thread_res_u2 = client.get(
        f"/api/v1/chat/thread/{u1['id']}",
        headers={"Authorization": f"Bearer {t2}"}
    )
    assert thread_res_u2.status_code == 200
    # User 2 has not messaged User 1, so thread MUST NOT contain User 3's message!
    assert not any(m["message_text"] == "Hello Ramesh from test!" for m in thread_res_u2.json())

    # User 2 requests their conversations list: MUST NOT contain User 3
    convs_u2 = client.get("/api/v1/chat/conversations", headers={"Authorization": f"Bearer {t2}"}).json()
    assert not any(c.get("partner_id") == u3["id"] for c in convs_u2)


def test_chat_initiate_and_realtime_broadcast():
    import asyncio
    from app.services.chat_service import ChatService, chat_manager

    # Test initiate on job 1
    info = ChatService.get_or_create_user_for_target("job", 1)
    assert info is not None
    assert info["partner_id"] == 3
    assert "Shree Manjunatha Traders" in info["partner_name"]

    # Test initiate on worker 1
    winfo = ChatService.get_or_create_user_for_target("worker", 1)
    assert winfo is not None
    assert winfo["partner_id"] == 1
    assert "Ramesh Gowda" in winfo["partner_name"]

    # Test WebSocket connection manager
    received = []
    class DummyWS:
        async def accept(self): pass
        async def send_json(self, data): received.append(data)

    dummy = DummyWS()
    async def async_test():
        await chat_manager.connect(999, dummy)
        assert chat_manager.is_user_online(999)
        sent = await chat_manager.send_to_user(999, {"type": "ping"})
        assert sent is True
        assert len(received) == 1
        chat_manager.disconnect(999, dummy)
        assert not chat_manager.is_user_online(999)

    asyncio.run(async_test())


def test_custom_location_and_no_wage_input(client):
    from app.services.auth_service import AuthService
    from app.services.worker_service import WorkerService
    from app.database import get_db

    phone = "9845077889"
    with get_db() as conn:
        conn.execute("DELETE FROM workers WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM users WHERE phone = ?", (phone,))

    # Register worker with custom location and NO daily_rate specified
    reg_payload = {
        "username": "kanaka_carpenter",
        "phone": phone,
        "password": "password123",
        "role": "worker",
        "full_name": "Nagaraj Carpenter",
        "trade": "Carpenter",
        "experience_years": 5,
        "city": "Kanakapura Rural"
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    user = res.json()["user"]
    assert user["city"] == "Kanakapura Rural"

    # Worker record should have auto-calculated fair wage
    worker = WorkerService.get_worker_by_phone(phone)
    assert worker is not None
    assert worker["city"] == "Kanakapura Rural"
    assert worker["daily_rate"] > 0
    assert worker["daily_rate"] >= 800.0


def test_ivr_voice_speech_input_for_occupation_and_location():
    from app.database import get_db
    from app.services.worker_service import WorkerService
    from app.routers.telecom import process_ivr
    from app.models.schemas import IVRRequest

    call_sid = "CALL_VOICE_SPEECH_TEST_1"
    phone = "9845088991"

    with get_db() as conn:
        conn.execute("DELETE FROM workers WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM users WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM telecom_sessions WHERE session_id = ?", (call_sid,))

    # Step 0: Greeting - Asks language
    res0 = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits=""))
    assert res0.action == "gather"

    # Step 1: Select Kannada language (1)
    res_lang = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="1"))
    assert res_lang.action == "gather"
    assert "ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ" in res_lang.prompt_text

    # Step 2: Select Worker Registration (1 or voice "ನೋಂದಣಿ")
    res1 = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="1"))
    assert res1.action == "gather"
    assert "ವೃತ್ತಿ" in res1.prompt_text

    # Step 3: VOICE INPUT for OCCUPATION: say "Plumber" / "ಪ್ಲಂಬರ್"
    res_trade = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="", speech_result="ನಾನು ಪ್ಲಂಬರ್ ಕೆಲಸ ಮಾಡುತ್ತೇನೆ"))
    assert res_trade.action == "gather"
    assert "ಅನುಭವ" in res_trade.prompt_text

    # Step 4: Speak experience: say "3 years" / "ಮೂರು ವರ್ಷ"
    res_exp = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="", speech_result="3 years experience"))
    assert res_exp.action == "gather"
    assert "ಸ್ಥಳ" in res_exp.prompt_text
    assert res_exp.options == []  # Location options removed: voice input only!

    # Step 5: VOICE INPUT for LOCATION: say custom place "Kanakapura"
    res_city = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="", speech_result="Kanakapura"))
    assert res_city.action == "hangup"
    assert "ನೋಂದಾಯಿಸಲಾಗಿದೆ" in res_city.prompt_text

    # Verify worker was created with voice parsed trade and spoken location
    w = WorkerService.get_worker_by_phone(phone)
    assert w is not None
    assert w["trade"] == "Plumber"
    assert w["city"] == "Kanakapura"
    assert w["experience_years"] == 3
    assert w["daily_rate"] > 0


def test_twilio_kannada_voice_and_absolute_action_url():
    import os
    from starlette.requests import Request
    from app.routers.telecom import process_ivr_twiml
    from app.database import get_db

    call_sid = "TWILIO_CALL_TEST_KANNADA_VOICE_1"
    phone = "9845012345"

    with get_db() as conn:
        conn.execute("DELETE FROM workers WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM users WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM telecom_sessions WHERE session_id = ?", (call_sid,))

    # Create dummy Starlette Request simulating reverse proxy behind Render/ngrok
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/telecom/ivr/twiml",
        "headers": [
            (b"host", b"api.kaayakasetu.in"),
            (b"x-forwarded-proto", b"https"),
            (b"x-forwarded-host", b"bluecollar.onrender.com"),
        ],
        "query_string": b"",
    }
    req = Request(scope)

    # Step 0: Initial call - greeting
    res0 = process_ivr_twiml(request=req, CallSid=call_sid, From=phone, Digits=None)
    assert res0.status_code == 200
    xml_0 = res0.body.decode("utf-8")
    assert 'voice="Google.kn-IN-Standard-A"' in xml_0
    assert 'language="kn-IN"' in xml_0
    assert 'voice="Polly.Aditi"' in xml_0
    assert 'action="https://bluecollar.onrender.com/api/v1/telecom/ivr/twiml"' in xml_0

    # Step 1: User enters 1 for Kannada
    res1 = process_ivr_twiml(request=req, CallSid=call_sid, From=phone, Digits="1")
    assert res1.status_code == 200
    xml_1 = res1.body.decode("utf-8")
    assert '<Say language="kn-IN" voice="Google.kn-IN-Standard-A">' in xml_1
    assert "ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ" in xml_1
    assert 'action="https://bluecollar.onrender.com/api/v1/telecom/ivr/twiml"' in xml_1

    # Step 2: Environment variable override test
    os.environ["TWILIO_WEBHOOK_URL"] = "https://custom-proxy.ngrok-free.app/api/v1/telecom/ivr/twiml"
    try:
        res_env = process_ivr_twiml(request=req, CallSid=call_sid, From=phone, Digits="1")
        xml_env = res_env.body.decode("utf-8")
        assert 'action="https://custom-proxy.ngrok-free.app/api/v1/telecom/ivr/twiml"' in xml_env
    finally:
        os.environ.pop("TWILIO_WEBHOOK_URL", None)


def test_job_removal_and_worker_busy_flow():
    from app.services.worker_service import WorkerService
    from app.services.job_service import JobService
    from app.models.schemas import WorkerCreate, JobCreate
    from app.routers.jobs import hire_worker_for_job, delete_job
    from app.routers.workers import set_worker_status
    from app.database import get_db

    phone = "9845099881"
    emp_phone = "9845099882"

    with get_db() as conn:
        conn.execute("DELETE FROM workers WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM jobs WHERE employer_phone = ?", (emp_phone,))

    # Create worker
    w = WorkerService.create_worker(WorkerCreate(
        name="Test Plumber",
        phone=phone,
        trade="Plumber",
        experience_years=4,
        city="Bengaluru",
        availability="available"
    ))
    assert w["availability"] == "available"
    initial_completed = w.get("jobs_completed", 0)

    # Create job
    j = JobService.create_job(JobCreate(
        title="Kitchen Pipeline Repair",
        trade="Plumber",
        employer_name="Anand Employer",
        employer_phone=emp_phone,
        city="Bengaluru",
        wage_offered=850.0
    ))
    assert j is not None
    job_id = j["id"]

    # 1. Employer hires the worker for the job and removes the job listing
    hire_res = hire_worker_for_job(job_id=job_id, worker_id=w["id"], remove_job=True)
    assert hire_res["status"] == "success"
    assert hire_res["availability"] == "busy"
    assert hire_res["job_removed"] is True

    # Verify worker is now busy in work
    updated_w = WorkerService.get_worker(w["id"])
    assert updated_w["availability"] == "busy"
    assert updated_w["jobs_completed"] == initial_completed + 1

    # Verify job was removed from active listings
    assert JobService.get_job(job_id) is None

    # 2. Worker completes work and updates status back to available
    status_res = set_worker_status(worker_id=w["id"], availability="available")
    assert status_res["availability"] == "available"

    # 3. Test standalone delete_job
    j2 = JobService.create_job(JobCreate(
        title="Bathroom Tile Work",
        trade="Mason",
        employer_name="Anand Employer",
        employer_phone=emp_phone,
        city="Bengaluru",
        wage_offered=900.0
    ))
    del_res = delete_job(j2["id"])
    assert del_res["status"] == "success"
    assert JobService.get_job(j2["id"]) is None


def test_ivr_web_simulator_pure_hindi_flow():
    from app.routers.telecom import process_ivr
    from app.models.schemas import IVRRequest
    from app.database import get_db

    call_sid = "SIMULATOR_HINDI_SESSION_1"
    phone = "9845099883"

    with get_db() as conn:
        conn.execute("DELETE FROM workers WHERE phone = ?", (phone,))
        conn.execute("DELETE FROM telecom_sessions WHERE session_id = ?", (call_sid,))

    # Step 0: Simulator connects with language="hindi" -> Directly starts in Hindi!
    res0 = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="", language="hindi"))
    assert res0.action == "gather"
    assert res0.language == "hindi"
    assert "श्रमसेतु में आपका स्वागत है" in res0.prompt_text
    # Must NOT contain any Kannada text or options in the web simulator!
    assert "ಕನ್ನಡ" not in res0.prompt_text
    assert "ಕಾಯಕಸೇತು" not in res0.prompt_text
    assert any("पंजीकरण" in o["label"] for o in res0.options)

    # Step 1: Simulator user presses 1 for Worker Registration -> Continues purely in Hindi!
    res1 = process_ivr(IVRRequest(call_sid=call_sid, caller_phone=phone, digits="1", language="hindi"))
    assert res1.action == "gather"
    assert res1.language == "hindi"
    assert "श्रमिक पंजीकरण में आपका स्वागत है" in res1.prompt_text
    assert "ಕನ್ನಡ" not in res1.prompt_text




