from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database import get_db
from app.models.schemas import ContactCreate, ContactStatusUpdate
from app.services.worker_service import WorkerService
from app.services.job_service import JobService


class ContactService:
    @staticmethod
    def create_contact(contact: ContactCreate) -> Dict[str, Any]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (
                    sender_type, sender_id, receiver_type, receiver_id, job_id, message, status
                ) VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """, (
                contact.sender_type, contact.sender_id, contact.receiver_type,
                contact.receiver_id, contact.job_id, contact.message
            ))
            contact_id = cursor.lastrowid
            return ContactService.get_contact_with_details(contact_id, conn)

    @staticmethod
    def get_contact_with_details(contact_id: int, conn=None) -> Optional[Dict[str, Any]]:
        def _fetch(c):
            cursor = c.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)

            # Enrich with sender & receiver contact numbers
            if res["sender_type"] == "worker":
                sender = WorkerService.get_worker(res["sender_id"])
                res["sender_name"] = sender["name"] if sender else "Worker"
                res["sender_phone"] = sender["phone"] if sender else ""
            else:
                job = JobService.get_job(res["job_id"]) if res["job_id"] else None
                res["sender_name"] = job["employer_name"] if job else "Employer"
                res["sender_phone"] = job["employer_phone"] if job else ""

            if res["receiver_type"] == "worker":
                receiver = WorkerService.get_worker(res["receiver_id"])
                res["receiver_name"] = receiver["name"] if receiver else "Worker"
                res["receiver_phone"] = receiver["phone"] if receiver else ""
            else:
                job = JobService.get_job(res["job_id"]) if res["job_id"] else None
                res["receiver_name"] = job["employer_name"] if job else "Employer"
                res["receiver_phone"] = job["employer_phone"] if job else ""

            return res

        if conn:
            return _fetch(conn)
        with get_db() as conn_new:
            return _fetch(conn_new)

    @staticmethod
    def update_status(contact_id: int, status_update: ContactStatusUpdate) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET status = ? WHERE id = ?",
                (status_update.status, contact_id)
            )
            return ContactService.get_contact_with_details(contact_id, conn)

    @staticmethod
    def list_contacts_for_user(user_type: str, user_id: int) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM contacts
                WHERE (sender_type = ? AND sender_id = ?)
                   OR (receiver_type = ? AND receiver_id = ?)
                ORDER BY created_at DESC
            """, (user_type, user_id, user_type, user_id))
            rows = cursor.fetchall()
            return [ContactService.get_contact_with_details(r["id"], conn) for r in rows]

    @staticmethod
    def simulate_dispatch_sms(contact_id: int) -> Dict[str, Any]:
        """
        Simulates sending an SMS or WhatsApp notification to the parties involved.
        """
        c = ContactService.get_contact_with_details(contact_id)
        if not c:
            return {"status": "error", "message": "Contact record not found"}

        sms_payload = {
            "dispatch_status": "SENT",
            "provider": "MockExotelTelecomGateway",
            "timestamp": datetime.now().isoformat(),
            "to_phone": c.get("receiver_phone"),
            "sender_phone": c.get("sender_phone"),
            "notification_text": (
                f"KaayakaSetu: You have a new work inquiry from {c.get('sender_name')} "
                f"(Ph: {c.get('sender_phone')}). Message: '{c.get('message', 'Interested in work')}'. "
                f"Call back to confirm."
            )
        }
        return sms_payload
