import json
import logging
import re
from typing import Dict, Any, Optional, Tuple, List
from app.database import get_db
from app.models.schemas import WorkerCreate
from app.services.worker_service import WorkerService
from app.services.job_service import JobService
from app.services.wage_service import FairWageService

logger = logging.getLogger(__name__)

TRADE_OPTIONS: Dict[str, Dict[str, str]] = {
    "1": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "2": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "3": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "4": {"trade": "Carpenter", "kn": "ಬಡಗಿ", "hi": "बढ़ई"},
    "5": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "6": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "7": {"trade": "Welder", "kn": "ವೆಲ್ಡರ್", "hi": "वेल्डर"},
}

CITY_OPTIONS: Dict[str, Dict[str, str]] = {
    "1": {"city": "Bengaluru", "kn": "ಬೆಂಗಳೂರು", "hi": "बेंगलुरु"},
    "2": {"city": "Mysuru", "kn": "ಮೈಸೂರು", "hi": "मैसूर"},
    "3": {"city": "Hubballi", "kn": "ಹುಬ್ಬಳ್ಳಿ", "hi": "हुबली"},
    "4": {"city": "Belagavi", "kn": "ಬೆಳಗಾವಿ", "hi": "बेलगाम"},
    "5": {"city": "Mangaluru", "kn": "ಮಂಗಳೂರು", "hi": "मंगलुरु"},
    "6": {"city": "Kalaburagi", "kn": "ಕಲಬುರಗಿ", "hi": "कलबुर्गी"},
    "7": {"city": "Delhi", "kn": "ದೆಹಲಿ", "hi": "दिल्ली"},
    "8": {"city": "Hassan", "kn": "ಹಾಸನ ಅಥವಾ ಇತರ ಜಿಲ್ಲೆ", "hi": "हासन या अन्य जिला"},
}

TRADE_KEYWORDS: Dict[str, Dict[str, str]] = {
    # Electrician
    "electrician": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "electric": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "wiring": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "wireman": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "ವೈರಿಂಗ್": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "ಕರೆಂಟ್": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "इलेक्ट्रीशियन": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "बिजली": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "वायरमैन": {"trade": "Electrician", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},

    # Plumber
    "plumber": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "pipe": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "fitting": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "ಪ್ಲಂಬರ್": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "ನಲ್ಲಿ": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "ಪೈಪ್": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "प्लंबर": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "नल": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "पाइप": {"trade": "Plumber", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},

    # Mason
    "mason": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "mestri": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "construction": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "brick": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "ಮೇಸ್ತ್ರಿ": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "ಗಾರೆ": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "ಕಟ್ಟಡ": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "मिस्त्री": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "राजमिस्त्री": {"trade": "Mason", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},

    # Carpenter
    "carpenter": {"trade": "Carpenter", "kn": "ಬಡಗಿ", "hi": "बढ़ई"},
    "wood": {"trade": "Carpenter", "kn": "ಬಡಗಿ", "hi": "बढ़ई"},
    "furniture": {"trade": "Carpenter", "kn": "ಬಡಗಿ", "hi": "बढ़ई"},
    "ಬಡಗಿ": {"trade": "Carpenter", "kn": "ಬಡಗಿ", "hi": "बढ़ई"},
    "ಮರಗೆಲಸ": {"trade": "Carpenter", "kn": "ಬಡಗಿ", "hi": "बढ़ई"},
    "बढ़ई": {"trade": "Carpenter", "kn": "ಬಡಗಿ", "hi": "बढ़ई"},

    # Painter
    "painter": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "paint": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "color": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "ಪೇಂಟರ್": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "ಬಣ್ಣ": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "पेंटर": {"trade": "Painter", "kn": "पೇಂಟರ್", "hi": "पेंटर"},
    "रंगाई": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},

    # Helper
    "helper": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "labour": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "coolie": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "hamali": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "ಕೂಲಿ": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "ಲೇಬರ್": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "ಹಮಾಲಿ": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "ಸಹಾಯಕ": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "मजदूर": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "सहायक": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},

    # Welder
    "welder": {"trade": "Welder", "kn": "ವೆಲ್ಡರ್", "hi": "वेल्डर"},
    "welding": {"trade": "Welder", "kn": "ವೆಲ್ಡರ್", "hi": "वेल्डर"},
    "ವೆಲ್ಡರ್": {"trade": "Welder", "kn": "ವೆಲ್ಡರ್", "hi": "वेल्डर"},
    "वेल्डर": {"trade": "Welder", "kn": "ವೆಲ್ಡರ್", "hi": "वेल्डर"}
}


class IVRService:
    """
    Dedicated Interactive Voice Response (IVR) Microservice.
    Generates TwiML / Exotel voice XML responses and dual-language audio scripts
    in Kannada (ಕನ್ನಡ) and Hindi (हिन्दी) for blue-collar workers and employers.
    Supports both Speech Voice input and DTMF keypad tones for occupation and location.
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

    @staticmethod
    def resolve_trade(digits: Optional[str], speech: Optional[str]) -> Dict[str, str]:
        """
        Resolves trade from keypad digit or spoken voice audio in Kannada, Hindi, or English.
        """
        d = (digits or "").strip()
        if d in TRADE_OPTIONS:
            return TRADE_OPTIONS[d]

        s = (speech or "").strip().lower()
        if s:
            for kw, meta in TRADE_KEYWORDS.items():
                if kw in s:
                    return meta
            # User spoke an unlisted trade by voice (e.g. "Driver", "Tile Worker")
            spoken = speech.strip().title()
            return {"trade": spoken, "kn": spoken, "hi": spoken}

        return TRADE_OPTIONS["1"]

    @staticmethod
    def resolve_experience(digits: Optional[str], speech: Optional[str]) -> int:
        """
        Resolves experience years from keypad digit or spoken voice phrase.
        """
        d = (digits or "").strip()
        if d.isdigit() and int(d) > 0:
            return max(1, min(int(d), 40))

        s = (speech or "").strip()
        if s:
            nums = re.findall(r'\d+', s)
            if nums:
                return max(1, min(int(nums[0]), 40))

            word_map = {
                "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                "ಒಂದು": 1, "ಎರಡು": 2, "ಮೂರು": 3, "ನಾಲ್ಕು": 4, "ಐದು": 5, "ಆರು": 6, "ಏಳು": 7, "ಎಂಟು": 8, "ಒಂಬತ್ತು": 9, "ಹತ್ತು": 10,
                "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10
            }
            s_lower = s.lower()
            for w, val in word_map.items():
                if w in s_lower:
                    return val

        return 2

    @staticmethod
    def resolve_location(digits: Optional[str], speech: Optional[str]) -> Dict[str, str]:
        """
        Resolves city/location from keypad digit or spoken voice name (any village/town/city).
        """
        d = (digits or "").strip()
        if d in CITY_OPTIONS:
            return CITY_OPTIONS[d]

        s = (speech or "").strip()
        if s:
            cleaned = s.rstrip(".,!?").strip().title()
            if cleaned:
                return {"city": cleaned, "kn": s, "hi": s}

        return CITY_OPTIONS["1"]

    @classmethod
    def handle_ivr_call(
        cls,
        call_sid: str,
        phone: str,
        digits: Optional[str] = None,
        speech_result: Optional[str] = None,
        action_url: str = "/api/v1/telecom/ivr/twiml"
    ) -> Dict[str, Any]:
        """
        Main IVR State Machine.
        Handles both DTMF keypad tones and Speech Voice inputs for occupation and location.
        Returns TwiML Voice XML with bilingual Kannada & Hindi audio scripts.
        """
        digits = (digits or "").strip()
        speech = (speech_result or "").strip()
        phone = (phone or "").strip() or "9845000000"

        session = cls.get_or_create_call_session(call_sid, phone)
        step = session.get("current_step", "welcome")
        draft = session.get("draft", {})

        # -------------------------------------------------------------
        # Step 0: Initial Call Greeting (No DTMF digits and no speech)
        # -------------------------------------------------------------
        if not digits and not speech:
            cls.update_call_session(call_sid, "menu", "bilingual", {})
            prompt_kn = (
                "ನಮಸ್ಕಾರ, ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ. "
                "ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ನೋಂದಾಯಿಸಲು 1 ಒತ್ತಿ ಅಥವಾ ನೋಂದಣಿ ಎಂದು ಮಾತನಾಡಿ. "
                "ಇಂದಿನ ಹೊಸ ಕೆಲಸಗಳ ಮಾಹಿತಿ ಕೇಳಲು 2 ಒತ್ತಿ. "
                "ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ದರ ತಿಳಿಯಲು 3 ಒತ್ತಿ."
            )
            prompt_hi = (
                "नमस्कार, श्रमसेतु में आपका स्वागत है। "
                "श्रमिक प्रोफ़ाइल दर्ज करने के लिए 1 दबाएं या पंजीकरण बोलें। "
                "आज के नए काम सुनने के लिए 2 दबाएं। "
                "उचित दैनिक मजदूरी दर जानने के लिए 3 दबाएं।"
            )

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech dtmf" numDigits="1" speechTimeout="auto" action="{action_url}" method="POST" timeout="10">
        <Say language="kn-IN">{prompt_kn}</Say>
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
        # Step 1: Main Menu Handler
        # -------------------------------------------------------------
        if step in ("welcome", "menu"):
            speech_lower = speech.lower()
            is_reg = digits == "1" or any(k in speech_lower for k in ("ನೋಂದಣಿ", "ಪಂಜೀಕರಣ", "register", "registration", "profile"))
            is_jobs = digits == "2" or any(k in speech_lower for k in ("ಕೆಲಸ", "ಕಾಮ", "job", "work"))
            is_wage = digits == "3" or any(k in speech_lower for k in ("ದಿನಗೂಲಿ", "ಮಜದೂರಿ", "wage", "rate", "salary"))

            if is_reg:
                existing = WorkerService.get_worker_by_phone(phone)
                if existing:
                    cls.delete_call_session(call_sid)
                    msg_kn = (
                        f"ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಕಾಯಕಸೇತುವಿನಲ್ಲಿ ಮೊದಲೇ ನೋಂದಾಯಿತವಾಗಿದೆ. "
                        f"ಹೆಸರು: {existing['name']}. ವೃತ್ತಿ: {existing['trade']}. ಸ್ಥಳ: {existing['city']}."
                    )
                    msg_hi = (
                        f"नमस्ते! आपका मोबाइल नंबर श्रमसेतु पर पहले से पंजीकृत है। "
                        f"नाम: {existing['name']}, व्यवसाय: {existing['trade']}, शहर: {existing['city']}."
                    )

                    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN">{msg_kn}</Say>
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

                # Transition to reg_trade step to capture occupation via voice or digit
                cls.update_call_session(call_sid, "reg_trade", "bilingual", {})
                prompt_kn = (
                    "ಕಾರ್ಮಿಕ ನೋಂದಣಿಗೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ವೃತ್ತಿಯ ಹೆಸರನ್ನು ನೇರವಾಗಿ ಮಾತನಾಡಿ, "
                    "ಅಥವಾ ಕೀಲಿಮಣೆಯಲ್ಲಿ ಒತ್ತಿ: 1 ಎಲೆಕ್ಟ್ರಿಷಿಯನ್, 2 ಪ್ಲಂಬರ್, 3 ಮೇಸ್ತ್ರಿ, 4 ಬಡಗಿ, 5 ಪೇಂಟರ್, 6 ಕೂಲಿ ಕಾರ್ಮಿಕ, 7 ವೆಲ್ಡರ್."
                )
                prompt_hi = (
                    "श्रमिक पंजीकरण में आपका स्वागत है। अपने व्यवसाय का नाम सीधे बोलें, "
                    "या कीपैड पर दबाएं: 1 इलेक्ट्रीशियन, 2 प्लंबर, 3 राजमिस्त्री, 4 बढ़ई, 5 पेंटर, 6 मजदूर, 7 वेल्डर।"
                )

                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech dtmf" numDigits="1" speechTimeout="auto" action="{action_url}" method="POST" timeout="12">
        <Say language="kn-IN">{prompt_kn}</Say>
        <Say language="hi-IN" voice="Polly.Aditi">{prompt_hi}</Say>
    </Gather>
    <Say language="kn-IN">ಸಮಯ ಮೀರಿದೆ. ದಯವಿಟ್ಟು ಮರಳಿ ಕರೆ ಮಾಡಿ.</Say>
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
                        {"digit": "1", "label": "Electrician (ಎಲೆಕ್ಟ್ರಿಷಿಯನ್)"},
                        {"digit": "2", "label": "Plumber (ಪ್ಲಂಬರ್)"},
                        {"digit": "3", "label": "Mason (ಮೇಸ್ತ್ರಿ)"},
                        {"digit": "4", "label": "Carpenter (ಬಡಗಿ)"},
                        {"digit": "5", "label": "Painter (ಪೇಂಟರ್)"},
                        {"digit": "6", "label": "Helper (ಕೂಲಿ ಕಾರ್ಮಿಕ)"},
                        {"digit": "7", "label": "Welder (ವೆಲ್ಡರ್)"}
                    ]
                }

            if is_jobs:
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
    <Say language="kn-IN">{msg_kn}</Say>
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

            if is_wage:
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
    <Say language="kn-IN">{msg_kn}</Say>
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
        # Step 2: Trade Chosen (via voice speech or DTMF digit) -> Prompt Experience
        # -------------------------------------------------------------
        if step == "reg_trade":
            selected_trade = cls.resolve_trade(digits, speech)
            draft["trade"] = selected_trade["trade"]
            draft["trade_kn"] = selected_trade["kn"]
            draft["trade_hi"] = selected_trade["hi"]

            cls.update_call_session(call_sid, "reg_exp", "bilingual", draft)

            prompt_kn = (
                f"ಆಯ್ಕೆ ಮಾಡಿದ ವೃತ್ತಿ: {selected_trade['kn']}. "
                "ನಿಮ್ಮ ಕೆಲಸದ ಅನುಭವದ ವರ್ಷಗಳನ್ನು ಮಾತನಾಡಿ ಅಥವಾ ಸಂಖ್ಯೆ ಒತ್ತಿ: 1 ವರ್ಷಕ್ಕೆ 1, 2 ವರ್ಷಕ್ಕೆ 2, 3 ವರ್ಷಕ್ಕೆ 3, 4 ವರ್ಷಕ್ಕೆ 4, 5 ಅಥವಾ ಹೆಚ್ಚಿನ ವರ್ಷಕ್ಕೆ 5."
            )
            prompt_hi = (
                f"चुना गया व्यवसाय: {selected_trade['hi']}। "
                "अपने अनुभव के वर्ष बोलें या संख्या दबाएं: 1 वर्ष के लिए 1, 2 वर्ष के लिए 2, 3 वर्ष के लिए 3, 4 वर्ष के लिए 4, 5 या अधिक वर्ष के लिए 5।"
            )

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech dtmf" numDigits="1" speechTimeout="auto" action="{action_url}" method="POST" timeout="12">
        <Say language="kn-IN">{prompt_kn}</Say>
        <Say language="hi-IN" voice="Polly.Aditi">{prompt_hi}</Say>
    </Gather>
    <Say language="kn-IN">ಸಮಯ ಮೀರಿದೆ. ದಯವಿಟ್ಟು ಮರಳಿ ಕರೆ ಮಾಡಿ.</Say>
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
                    {"digit": "1", "label": "1 Year (1 ವರ್ಷ)"},
                    {"digit": "2", "label": "2 Years (2 ವರ್ಷ)"},
                    {"digit": "3", "label": "3 Years (3 ವರ್ಷ)"},
                    {"digit": "4", "label": "4 Years (4 ವರ್ಷ)"},
                    {"digit": "5", "label": "5+ Years (5 ಅಥವಾ ಹೆಚ್ಚಿನ ವರ್ಷ)"}
                ]
            }

        # -------------------------------------------------------------
        # Step 3: Experience Chosen -> Prompt Location (via voice speech or DTMF)
        # -------------------------------------------------------------
        if step == "reg_exp":
            exp_val = cls.resolve_experience(digits, speech)
            draft["experience_years"] = exp_val

            cls.update_call_session(call_sid, "reg_city", "bilingual", draft)

            prompt_kn = (
                f"{exp_val} ವರ್ಷಗಳ ಅನುಭವ ದಾಖಲಾಗಿದೆ. "
                "ನಿಮ್ಮ ನಗರ ಅಥವಾ ಸ್ಥಳದ ಹೆಸರನ್ನು ನೇರವಾಗಿ ಮಾತನಾಡಿ, "
                "ಅಥವಾ ಸಂಖ್ಯೆ ಒತ್ತಿ: 1 ಬೆಂಗಳೂರು, 2 ಮೈಸೂರು, 3 ಹುಬ್ಬಳ್ಳಿ, 4 ಬೆಳಗಾವಿ, 5 ಮಂಗಳೂರು, 6 ಕಲಬುರಗಿ, 7 ದೆಹಲಿ, 8 ಹಾಸನ ಅಥವಾ ಇತರ ಜಿಲ್ಲೆ."
            )
            prompt_hi = (
                f"{exp_val} वर्ष का अनुभव दर्ज हुआ। "
                "अपने शहर या स्थान का नाम सीधे बोलें, "
                "या संख्या दबाएं: 1 बेंगलुरु, 2 मैसूर, 3 हुबली, 4 बेलगाम, 5 मंगलुरु, 6 कलबुर्गी, 7 दिल्ली, 8 हासन या अन्य जिला।"
            )

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech dtmf" numDigits="1" speechTimeout="auto" action="{action_url}" method="POST" timeout="14">
        <Say language="kn-IN">{prompt_kn}</Say>
        <Say language="hi-IN" voice="Polly.Aditi">{prompt_hi}</Say>
    </Gather>
    <Say language="kn-IN">ಸಮಯ ಮೀರಿದೆ. ದಯವಿಟ್ಟು ಮರಳಿ ಕರೆ ಮಾಡಿ.</Say>
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
                    {"digit": "1", "label": "Bengaluru (ಬೆಂಗಳೂರು)"},
                    {"digit": "2", "label": "Mysuru (ಮೈಸೂರು)"},
                    {"digit": "3", "label": "Hubballi (ಹುಬ್ಬಳ್ಳಿ)"},
                    {"digit": "4", "label": "Belagavi (ಬೆಳಗಾವಿ)"},
                    {"digit": "5", "label": "Mangaluru (ಮಂಗಳೂರು)"},
                    {"digit": "6", "label": "Kalaburagi (ಕಲಬುರಗಿ)"},
                    {"digit": "7", "label": "Delhi (ದೆಹಲಿ)"},
                    {"digit": "8", "label": "Hassan / Other (ಹಾಸನ ಅಥವಾ ಇತರ)"}
                ]
            }

        # -------------------------------------------------------------
        # Step 4: Location Chosen (via voice speech or DTMF) -> Finalize Registration
        # -------------------------------------------------------------
        if step == "reg_city":
            selected_city = cls.resolve_location(digits, speech)
            city_name = selected_city["city"]
            city_kn = selected_city["kn"]
            city_hi = selected_city["hi"]

            trade = draft.get("trade", "Helper")
            trade_kn = draft.get("trade_kn", trade)
            trade_hi = draft.get("trade_hi", trade)
            exp = draft.get("experience_years", 2)

            # Automatically compute fair wage for their exact trade, location, and experience
            pred = FairWageService.predict_fair_wage(trade=trade, city=city_name, experience_years=exp)
            rec_wage = float(pred.get("recommended_daily_wage", 750.0))

            worker_name = f"{trade} Worker {phone[-4:]}" if len(phone) >= 4 else f"{trade} Worker"

            # Create Worker Record in DB
            WorkerService.create_worker(WorkerCreate(
                name=worker_name,
                phone=phone,
                trade=trade,
                experience_years=exp,
                daily_rate=rec_wage,
                city=city_name,
                language_pref="kannada",
                source="ivr"
            ))

            # Auto-create User account so worker can log into dashboard
            try:
                from app.services.auth_service import AuthService
                existing_user = AuthService.get_user_by_username_or_phone(phone)
                if not existing_user:
                    user_login = f"worker_{phone[-4:]}" if len(phone) >= 4 else "worker_ivr"
                    AuthService.register_user(
                        username=user_login,
                        phone=phone,
                        password="password123",
                        role="worker",
                        full_name=worker_name,
                        city=city_name,
                        trade=trade,
                        experience_years=exp,
                        daily_rate=rec_wage
                    )
            except Exception as e:
                logger.warning("Could not auto-create web user for IVR worker: %s", e)

            cls.delete_call_session(call_sid)

            msg_kn = (
                f"ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಕಾಯಕಸೇತು ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ಯಶಸ್ವಿಯಾಗಿ ನೋಂದಾಯಿಸಲಾಗಿದೆ. "
                f"ವೃತ್ತಿ: {trade_kn}, ಅನುಭವ: {exp} ವರ್ಷ, ಸ್ಥಳ: {city_kn}. "
                f"ಶಿಫಾರಸು ಮಾಡಿದ ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ₹{int(rec_wage)}. "
                f"ಉದ್ಯೋಗದಾತರು ಶೀಘ್ರದಲ್ಲೇ ಸಂಪರ್ಕಿಸುತ್ತಾರೆ."
            )
            msg_hi = (
                f"धन्यवाद! आपका श्रमसेतु श्रमिक प्रोफ़ाइल सफलतापूर्वक पंजीकृत हो गया है। "
                f"व्यवसाय: {trade_hi}, अनुभव: {exp} वर्ष, स्थान: {city_hi}। "
                f"अनुशंसित उचित दैनिक मजदूरी ₹{int(rec_wage)} है। "
                f"नियोक्ता आपसे जल्द संपर्क करेंगे।"
            )

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN">{msg_kn}</Say>
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
        # Fallback: Invalid Key / Speech
        # -------------------------------------------------------------
        cls.delete_call_session(call_sid)
        msg_kn = "ತಪ್ಪಾದ ಸಂಖ್ಯೆ ಅಥವಾ ಧ್ವನಿ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. ದಯವಿಟ್ಟು ಮರಳಿ ಕರೆ ಮಾಡಿ."
        msg_hi = "गलत इनपुट प्राप्त हुआ। कृपया दोबारा कॉल करें।"

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN">{msg_kn}</Say>
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


# Alias for backwards compatibility
TelecomService = IVRService
