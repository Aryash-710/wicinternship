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
from app.services.ivr_ussd_service import TelecomService
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
    assert data["services"]["ivr_ussd_telecom"] == "UP"


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


def test_ussd_regional_kannada_flow():
    session_id = "test_ussd_kn_99"
    phone = "9845000111"

    # Step 1: Initial dial
    action, text = TelecomService.handle_ussd(session_id, phone, "*345#")
    assert action == "CON"
    assert "1. ಕನ್ನಡ" in text

    # Step 2: Select Kannada (Option 1)
    action, text = TelecomService.handle_ussd(session_id, phone, "1")
    assert action == "CON"
    assert "ಕಾಯಕಸೇತು ಮುಖ್ಯ ಮೆನು" in text
    assert "1. ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ನೋಂದಣಿ" in text

    # Step 3: Select Registration (Option 1)
    action, text = TelecomService.handle_ussd(session_id, phone, "1")
    assert action == "CON"
    assert "ಕೌಶಲ್ಯ/ವೃತ್ತಿ ಆಯ್ಕೆ ಮಾಡಿ" in text

    # Step 4: Select Trade (Option 2 = Electrician)
    action, text = TelecomService.handle_ussd(session_id, phone, "2")
    assert action == "CON"
    assert "ಅನುಭವ ಎಷ್ಟು ವರ್ಷ" in text

    # Step 5: Enter Experience (5 years)
    action, text = TelecomService.handle_ussd(session_id, phone, "5")
    assert action == "CON"
    assert "ದೈನಂದಿನ ಕೂಲಿ" in text

    # Step 6: Enter Expected Daily Wage (850)
    action, text = TelecomService.handle_ussd(session_id, phone, "850")
    assert action == "CON"
    assert "ನಗರ/ಜಿಲ್ಲೆ ಆಯ್ಕೆ ಮಾಡಿ" in text

    # Step 7: Select City (Option 1 = Bengaluru)
    action, text = TelecomService.handle_ussd(session_id, phone, "1")
    assert action == "END"
    assert "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಯಶಸ್ವಿಯಾಗಿ ನೋಂದಾಯಿಸಲಾಗಿದೆ" in text


def test_ussd_regional_hindi_jobs_flow():
    session_id = "test_ussd_hi_88"
    phone = "9811000222"

    # Step 1: Initial dial
    action, text = TelecomService.handle_ussd(session_id, phone, "*345#")
    assert action == "CON"

    # Step 2: Select Hindi (Option 2)
    action, text = TelecomService.handle_ussd(session_id, phone, "2")
    assert action == "CON"
    assert "श्रमसेतु मुख्य मेन्यू" in text
    assert "2. नजदीकी काम खोजें" in text

    # Step 3: Select Find Jobs (Option 2)
    action, text = TelecomService.handle_ussd(session_id, phone, "2")
    assert action == "CON"
    assert "हुनर चुनें" in text

    # Step 4: Choose Electrician (Option 2)
    action, text = TelecomService.handle_ussd(session_id, phone, "2")
    assert action == "END"
    assert ("काम" in text or "दुकान" in text or "उपलब्ध" in text)


def test_ivr_voice_bilingual_flow():
    # Call greeting
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

    # Press Digit 1 for auto-registration
    res_reg = client.post("/api/v1/telecom/ivr", json={
        "call_sid": "CALL_TEST_101",
        "caller_phone": "9845011999",
        "digits": "1"
    })
    assert res_reg.status_code == 200
    data_reg = res_reg.json()
    assert data_reg["action"] == "hangup"
    assert "ನೋಂದಾಯಿಸಲಾಗಿದೆ" in data_reg["prompt_text"]
    assert "पंजीकृत" in data_reg["prompt_text"]
