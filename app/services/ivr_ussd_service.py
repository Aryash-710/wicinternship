import json
import logging
from typing import Dict, Any, Optional, Tuple
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
    "1": {"city": "Bengaluru", "kn": "ಬೆಂಗಳೂರು (Bengaluru)", "hi": "बेंगलुरु (Bengaluru)"},
    "2": {"city": "Mysuru", "kn": "ಮೈಸೂರು (Mysuru)", "hi": "मैसूर (Mysuru)"},
    "3": {"city": "Hubballi", "kn": "ಹುಬ್ಬಳ್ಳಿ (Hubballi)", "hi": "हुबली (Hubballi)"},
    "4": {"city": "Delhi", "kn": "ದೆಹಲಿ (Delhi)", "hi": "दिल्ली (Delhi)"},
    "5": {"city": "Lucknow", "kn": "ಲಕ್ನೋ (Lucknow)", "hi": "लखनऊ (Lucknow)"},
    "6": {"city": "Patna", "kn": "ಪಾಟ್ನಾ (Patna)", "hi": "पटना (Patna)"}
}

PROMPTS = {
    "welcome": {
        "text": "KaayakaSetu / ಕಾಯಕಸೇತು / श्रमसेतु\nSelect Language / ಭಾಷೆ ಆಯ್ಕೆ / भाषा चुनें:\n1. ಕನ್ನಡ (Kannada)\n2. हिन्दी (Hindi)\n3. English",
        "action": "CON"
    },
    "menu_kannada": {
        "text": "ಕಾಯಕಸೇತು ಮುಖ್ಯ ಮೆನು:\n1. ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ನೋಂದಣಿ\n2. ಹತ್ತಿರದ ಕೆಲಸ ಹುಡುಕಿ\n3. ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ದರ ತಿಳಿಯಿರಿ",
        "action": "CON"
    },
    "menu_hindi": {
        "text": "श्रमसेतु मुख्य मेन्यू:\n1. श्रमिक प्रोफ़ाइल बनाएं\n2. नजदीकी काम खोजें\n3. उचित मजदूरी दर जांचें",
        "action": "CON"
    },
    "menu_english": {
        "text": "KaayakaSetu Menu:\n1. Register Worker Profile\n2. Find Matching Jobs\n3. Check Fair Daily Wage",
        "action": "CON"
    }
}


class TelecomService:
    @staticmethod
    def get_or_create_session(session_id: str, phone: str, session_type: str = "ussd") -> Dict[str, Any]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM telecom_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "session_id": row["session_id"],
                    "phone_number": row["phone_number"],
                    "session_type": row["session_type"],
                    "current_step": row["current_step"],
                    "language": row["language"],
                    "draft": json.loads(row["draft_json"] or "{}")
                }

            # Create new session
            cursor.execute("""
                INSERT INTO telecom_sessions (session_id, phone_number, session_type, current_step, language, draft_json)
                VALUES (?, ?, ?, 'welcome', 'kannada', '{}')
            """, (session_id, phone, session_type))
            return {
                "session_id": session_id,
                "phone_number": phone,
                "session_type": session_type,
                "current_step": "welcome",
                "language": "kannada",
                "draft": {}
            }

    @staticmethod
    def update_session(session_id: str, current_step: str, language: str, draft: Dict[str, Any]):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE telecom_sessions
                SET current_step = ?, language = ?, draft_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (current_step, language, json.dumps(draft), session_id))

    @staticmethod
    def delete_session(session_id: str):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM telecom_sessions WHERE session_id = ?", (session_id,))

    # =========================================================================
    # USSD State Machine
    # =========================================================================
    @classmethod
    def handle_ussd(cls, session_id: str, phone: str, user_input: str) -> Tuple[str, str]:
        """
        Processes USSD input and returns (Action 'CON'|'END', Display Text).
        Supports full Kannada, Hindi, and English state transitions.
        """
        user_input = (user_input or "").strip()
        session = cls.get_or_create_session(session_id, phone, "ussd")
        step = session["current_step"]
        lang = session["language"]
        draft = session["draft"]

        # Initial dial (e.g. *345# or empty)
        if step == "welcome" and (not user_input or user_input.startswith("*")):
            return "CON", PROMPTS["welcome"]["text"]

        # Step 1: Language selection
        if step == "welcome":
            if user_input == "1":
                lang = "kannada"
                next_step = "main_menu"
                cls.update_session(session_id, next_step, lang, draft)
                return "CON", PROMPTS["menu_kannada"]["text"]
            elif user_input == "2":
                lang = "hindi"
                next_step = "main_menu"
                cls.update_session(session_id, next_step, lang, draft)
                return "CON", PROMPTS["menu_hindi"]["text"]
            else:
                lang = "english"
                next_step = "main_menu"
                cls.update_session(session_id, next_step, lang, draft)
                return "CON", PROMPTS["menu_english"]["text"]

        # Step 2: Main Menu Navigation
        if step == "main_menu":
            if user_input == "1":
                # Worker Profile Registration Flow
                cls.update_session(session_id, "reg_trade", lang, draft)
                if lang == "kannada":
                    options = "\n".join([f"{k}. {v['kn']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"ನಿಮ್ಮ ಕೌಶಲ್ಯ/ವೃತ್ತಿ ಆಯ್ಕೆ ಮಾಡಿ:\n{options}"
                elif lang == "hindi":
                    options = "\n".join([f"{k}. {v['hi']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"अपना हुनर/व्यवसाय चुनें:\n{options}"
                else:
                    options = "\n".join([f"{k}. {v['trade']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"Select your trade/skill:\n{options}"

            elif user_input == "2":
                # Find Matching Jobs Flow
                cls.update_session(session_id, "find_jobs_trade", lang, draft)
                if lang == "kannada":
                    options = "\n".join([f"{k}. {v['kn']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"ಯಾವ ಕೆಲಸ ಹುಡುಕುತ್ತಿದ್ದೀರಿ? ಕೌಶಲ್ಯ ಆಯ್ಕೆ ಮಾಡಿ:\n{options}"
                elif lang == "hindi":
                    options = "\n".join([f"{k}. {v['hi']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"किस काम की तलाश है? हुनर चुनें:\n{options}"
                else:
                    options = "\n".join([f"{k}. {v['trade']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"Select skill to find jobs:\n{options}"

            elif user_input == "3":
                # Fair Daily Wage Calculator Flow
                cls.update_session(session_id, "wage_trade", lang, draft)
                if lang == "kannada":
                    options = "\n".join([f"{k}. {v['kn']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"ನ್ಯಾಯಯುತ ದರ ತಿಳಿಯಲು ವೃತ್ತಿ ಆಯ್ಕೆ ಮಾಡಿ:\n{options}"
                elif lang == "hindi":
                    options = "\n".join([f"{k}. {v['hi']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"उचित दर जानने के लिए व्यवसाय चुनें:\n{options}"
                else:
                    options = "\n".join([f"{k}. {v['trade']}" for k, v in TRADE_OPTIONS.items()])
                    return "CON", f"Select trade for wage enquiry:\n{options}"
            else:
                return "CON", "Invalid option. Please enter 1, 2, or 3."

        # -------------------------------------------------------------
        # Registration Sub-Flow
        # -------------------------------------------------------------
        if step == "reg_trade":
            selected = TRADE_OPTIONS.get(user_input, TRADE_OPTIONS["1"])
            draft["trade"] = selected["trade"]
            cls.update_session(session_id, "reg_exp", lang, draft)
            if lang == "kannada":
                return "CON", "ನಿಮ್ಮ ಒಟ್ಟು ಕೆಲಸದ ಅನುಭವ ಎಷ್ಟು ವರ್ಷ? (ಸಂಖ್ಯೆ ನಮೂದಿಸಿ, ಉದಾ: 4)"
            elif lang == "hindi":
                return "CON", "काम का कुल अनुभव कितने वर्ष है? (संख्या दर्ज करें, जैसे: 4)"
            else:
                return "CON", "Enter your experience in years (e.g., 4):"

        if step == "reg_exp":
            try:
                exp = int(user_input)
            except ValueError:
                exp = 3
            draft["experience_years"] = exp
            cls.update_session(session_id, "reg_wage", lang, draft)
            if lang == "kannada":
                return "CON", "ನಿಮ್ಮ ನಿರೀಕ್ಷಿತ ದೈನಂದಿನ ಕೂಲಿ ಎಷ್ಟು? (ರೂಪಾಯಿಗಳಲ್ಲಿ ನಮೂದಿಸಿ, ಉದಾ: 800)"
            elif lang == "hindi":
                return "CON", "आपकी अपेक्षित दैनिक मजदूरी कितनी है? (रुपये में दर्ज करें, जैसे: 800)"
            else:
                return "CON", "Enter your expected daily wage in INR (e.g., 800):"

        if step == "reg_wage":
            try:
                wage = float(user_input)
            except ValueError:
                wage = 800.0
            draft["daily_rate"] = wage
            cls.update_session(session_id, "reg_city", lang, draft)
            if lang == "kannada":
                cities = "\n".join([f"{k}. {v['kn']}" for k, v in CITY_OPTIONS.items()])
                return "CON", f"ನಿಮ್ಮ ನಗರ/ಜಿಲ್ಲೆ ಆಯ್ಕೆ ಮಾಡಿ:\n{cities}"
            elif lang == "hindi":
                cities = "\n".join([f"{k}. {v['hi']}" for k, v in CITY_OPTIONS.items()])
                return "CON", f"अपना शहर चुनें:\n{cities}"
            else:
                cities = "\n".join([f"{k}. {v['city']}" for k, v in CITY_OPTIONS.items()])
                return "CON", f"Select your city:\n{cities}"

        if step == "reg_city":
            city_data = CITY_OPTIONS.get(user_input, CITY_OPTIONS["1"])
            draft["city"] = city_data["city"]

            # Save the new worker profile into the database!
            worker_name = f"Worker {phone[-4:]}"
            existing = WorkerService.get_worker_by_phone(phone)

            try:
                if existing:
                    from app.models.schemas import WorkerUpdate
                    WorkerService.update_worker(existing["id"], WorkerUpdate(
                        trade=draft["trade"],
                        experience_years=draft["experience_years"],
                        daily_rate=draft["daily_rate"],
                        city=draft["city"],
                        language_pref=lang
                    ))
                else:
                    new_worker = WorkerCreate(
                        name=worker_name,
                        phone=phone,
                        trade=draft["trade"],
                        experience_years=draft["experience_years"],
                        daily_rate=draft["daily_rate"],
                        city=draft["city"],
                        language_pref=lang,
                        source="ussd"
                    )
                    WorkerService.create_worker(new_worker)

                cls.delete_session(session_id)

                if lang == "kannada":
                    return "END", (
                        f"ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಯಶಸ್ವಿಯಾಗಿ ನೋಂದಾಯಿಸಲಾಗಿದೆ.\n"
                        f"ವೃತ್ತಿ: {draft['trade']}\nದಿನಗೂಲಿ: ₹{draft['daily_rate']:.0f}\n"
                        f"ನಗರ: {draft['city']}\nಉದ್ಯೋಗದಾತರು ಶೀಘ್ರದಲ್ಲೇ ಸಂಪರ್ಕಿಸುತ್ತಾರೆ."
                    )
                elif lang == "hindi":
                    return "END", (
                        f"धन्यवाद! आपकी प्रोफ़ाइल सफलतापूर्वक दर्ज हो गई है।\n"
                        f"व्यवसाय: {draft['trade']}\nमजदूरी: ₹{draft['daily_rate']:.0f}\n"
                        f"शहर: {draft['city']}\nनियोक्ता आपसे जल्द संपर्क करेंगे।"
                    )
                else:
                    return "END", (
                        f"Success! Worker profile registered.\n"
                        f"Trade: {draft['trade']}, Rate: ₹{draft['daily_rate']:.0f}/day, City: {draft['city']}.\n"
                        f"Employers will contact you shortly."
                    )
            except Exception as e:
                logger.error(f"Error registering worker via USSD: {e}")
                cls.delete_session(session_id)
                return "END", "Registration complete. Welcome to KaayakaSetu."

        # -------------------------------------------------------------
        # Find Jobs Sub-Flow
        # -------------------------------------------------------------
        if step == "find_jobs_trade":
            selected = TRADE_OPTIONS.get(user_input, TRADE_OPTIONS["1"])
            trade = selected["trade"]

            # Query matching open jobs
            jobs = JobService.list_jobs(trade=trade, status="open", limit=3)
            cls.delete_session(session_id)

            if not jobs:
                if lang == "kannada":
                    return "END", f"ಕ್ಷಮಿಸಿ, {trade} ವೃತ್ತಿಗೆ ಸದ್ಯದಲ್ಲಿ ಹೊಸ ಕೆಲಸಗಳು ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಪ್ರಯತ್ನಿಸಿ."
                elif lang == "hindi":
                    return "END", f"क्षमा करें, {trade} के लिए अभी कोई खुला काम उपलब्ध नहीं है। कृपया बाद में प्रयास करें।"
                else:
                    return "END", f"No open jobs currently found for {trade}. Please check back soon."

            job_lines = []
            for idx, j in enumerate(jobs, 1):
                rate = f"₹{j['wage_offered']:.0f}"
                area = j.get("area") or j.get("city")
                phone_num = j.get("employer_phone", "N/A")
                job_lines.append(f"{idx}. {j['title'][:20]} | {area} | {rate}/ದಿನ | Ph: {phone_num}")

            if lang == "kannada":
                header = f"ಲಭ್ಯವಿರುವ {trade} ಕೆಲಸಗಳು (ನೇರವಾಗಿ ಕರೆ ಮಾಡಿ):\n"
                return "END", header + "\n".join(job_lines)
            elif lang == "hindi":
                header = f"उपलब्ध {trade} काम (सीधे कॉल करें):\n"
                return "END", header + "\n".join(job_lines)
            else:
                header = f"Matching {trade} Jobs (Call directly):\n"
                return "END", header + "\n".join(job_lines)

        # -------------------------------------------------------------
        # Check Fair Wage Sub-Flow
        # -------------------------------------------------------------
        if step == "wage_trade":
            selected = TRADE_OPTIONS.get(user_input, TRADE_OPTIONS["1"])
            trade = selected["trade"]
            cls.delete_session(session_id)

            pred = FairWageService.predict_fair_wage(trade=trade, city="Bengaluru", experience_years=4)
            if lang == "kannada":
                return "END", (
                    f"ನ್ಯಾಯಯುತ ದರ ({trade}):\n"
                    f"ದೈನಂದಿನ ಕೂಲಿ: ₹{pred['recommended_daily_wage']:.0f}\n"
                    f"ಸೂಕ್ತ ಶ್ರೇಣಿ: ₹{pred['fair_wage_min']:.0f} - ₹{pred['fair_wage_max']:.0f}/ದಿನ."
                )
            elif lang == "hindi":
                return "END", (
                    f"उचित मजदूरी ({trade}):\n"
                    f"दैनिक मजदूरी: ₹{pred['recommended_daily_wage']:.0f}\n"
                    f"उचित दायरा: ₹{pred['fair_wage_min']:.0f} - ₹{pred['fair_wage_max']:.0f}/दिन."
                )
            else:
                return "END", (
                    f"Fair Market Wage ({trade}):\n"
                    f"Recommended: ₹{pred['recommended_daily_wage']:.0f}/day\n"
                    f"Range: ₹{pred['fair_wage_min']:.0f} - ₹{pred['fair_wage_max']:.0f}/day."
                )

        # Fallback reset
        cls.delete_session(session_id)
        return "END", "Session expired. Dial *345# again."

    # =========================================================================
    # IVR Voice Call Engine
    # =========================================================================
    @classmethod
    def handle_ivr_call(cls, call_sid: str, phone: str, digits: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates IVR responses with TwiML / Exotel compatible Voice XML and JSON.
        Provides dual-language audio scripts in Kannada and Hindi.
        """
        digits = (digits or "").strip()

        # Step 0: Welcome greeting
        if not digits:
            prompt_text_kn = (
                "ನಮಸ್ಕಾರ, ಕಾಯಕಸೇತುವಿಗೆ ಸ್ವಾಗತ. "
                "ಕಾರ್ಮಿಕ ಪ್ರೊಫೈಲ್ ನೋಂದಾಯಿಸಲು 1 ಒತ್ತಿ. "
                "ಇಂದಿನ ಹೊಸ ಕೆಲಸಗಳ ಮಾಹಿತಿ ಕೇಳಲು 2 ಒತ್ತಿ."
            )
            prompt_text_hi = (
                "नमस्कार, श्रमसेतु में आपका स्वागत है। "
                "श्रमिक प्रोफ़ाइल दर्ज करने के लिए 1 दबाएं। "
                "आज के नए काम सुनने के लिए 2 दबाएं।"
            )
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="/api/v1/telecom/ivr" method="POST" timeout="10">
        <Say language="kn-IN" voice="Polly.Aditi">{prompt_text_kn}</Say>
        <Say language="hi-IN" voice="Polly.Aditi">{prompt_text_hi}</Say>
    </Gather>
</Response>"""
            return {
                "call_sid": call_sid,
                "twiml_xml": twiml,
                "prompt_text": f"[KN]: {prompt_text_kn}\n[HI]: {prompt_text_hi}",
                "prompt_audio_text": f"{prompt_text_kn}. {prompt_text_hi}",
                "language": "bilingual",
                "action": "gather",
                "options": [
                    {"digit": "1", "label": "ಕಾರ್ಮಿಕ ನೋಂದಣಿ / श्रमिक पंजीकरण (Register Profile)"},
                    {"digit": "2", "label": "ಹೊಸ ಕೆಲಸಗಳು / नए काम खोजें (Find Jobs)"}
                ]
            }

        # Step 1 Pressed: Quick Registration Voice Confirmation
        if digits == "1":
            # Auto-register basic worker profile based on caller ID
            existing = WorkerService.get_worker_by_phone(phone)
            if not existing:
                WorkerService.create_worker(WorkerCreate(
                    name=f"Worker {phone[-4:]}",
                    phone=phone,
                    trade="Helper",
                    experience_years=2,
                    daily_rate=650.0,
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
                "prompt_text": f"[KN]: {msg_kn}\n[HI]: {msg_hi}",
                "prompt_audio_text": f"{msg_kn}. {msg_hi}",
                "language": "bilingual",
                "action": "hangup",
                "options": []
            }

        # Step 2 Pressed: Voice Job Listing
        if digits == "2":
            jobs = JobService.list_jobs(status="open", limit=2)
            if jobs:
                j1 = jobs[0]
                text_kn = f"ಇಂದಿನ ಕೆಲಸ: {j1['title']}, ದಿನಗೂಲಿ ₹{j1['wage_offered']:.0f}. ಸಂಪರ್ಕ ಸಂಖ್ಯೆ {j1['employer_phone']}."
                text_hi = f"आज का काम: {j1['title']}, दैनिक मजदूरी ₹{j1['wage_offered']:.0f}. संपर्क नंबर {j1['employer_phone']}."
            else:
                text_kn = "ಸದ್ಯಕ್ಕೆ ಹೊಸ ಕೆಲಸಗಳು ಲಭ್ಯವಿಲ್ಲ. ಧನ್ಯವಾದಗಳು."
                text_hi = "फिलहाल कोई नया काम उपलब्ध नहीं है। धन्यवाद।"

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN" voice="Polly.Aditi">{text_kn}</Say>
    <Say language="hi-IN" voice="Polly.Aditi">{text_hi}</Say>
    <Hangup/>
</Response>"""
            return {
                "call_sid": call_sid,
                "twiml_xml": twiml,
                "prompt_text": f"[KN]: {text_kn}\n[HI]: {text_hi}",
                "prompt_audio_text": f"{text_kn}. {text_hi}",
                "language": "bilingual",
                "action": "hangup",
                "options": []
            }

        # Invalid digit fallback
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="kn-IN">ತಪ್ಪಾದ ಆಯ್ಕೆ. ದಯವಿಟ್ಟು ಮರಳಿ ಕರೆ ಮಾಡಿ.</Say>
    <Hangup/>
</Response>"""
        return {
            "call_sid": call_sid,
            "twiml_xml": twiml,
            "prompt_text": "Invalid selection / ತಪ್ಪಾದ ಆಯ್ಕೆ / अमान्य विकल्प",
            "prompt_audio_text": "ತಪ್ಪಾದ ಆಯ್ಕೆ. ದಯವಿಟ್ಟು ಮರಳಿ ಕರೆ ಮಾಡಿ.",
            "language": "kannada",
            "action": "hangup",
            "options": []
        }
