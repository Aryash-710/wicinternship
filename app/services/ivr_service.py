import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from app.database import get_db
from app.models.schemas import WorkerCreate
from app.services.worker_service import WorkerService
from app.services.job_service import JobService
from app.services.wage_service import FairWageService

logger = logging.getLogger(__name__)

TRADE_OPTIONS = {
    "1": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ (Mason)", "hi": "राजमिस्त्री (Mason)"},
    "2": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್ (Electrician)", "hi": "इलेक्ट्रीशियन (Electrician)"},
    "3": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್ (Plumber)", "hi": "प्लंबर (Plumber)"},
    "4": {"trade": "Carpenter", "kn": "ಬಡಗಿ (Carpenter)", "hi": "बढ़ई (Carpenter)"},
    "5": {"trade": "Painter", "kn": "ಪೇಂಟರ್ (Painter)", "hi": "पेंटर (Painter)"},
    "6": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ (Helper)", "hi": "मजदूर (Helper)"},
}

CITY_OPTIONS = {
    "1": {"city": "Bengaluru", "kn": "ಬೆಂಗಳೂರು", "hi": "बेंगलुरु"},
    "2": {"city": "Mysuru", "kn": "ಮೈಸೂರು", "hi": "मैसूर"},
    "3": {"city": "Hubballi", "kn": "ಹುಬ್ಬಳ್ಳಿ", "hi": "हुबली"},
    "4": {"city": "Delhi", "kn": "ದೆಹಲಿ", "hi": "दिल्ली"},
    "5": {"city": "Lucknow", "kn": "ಲಕ್ನೋ", "hi": "लखनऊ"},
    "6": {"city": "Patna", "kn": "ಪಾಟ್ನಾ", "hi": "पटना"}
}


class IVRService:
    """
    Dedicated Interactive Voice Response (IVR) Microservice.
    Generates TwiML / Exotel voice XML responses and dual-language audio scripts
    in Kannada (ಕನ್ನಡ) and Hindi (हिन्दी) for blue-collar workers and employers.
    """

    @staticmethod
    def get_or_create_call_session(call_sid: str, phone: str) -> Dict[str, Any]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM telecom_sessions WHERE session_id = ?", (call_sid,))
            row = cursor.fetchone()
            if row:
                return {
                    "call_sid": row["session_id"],
                    "phone_number": row["phone_number"],
                    "current_step": row["current_step"],
                    "language": row["language"],
                    "draft": json.loads(row["draft_json"] or "{}")
                }

            cursor.execute("""
                INSERT INTO telecom_sessions (session_id, phone_number, session_type, current_step, language, draft_json)
                VALUES (?, ?, 'ivr', 'welcome', 'bilingual', '{}')
            """, (call_sid, phone))
            return {
                "call_sid": call_sid,
                "phone_number": phone,
                "current_step": "welcome",
                "language": "bilingual",
                "draft": {}
            }

    @staticmethod
    def update_call_session(call_sid: str, current_step: str, language: str, draft: Dict[str, Any]):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE telecom_sessions
                SET current_step = ?, language = ?, draft_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (current_step, language, json.dumps(draft), call_sid))

    @staticmethod
    def delete_call_session(call_sid: str):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM telecom_sessions WHERE session_id = ?", (call_sid,))

    @classmethod
    def handle_ivr_call(cls, call_sid: str, phone: str, digits: Optional[str] = None) -> Dict[str, Any]:
        """
        Main IVR State Machine.
        Handles DTMF inputs, executes actions (profile registration, job search, wage enquiry),
        and returns TwiML Voice XML with bilingual Kannada & Hindi audio scripts.
        """
        digits = (digits or "").strip()
        phone = (phone or "").strip() or "9845000000"
        session = cls.get_or_create_call_session(call_sid, phone)
        step = session.get("current_step", "welcome")

        # -------------------------------------------------------------
        # Step 0: Initial Call Greeting (No DTMF digits provided)
        # -------------------------------------------------------------
        if not digits:
            cls.update_call_session(call_sid, "menu", "bilingual", {})
            prompt_kn = (
                "ನಮಸ್ಕಾರ, ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ. "
                "ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ನೋಂದಾಯಿಸಲು 1 ಒತ್ತಿ. "
                "ಇಂದಿನ ಹೊಸ ಕೆಲಸಗಳ ಮಾಹಿತಿ ಕೇಳಲು 2 ಒತ್ತಿ. "
                "ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ದರ ತಿಳಿಯಲು 3 ಒತ್ತಿ."
            )
            prompt_hi = (
                "नमस्कार, श्रमसेतु में आपका स्वागत है। "
                "श्रमिक प्रोफ़ाइल दर्ज करने के लिए 1 दबाएं। "
                "आज के नए काम सुनने के लिए 2 दबाएं। "
                "उचित दैनिक मजदूरी दर जानने के लिए 3 दबाएं।"
            )

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="/api/v1/telecom/ivr" method="POST" timeout="10">
        <Say language="kn-IN" voice="Polly.Aditi">{prompt_kn}</Say>
        <Say language="hi-IN" voice="Polly.Aditi">{prompt_hi}</Say>
    </Gather>
    <Say language="kn-IN">ಯಾವುದೇ ಆಯ್ಕೆ ಸ್ವೀಕರಿಸಲಾಗಿಲ್ಲ. ಧನ್ಯವಾದಗಳು.</Say>
    <Hangup/>
</Response>"""

            return {
                "call_sid": call_sid,
                "twiml_xml": twiml,
                "prompt_text": f"[ಕನ್ನಡ]: {prompt_kn}\n[हिन्दी]: {prompt_hi}",
                "prompt_audio_text": f"{prompt_kn} {prompt_hi}",
                "language": "bilingual",
                "action": "gather",
                "options": [
                    {"digit": "1", "label": "ಕಾರ್ಮಿಕ ನೋಂದಣಿ / श्रमिक पंजीकरण (Register Profile)"},
                    {"digit": "2", "label": "ಹೊಸ ಕೆಲಸಗಳು / नए काम खोजें (Find Jobs)"},
                    {"digit": "3", "label": "ದಿನಗೂಲಿ ದರ ಪರಿಶೀಲನೆ / मजदूरी दर जांचें (Check Daily Wage)"}
                ]
            }

        # -------------------------------------------------------------
        # DTMF 1: Auto-Register or Confirm Worker Profile
        # -------------------------------------------------------------
        if digits == "1":
            cls.delete_call_session(call_sid)
            existing = WorkerService.get_worker_by_phone(phone)
            worker_display_name = f"Worker {phone[-4:]}" if len(phone) >= 4 else "New Worker"

            if existing:
                msg_kn = f"ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಕಾಯಕಸೇತುವಿನಲ್ಲಿ ಮೊದಲೇ ನೋಂದಾಯಿತವಾಗಿದೆ. ವೃತ್ತಿ: {existing['trade']}. ಸ್ಥಳ: {existing['city']}."
                msg_hi = f"नमस्ते! आपका मोबाइल नंबर श्रमसेतु पर पहले से पंजीकृत है। व्यवसाय: {existing['trade']}, शहर: {existing['city']}."
            else:
                WorkerService.create_worker(WorkerCreate(
                    name=worker_display_name,
                    phone=phone,
                    trade="Helper",
                    experience_years=2,
                    daily_rate=700.0,
                    city="Bengaluru",
                    language_pref="kannada",
                    source="ivr"
                ))
                msg_kn = "ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯನ್ನು ಕಾಯಕಸೇತುವಿನಲ್ಲಿ ಯಶಸ್ವಿಯಾಗಿ ನೋಂದಾಯಿಸಲಾಗಿದೆ. ಉದ್ಯೋಗದಾತರು ಶೀಘ್ರದಲ್ಲೇ ಸಂಪರ್ಕಿಸುತ್ತಾರೆ."
                msg_hi = "धन्यवाद! आपका मोबाइल नंबर श्रमसेतु पर पंजीकृत हो गया है। नियोक्ता आपसे जल्द संपर्क करेंगे।"

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN" voice="Polly.Aditi">{msg_kn}</Say>
    <Say language="hi-IN" voice="Polly.Aditi">{msg_hi}</Say>
    <Hangup/>
</Response>"""

            return {
                "call_sid": call_sid,
                "twiml_xml": twiml,
                "prompt_text": f"[ಕನ್ನಡ]: {msg_kn}\n[हिन्दी]: {msg_hi}",
                "prompt_audio_text": f"{msg_kn} {msg_hi}",
                "language": "bilingual",
                "action": "hangup",
                "options": []
            }

        # -------------------------------------------------------------
        # DTMF 2: Voice Job Listings (Read out latest open jobs)
        # -------------------------------------------------------------
        if digits == "2":
            cls.delete_call_session(call_sid)
            jobs = JobService.list_jobs(status="open", limit=2)
            if jobs:
                j1 = jobs[0]
                area = j1.get("area") or j1.get("city") or "ನಗರ"
                phone_num = j1.get("employer_phone", "ಲಭ್ಯವಿಲ್ಲ")
                msg_kn = f"ಇಂದಿನ ಕೆಲಸ: {j1['title']}, ಪ್ರದೇಶ: {area}, ದಿನಗೂಲಿ ₹{j1['wage_offered']:.0f}. ಸಂಪರ್ಕ ಸಂಖ್ಯೆ {phone_num}."
                msg_hi = f"आज का काम: {j1['title']}, क्षेत्र: {area}, दैनिक मजदूरी ₹{j1['wage_offered']:.0f}. संपर्क नंबर {phone_num}."
            else:
                msg_kn = "ಸದ್ಯಕ್ಕೆ ಹೊಸ ಕೆಲಸಗಳು ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಮರಳಿ ಕರೆ ಮಾಡಿ."
                msg_hi = "फिलहाल कोई नया काम उपलब्ध नहीं है। कृपया थोड़ी देर बाद फिर से कॉल करें।"

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN" voice="Polly.Aditi">{msg_kn}</Say>
    <Say language="hi-IN" voice="Polly.Aditi">{msg_hi}</Say>
    <Hangup/>
</Response>"""

            return {
                "call_sid": call_sid,
                "twiml_xml": twiml,
                "prompt_text": f"[ಕನ್ನಡ]: {msg_kn}\n[हिन्दी]: {msg_hi}",
                "prompt_audio_text": f"{msg_kn} {msg_hi}",
                "language": "bilingual",
                "action": "hangup",
                "options": []
            }

        # -------------------------------------------------------------
        # DTMF 3: Fair Daily Wage Voice Calculator
        # -------------------------------------------------------------
        if digits == "3":
            cls.delete_call_session(call_sid)
            pred = FairWageService.predict_fair_wage(trade="Electrician", city="Bengaluru", experience_years=4)
            rec_rate = pred.get("recommended_daily_wage", 850.0)
            wage_min = pred.get("fair_wage_min", 750.0)
            wage_max = pred.get("fair_wage_max", 950.0)

            msg_kn = (
                f"ಬೆಂಗಳೂರಿನಲ್ಲಿ ಎಲೆಕ್ಟ್ರಿಷಿಯನ್ ಕೆಲಸಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಿದ ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ₹{rec_rate:.0f}. "
                f"ದರ ಶ್ರೇಣಿ ₹{wage_min:.0f} ರಿಂದ ₹{wage_max:.0f} ಪ್ರತಿ ದಿನಕ್ಕೆ."
            )
            msg_hi = (
                f"बेंगलुरु में इलेक्ट्रीशियन काम के लिए अनुशंसित उचित दैनिक मजदूरी ₹{rec_rate:.0f} है। "
                f"उचित दायरा ₹{wage_min:.0f} से ₹{wage_max:.0f} प्रति दिन।"
            )

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN" voice="Polly.Aditi">{msg_kn}</Say>
    <Say language="hi-IN" voice="Polly.Aditi">{msg_hi}</Say>
    <Hangup/>
</Response>"""

            return {
                "call_sid": call_sid,
                "twiml_xml": twiml,
                "prompt_text": f"[ಕನ್ನಡ]: {msg_kn}\n[हिन्दी]: {msg_hi}",
                "prompt_audio_text": f"{msg_kn} {msg_hi}",
                "language": "bilingual",
                "action": "hangup",
                "options": []
            }

        # -------------------------------------------------------------
        # Fallback: Invalid Key
        # -------------------------------------------------------------
        cls.delete_call_session(call_sid)
        msg_kn = "ತಪ್ಪಾದ ಸಂಖ್ಯೆ ಒತ್ತಲಾಗಿದೆ. ದಯವಿಟ್ಟು ಮರಳಿ ಕರೆ ಮಾಡಿ."
        msg_hi = "गलत नंबर दबाया गया है। कृपया दोबारा कॉल करें।"

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN">{msg_kn}</Say>
    <Say language="hi-IN">{msg_hi}</Say>
    <Hangup/>
</Response>"""

        return {
            "call_sid": call_sid,
            "twiml_xml": twiml,
            "prompt_text": f"[ಕನ್ನಡ]: {msg_kn}\n[हिन्दी]: {msg_hi}",
            "prompt_audio_text": f"{msg_kn} {msg_hi}",
            "language": "bilingual",
            "action": "hangup",
            "options": []
        }


# Alias for backwards compatibility
TelecomService = IVRService

