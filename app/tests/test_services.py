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

client = TestClient(app)


def setup_module(module):
    """Initialize clean database before running tests"""
    init_db()


def test_health_check():
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


def test_job_posting_and_api():
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


def test_feed_service_endpoints():
    res_jobs = client.get("/api/v1/feeds/jobs?city=Bengaluru")
    assert res_jobs.status_code == 200
    jobs = res_jobs.json()
    assert isinstance(jobs, list)

    res_workers = client.get("/api/v1/feeds/workers?city=Bengaluru")
    assert res_workers.status_code == 200
    workers = res_workers.json()
    assert isinstance(workers, list)


def test_contact_service_and_sms():
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

    # Step 1: Initial call greeting
    res_welcome = IVRService.handle_ivr_call(call_sid, phone, digits=None)
    assert res_welcome["action"] == "gather"
    assert "<Gather" in res_welcome["twiml_xml"]
    assert "ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ" in res_welcome["prompt_text"]
    assert "श्रमसेतु में आपका स्वागत है" in res_welcome["prompt_text"]
    assert len(res_welcome["options"]) == 3

    # Step 2: Option 1 - Worker Registration
    res_reg = IVRService.handle_ivr_call(call_sid, phone, digits="1")
    assert res_reg["action"] == "hangup"
    assert "<Hangup/>" in res_reg["twiml_xml"]
    assert "ನೋಂದಾಯಿಸಲಾಗಿದೆ" in res_reg["prompt_text"] or "ನೋಂದಾಯಿತವಾಗಿದೆ" in res_reg["prompt_text"]

    # Step 3: Option 2 - Find Jobs Voice Readout
    call_sid_2 = "CALL_UNIT_TEST_88"
    res_jobs = IVRService.handle_ivr_call(call_sid_2, phone, digits="2")
    assert res_jobs["action"] == "hangup"
    assert ("ಕೆಲಸ" in res_jobs["prompt_text"] or "ಲಭ್ಯವಿಲ್ಲ" in res_jobs["prompt_text"])

    # Step 4: Option 3 - Fair Daily Wage Voice Calculator
    call_sid_3 = "CALL_UNIT_TEST_77"
    res_wage = IVRService.handle_ivr_call(call_sid_3, phone, digits="3")
    assert res_wage["action"] == "hangup"
    assert "ದಿನಗೂಲಿ" in res_wage["prompt_text"]
    assert "मजदूरी" in res_wage["prompt_text"]


def test_ivr_voice_bilingual_api_flow():
    # Call greeting via API
    res = client.post("/api/v1/telecom/ivr", json={
        "call_sid": "CALL_TEST_101",
        "caller_phone": "9845011999",
        "digits": ""
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "gather"
    assert "ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ" in data["prompt_text"]
    assert "श्रमसेतु में आपका स्वागत है" in data["prompt_text"]

    # Press Digit 1 for registration
    res_reg = client.post("/api/v1/telecom/ivr", json={
        "call_sid": "CALL_TEST_101",
        "caller_phone": "9845011999",
        "digits": "1"
    })
    assert res_reg.status_code == 200
    data_reg = res_reg.json()
    assert data_reg["action"] == "hangup"
    assert "ನೋಂದಾಯಿಸಲಾಗಿದೆ" in data_reg["prompt_text"] or "ನೋಂದಾಯಿತವಾಗಿದೆ" in data_reg["prompt_text"]


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


def test_scoped_matching_queries_worker_and_employer():
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


def test_private_chat_service_and_isolation():
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

