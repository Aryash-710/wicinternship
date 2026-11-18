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
    "painter": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "ಪೇಂಟರ್"},
    "paint": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "ಪೇಂಟರ್"},
    "color": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "ಪೇಂಟರ್"},
    "ಪೇಂಟರ್": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "ಬಣ್ಣ": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "पेंटर": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "रंगाई": {"trade": "Painter", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},

    # Helper
    "helper": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "labour": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "coolie": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "hamali": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर"},
    "ಕೂಲಿ": {"trade": "Helper", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मಜದೂರ"},
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
    Asks the user for language preference (Kannada or Hindi) at the start of the call,
    and conducts all subsequent steps strictly in the user's chosen language.
    Supports Speech Voice input and DTMF keypad tones for occupation, experience, and location.
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
                VALUES (?, ?, 'ivr', 'lang_select', 'pending', '{}')
            """, (call_sid, phone))
            return {
                "call_sid": call_sid,
                "phone_number": phone,
                "current_step": "lang_select",
                "language": "pending",
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
        d = (digits or "").strip()
        if d in TRADE_OPTIONS:
            return TRADE_OPTIONS[d]

        s = (speech or "").strip().lower()
        if s:
            for kw, meta in TRADE_KEYWORDS.items():
                if kw in s:
                    return meta
            spoken = speech.strip().title()
            return {"trade": spoken, "kn": spoken, "hi": spoken}

        return TRADE_OPTIONS["1"]

    @staticmethod
    def resolve_experience(digits: Optional[str], speech: Optional[str]) -> int:
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
    def _build_response(
        cls,
        call_sid: str,
        prompt: str,
        language: str,
        action: str = "gather",
        options: Optional[List[Dict[str, str]]] = None,
        action_url: str = "/api/v1/telecom/ivr/twiml"
    ) -> Dict[str, Any]:
        """
        Builds TwiML XML and response payload in the user's chosen language.
        """
        opts = options or []
        if language == "hindi":
            voice_tag = f'<Say language="hi-IN" voice="Polly.Aditi">{prompt}</Say>'
        elif language == "kannada":
            voice_tag = f'<Say language="kn-IN">{prompt}</Say>'
        else:
            # Bilingual for initial language selection greeting
            kn_part = "ನಮಸ್ಕಾರ, ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ. ಕನ್ನಡಕ್ಕಾಗಿ 1 ಒತ್ತಿ."
            hi_part = "नमस्कार, श्रमसेतु में आपका स्वागत है। हिन्दी के लिए 2 दबाएं।"
            voice_tag = f'<Say language="kn-IN">{kn_part}</Say>\n        <Say language="hi-IN" voice="Polly.Aditi">{hi_part}</Say>'

        if action == "gather":
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech dtmf" numDigits="1" speechTimeout="auto" action="{action_url}" method="POST" timeout="12">
        {voice_tag}
    </Gather>
    <Say language="{'hi-IN' if language == 'hindi' else 'kn-IN'}">{'समय समाप्त हो गया है।' if language == 'hindi' else 'ಸಮಯ ಮೀರಿದೆ. ಧನ್ಯವಾದಗಳು.'}</Say>
    <Hangup/>
</Response>"""
        else:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    {voice_tag}
    <Hangup/>
</Response>"""

        return {
            "call_sid": call_sid,
            "twiml_xml": twiml,
            "prompt_text": prompt,
            "prompt_audio_text": prompt,
            "language": language,
            "action": action,
            "options": opts
        }

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
        Step 0: Asks user to select language: 1 for Kannada, 2 for Hindi.
        Subsequent Steps: Proceeds 100% in the chosen language.
        """
        digits = (digits or "").strip()
        speech = (speech_result or "").strip()
        phone = (phone or "").strip() or "9845000000"

        session = cls.get_or_create_call_session(call_sid, phone)
        step = session.get("current_step", "lang_select")
        lang = session.get("language", "pending")
        draft = session.get("draft", {})

        # -------------------------------------------------------------
        # Step 0: Initial Call Connection -> Ask for Language Selection
        # -------------------------------------------------------------
        if not digits and not speech:
            cls.update_call_session(call_sid, "lang_select", "pending", {})
            greeting_prompt = (
                "[ಕನ್ನಡ]: ನಮಸ್ಕಾರ, ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ. ಕನ್ನಡಕ್ಕಾಗಿ 1 ಒತ್ತಿ.\n"
                "[हिन्दी]: नमस्कार, श्रमसेतु में आपका स्वागत है। हिन्दी के लिए 2 दबाएं।"
            )
            return cls._build_response(
                call_sid=call_sid,
                prompt=greeting_prompt,
                language="bilingual",
                action="gather",
                options=[
                    {"digit": "1", "label": "ಕನ್ನಡ (Kannada - Press 1)"},
                    {"digit": "2", "label": "हिन्दी (Hindi - Press 2)"}
                ],
                action_url=action_url
            )

        # -------------------------------------------------------------
        # Step 1: Language Selection Received -> Store language and show Main Menu
        # -------------------------------------------------------------
        if step in ("lang_select", "welcome") or lang == "pending":
            speech_lower = speech.lower()
            if digits == "2" or any(k in speech_lower for k in ("hindi", "हिन्दी", "हिंदी", "दो")):
                chosen_lang = "hindi"
            elif digits == "1" or any(k in speech_lower for k in ("kannada", "ಕನ್ನಡ", "ಒಂದು")):
                chosen_lang = "kannada"
            else:
                chosen_lang = "kannada"

            cls.update_call_session(call_sid, "menu", chosen_lang, {})

            if chosen_lang == "hindi":
                menu_prompt = (
                    "श्रमसेतु में आपका स्वागत है।\n"
                    "1: श्रमिक प्रोफ़ाइल दर्ज करने के लिए 1 दबाएं।\n"
                    "2: आज के नए काम सुनने के लिए 2 दबाएं।\n"
                    "3: उचित दैनिक मजदूरी दर जानने के लिए 3 दबाएं।"
                )
                options = [
                    {"digit": "1", "label": "श्रमिक पंजीकरण (Register Profile)"},
                    {"digit": "2", "label": "नए काम खोजें (Find Jobs)"},
                    {"digit": "3", "label": "दैनिक मजदूरी दर जांचें (Check Daily Wage)"}
                ]
            else:
                menu_prompt = (
                    "ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ.\n"
                    "1: ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ನೋಂದಾಯಿಸಲು 1 ಒತ್ತಿ.\n"
                    "2: ಇಂದಿನ ಹೊಸ ಕೆಲಸಗಳ ಮಾಹಿತಿ ಕೇಳಲು 2 ಒತ್ತಿ.\n"
                    "3: ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ದರ ತಿಳಿಯಲು 3 ಒತ್ತಿ."
                )
                options = [
                    {"digit": "1", "label": "ಕಾರ್ಮಿಕ ನೋಂದಣಿ (Register Profile)"},
                    {"digit": "2", "label": "ಹೊಸ ಕೆಲಸಗಳು (Find Jobs)"},
                    {"digit": "3", "label": "ದಿನಗೂಲಿ ದರ ಪರಿಶೀಲನೆ (Check Daily Wage)"}
                ]

            return cls._build_response(
                call_sid=call_sid,
                prompt=menu_prompt,
                language=chosen_lang,
                action="gather",
                options=options,
                action_url=action_url
            )

        # -------------------------------------------------------------
        # Step 2: Main Menu Option Selected (Register, Jobs, or Fair Wage)
        # -------------------------------------------------------------
        if step == "menu":
            speech_lower = speech.lower()
            is_reg = digits == "1" or any(k in speech_lower for k in ("ನೋಂದಣಿ", "पंजीकरण", "register", "profile"))
            is_jobs = digits == "2" or any(k in speech_lower for k in ("ಕೆಲಸ", "काम", "job", "work"))
            is_wage = digits == "3" or any(k in speech_lower for k in ("ದಿನಗೂಲಿ", "मजदूरी", "wage", "rate"))

            # Option 1: Worker Registration
            if is_reg:
                existing = WorkerService.get_worker_by_phone(phone)
                if existing:
                    cls.delete_call_session(call_sid)
                    if lang == "hindi":
                        msg = (
                            f"नमस्ते! आपका मोबाइल नंबर श्रमसेतु पर पहले से पंजीकृत है। "
                            f"नाम: {existing['name']}, व्यवसाय: {existing['trade']}, शहर: {existing['city']}."
                        )
                    else:
                        msg = (
                            f"ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಕಾಯಕಸೇತುವಿನಲ್ಲಿ ಮೊದಲೇ ನೋಂದಾಯಿತವಾಗಿದೆ. "
                            f"ಹೆಸರು: {existing['name']}. ವೃತ್ತಿ: {existing['trade']}. ಸ್ಥಳ: {existing['city']}."
                        )
                    return cls._build_response(call_sid, msg, lang, action="hangup", action_url=action_url)

                cls.update_call_session(call_sid, "reg_trade", lang, {})
                if lang == "hindi":
                    prompt = (
                        "श्रमिक पंजीकरण में आपका स्वागत है। अपने व्यवसाय का नाम सीधे बोलें, "
                        "या नंबर दबाएं: 1 इलेक्ट्रीशियन, 2 प्लंबर, 3 राजमिस्त्री, 4 बढ़ई, 5 पेंटर, 6 मजदूर, 7 वेल्डर।"
                    )
                    options = [
                        {"digit": "1", "label": "इलेक्ट्रीशियन (Electrician)"},
                        {"digit": "2", "label": "प्लंबर (Plumber)"},
                        {"digit": "3", "label": "राजमिस्त्री (Mason)"},
                        {"digit": "4", "label": "बढ़ई (Carpenter)"},
                        {"digit": "5", "label": "पेंटर (Painter)"},
                        {"digit": "6", "label": "मजदूर (Helper)"},
                        {"digit": "7", "label": "वेल्डर (Welder)"}
                    ]
                else:
                    prompt = (
                        "ಕಾರ್ಮಿಕ ನೋಂದಣಿಗೆ ಸ್ವಾಗತ. ನಿಮ್ಮ ವೃತ್ತಿಯ ಹೆಸರನ್ನು ನೇರವಾಗಿ ಮಾತನಾಡಿ, "
                        "ಅಥವಾ ಕೀಲಿಮಣೆಯಲ್ಲಿ ಒತ್ತಿ: 1 ಎಲೆಕ್ಟ್ರಿಷಿಯನ್, 2 ಪ್ಲಂಬರ್, 3 ಮೇಸ್ತ್ರಿ, 4 ಬಡಗಿ, 5 ಪೇಂಟರ್, 6 ಕೂಲಿ ಕಾರ್ಮಿಕ, 7 ವೆಲ್ಡರ್."
                    )
                    options = [
                        {"digit": "1", "label": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್ (Electrician)"},
                        {"digit": "2", "label": "ಪ್ಲಂಬರ್ (Plumber)"},
                        {"digit": "3", "label": "ಮೇಸ್ತ್ರಿ (Mason)"},
                        {"digit": "4", "label": "ಬಡಗಿ (Carpenter)"},
                        {"digit": "5", "label": "ಪೇಂಟರ್ (Painter)"},
                        {"digit": "6", "label": "ಕೂಲಿ ಕಾರ್ಮಿಕ (Helper)"},
                        {"digit": "7", "label": "ವೆಲ್ಡರ್ (Welder)"}
                    ]
                return cls._build_response(call_sid, prompt, lang, action="gather", options=options, action_url=action_url)

            # Option 2: Find Jobs
            if is_jobs:
                cls.delete_call_session(call_sid)
                jobs = JobService.list_jobs(status="open", limit=2)
                if jobs:
                    j1 = jobs[0]
                    area = j1.get("area") or j1.get("city") or ("शहर" if lang == "hindi" else "ನಗರ")
                    phone_num = j1.get("employer_phone", "9845011223")
                    if lang == "hindi":
                        msg = f"आज का काम: {j1['title']}, क्षेत्र: {area}, दैनिक मजदूरी ₹{j1['wage_offered']:.0f}. संपर्क नंबर {phone_num}."
                    else:
                        msg = f"ಇಂದಿನ ಕೆಲಸ: {j1['title']}, ಪ್ರದೇಶ: {area}, ದಿನಗೂಲಿ ₹{j1['wage_offered']:.0f}. ಸಂಪರ್ಕ ಸಂಖ್ಯೆ {phone_num}."
                else:
                    msg = "फिलहाल कोई नया काम उपलब्ध नहीं है। कृपया थोड़ी देर बाद फिर से कॉल करें।" if lang == "hindi" else "ಸದ್ಯಕ್ಕೆ ಹೊಸ ಕೆಲಸಗಳು ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಮಯದ ನಂತರ ಮರಳಿ ಕರೆ ಮಾಡಿ."

                return cls._build_response(call_sid, msg, lang, action="hangup", action_url=action_url)

            # Option 3: Fair Wage Calculator
            if is_wage:
                cls.delete_call_session(call_sid)
                pred = FairWageService.predict_fair_wage(trade="Electrician", city="Bengaluru", experience_years=4)
                rec_rate = pred.get("recommended_daily_wage", 850.0)
                wage_min = pred.get("fair_wage_min", 750.0)
                wage_max = pred.get("fair_wage_max", 950.0)

                if lang == "hindi":
                    msg = (
                        f"बेंगलुरु में इलेक्ट्रीशियन काम के लिए अनुशंसित उचित दैनिक मजदूरी ₹{rec_rate:.0f} है। "
                        f"उचित दायरा ₹{wage_min:.0f} से ₹{wage_max:.0f} प्रति दिन।"
                    )
                else:
                    msg = (
                        f"ಬೆಂಗಳೂರಿನಲ್ಲಿ ಎಲೆಕ್ಟ್ರಿಷಿಯನ್ ಕೆಲಸಕ್ಕೆ ಶಿಫಾರಸು ಮಾಡಿದ ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ₹{rec_rate:.0f}. "
                        f"ದರ ಶ್ರೇಣಿ ₹{wage_min:.0f} ರಿಂದ ₹{wage_max:.0f} ಪ್ರತಿ ದಿನಕ್ಕೆ."
                    )
                return cls._build_response(call_sid, msg, lang, action="hangup", action_url=action_url)

        # -------------------------------------------------------------
        # Step 3: Occupation Input Received -> Prompt Experience in chosen language
        # -------------------------------------------------------------
        if step == "reg_trade":
            selected_trade = cls.resolve_trade(digits, speech)
            trade_display = selected_trade["hi"] if lang == "hindi" else selected_trade["kn"]
            draft["trade"] = selected_trade["trade"]
            draft["trade_display"] = trade_display

            cls.update_call_session(call_sid, "reg_exp", lang, draft)

            if lang == "hindi":
                prompt = (
                    f"चुना गया व्यवसाय: {trade_display}। "
                    "अपने अनुभव के वर्ष बोलें या संख्या दबाएं: 1 वर्ष के लिए 1, 2 वर्ष के लिए 2, 3 वर्ष के लिए 3, 4 वर्ष के लिए 4, 5 या अधिक वर्ष के लिए 5।"
                )
                options = [
                    {"digit": "1", "label": "1 वर्ष (1 Year)"},
                    {"digit": "2", "label": "2 वर्ष (2 Years)"},
                    {"digit": "3", "label": "3 वर्ष (3 Years)"},
                    {"digit": "4", "label": "4 वर्ष (4 Years)"},
                    {"digit": "5", "label": "5+ वर्ष (5+ Years)"}
                ]
            else:
                prompt = (
                    f"ಆಯ್ಕೆ ಮಾಡಿದ ವೃತ್ತಿ: {trade_display}. "
                    "ನಿಮ್ಮ ಕೆಲಸದ ಅನುಭವದ ವರ್ಷಗಳನ್ನು ಮಾತನಾಡಿ ಅಥವಾ ಸಂಖ್ಯೆ ಒತ್ತಿ: 1 ವರ್ಷಕ್ಕೆ 1, 2 ವರ್ಷಕ್ಕೆ 2, 3 ವರ್ಷಕ್ಕೆ 3, 4 ವರ್ಷಕ್ಕೆ 4, 5 ಅಥವಾ ಹೆಚ್ಚಿನ ವರ್ಷಕ್ಕೆ 5."
                )
                options = [
                    {"digit": "1", "label": "1 ವರ್ಷ (1 Year)"},
                    {"digit": "2", "label": "2 ವರ್ಷ (2 Years)"},
                    {"digit": "3", "label": "3 ವರ್ಷ (3 Years)"},
                    {"digit": "4", "label": "4 ವರ್ಷ (4 Years)"},
                    {"digit": "5", "label": "5+ ವರ್ಷ (5+ Years)"}
                ]
            return cls._build_response(call_sid, prompt, lang, action="gather", options=options, action_url=action_url)

        # -------------------------------------------------------------
        # Step 4: Experience Input Received -> Prompt Location in chosen language
        # -------------------------------------------------------------
        if step == "reg_exp":
            exp_val = cls.resolve_experience(digits, speech)
            draft["experience_years"] = exp_val

            cls.update_call_session(call_sid, "reg_city", lang, draft)

            if lang == "hindi":
                prompt = (
                    f"{exp_val} वर्ष का अनुभव दर्ज हुआ। "
                    "अपने शहर या स्थान का नाम सीधे बोलें, "
                    "या संख्या दबाएं: 1 बेंगलुरु, 2 मैसूर, 3 हुबली, 4 बेलगाम, 5 मंगलुरु, 6 कलबुर्गी, 7 दिल्ली, 8 अन्य जिला।"
                )
                options = [
                    {"digit": "1", "label": "बेंगलुरु (Bengaluru)"},
                    {"digit": "2", "label": "मैसूर (Mysuru)"},
                    {"digit": "3", "label": "हुबली (Hubballi)"},
                    {"digit": "4", "label": "बेलगाम (Belagavi)"},
                    {"digit": "5", "label": "मंगलुरु (Mangaluru)"},
                    {"digit": "6", "label": "कलबुर्गी (Kalaburagi)"},
                    {"digit": "7", "label": "दिल्ली (Delhi)"},
                    {"digit": "8", "label": "अन्य जिला (Other)"}
                ]
            else:
                prompt = (
                    f"{exp_val} ವರ್ಷಗಳ ಅನುಭವ ದಾಖಲಾಗಿದೆ. "
                    "ನಿಮ್ಮ ನಗರ ಅಥವಾ ಸ್ಥಳದ ಹೆಸರನ್ನು ನೇರವಾಗಿ ಮಾತನಾಡಿ, "
                    "ಅಥವಾ ಸಂಖ್ಯೆ ಒತ್ತಿ: 1 ಬೆಂಗಳೂರು, 2 ಮೈಸೂರು, 3 ಹುಬ್ಬಳ್ಳಿ, 4 ಬೆಳಗಾವಿ, 5 ಮಂಗಳೂರು, 6 ಕಲಬುರಗಿ, 7 ದೆಹಲಿ, 8 ಹಾಸನ ಅಥವಾ ಇತರ ಜಿಲ್ಲೆ."
                )
                options = [
                    {"digit": "1", "label": "ಬೆಂಗಳೂರು (Bengaluru)"},
                    {"digit": "2", "label": "ಮೈಸೂರು (Mysuru)"},
                    {"digit": "3", "label": "ಹುಬ್ಬಳ್ಳಿ (Hubballi)"},
                    {"digit": "4", "label": "ಬೆಳಗಾವಿ (Belagavi)"},
                    {"digit": "5", "label": "ಮಂಗಳೂರು (Mangaluru)"},
                    {"digit": "6", "label": "ಕಲಬುರಗಿ (Kalaburagi)"},
                    {"digit": "7", "label": "ದೆಹಲಿ (Delhi)"},
                    {"digit": "8", "label": "ಹಾಸನ ಅಥವಾ ಇತರ (Hassan/Other)"}
                ]
            return cls._build_response(call_sid, prompt, lang, action="gather", options=options, action_url=action_url)

        # -------------------------------------------------------------
        # Step 5: Location Input Received -> Finalize Registration in chosen language
        # -------------------------------------------------------------
        if step == "reg_city":
            selected_city = cls.resolve_location(digits, speech)
            city_name = selected_city["city"]
            city_display = selected_city.get("hi" if lang == "hindi" else "kn", city_name)

            trade = draft.get("trade", "Helper")
            trade_display = draft.get("trade_display", trade)
            exp = draft.get("experience_years", 2)

            # Auto-calculate fair wage for their exact trade, location, and experience
            pred = FairWageService.predict_fair_wage(trade=trade, city=city_name, experience_years=exp)
            rec_wage = float(pred.get("recommended_daily_wage", 750.0))

            worker_name = f"{trade} Worker {phone[-4:]}" if len(phone) >= 4 else f"{trade} Worker"

            # Create Worker Record in DB with user's selected language
            WorkerService.create_worker(WorkerCreate(
                name=worker_name,
                phone=phone,
                trade=trade,
                experience_years=exp,
                daily_rate=rec_wage,
                city=city_name,
                language_pref=lang,
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

            if lang == "hindi":
                msg = (
                    f"धन्यवाद! आपका श्रमसेतु श्रमिक प्रोफ़ाइल सफलतापूर्वक पंजीकृत हो गया है। "
                    f"व्यवसाय: {trade_display}, अनुभव: {exp} वर्ष, स्थान: {city_display}। "
                    f"अनुशंसित उचित दैनिक मजदूरी ₹{int(rec_wage)} है। "
                    f"नियोक्ता आपसे जल्द संपर्क करेंगे।"
                )
            else:
                msg = (
                    f"ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಕಾಯಕಸೇತು ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ಯಶಸ್ವಿಯಾಗಿ ನೋಂದಾಯಿಸಲಾಗಿದೆ. "
                    f"ವೃತ್ತಿ: {trade_display}, ಅನುಭವ: {exp} ವರ್ಷ, ಸ್ಥಳ: {city_display}. "
                    f"ಶಿಫಾರಸು ಮಾಡಿದ ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ₹{int(rec_wage)}. "
                    f"ಉದ್ಯೋಗದಾತರು ಶೀಘ್ರದಲ್ಲೇ ಸಂಪರ್ಕಿಸುತ್ತಾರೆ."
                )

            return cls._build_response(call_sid, msg, lang, action="hangup", action_url=action_url)

        # -------------------------------------------------------------
        # Fallback
        # -------------------------------------------------------------
        cls.delete_call_session(call_sid)
        fallback_msg = "गलत इनपुट प्राप्त हुआ। कृपया दोबारा कॉल करें।" if lang == "hindi" else "ತಪ್ಪಾದ ಸಂಖ್ಯೆ ಅಥವಾ ಧ್ವನಿ ಸ್ವೀಕರಿಸಲಾಗಿದೆ. ದಯವಿಟ್ಟು ಮರಳಿ ಕರೆ ಮಾಡಿ."
        return cls._build_response(call_sid, fallback_msg, lang, action="hangup", action_url=action_url)


# Alias for backwards compatibility
TelecomService = IVRService
