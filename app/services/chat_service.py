import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database import get_db
from app.services.worker_service import WorkerService
from app.services.job_service import JobService
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class ChatService:
    """
    Dedicated 1-to-1 Private Chat & Messaging Microservice.
    Enforces absolute privacy: only the two users in a conversation can read or send messages.
    """

    @staticmethod
    def send_message(sender_id: int, receiver_id: int, message_text: str, job_id: Optional[int] = None) -> Dict[str, Any]:
        message_text = message_text.strip()
        if not message_text:
            raise ValueError("Message content cannot be empty.")
        if sender_id == receiver_id:
            raise ValueError("Cannot send a message to yourself.")

        with get_db() as conn:
            cursor = conn.cursor()
            # Verify receiver exists
            cursor.execute("SELECT id, full_name, role FROM users WHERE id = ?", (receiver_id,))
            receiver = cursor.fetchone()
            if not receiver:
                raise ValueError("Receiver user does not exist.")

            cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, job_id, message_text, is_read)
                VALUES (?, ?, ?, ?, 0)
            """, (sender_id, receiver_id, job_id, message_text))
            msg_id = cursor.lastrowid
            conn.commit()

            cursor.execute("""
                SELECT m.*, 
                       s.full_name as sender_name, s.role as sender_role,
                       r.full_name as receiver_name, r.role as receiver_role
                FROM messages m
                JOIN users s ON m.sender_id = s.id
                JOIN users r ON m.receiver_id = r.id
                WHERE m.id = ?
            """, (msg_id,))
            row = cursor.fetchone()
            res = dict(row)
            res["is_mine"] = True
            res["is_read"] = bool(res["is_read"])
            return res

    @staticmethod
    def get_conversations(user_id: int) -> List[Dict[str, Any]]:
        """
        Returns all active conversations for the authenticated user.
        Strictly excludes any conversation where this user is not a participant.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            # Find distinct partner IDs
            cursor.execute("""
                SELECT DISTINCT 
                    CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END AS partner_id
                FROM messages
                WHERE sender_id = ? OR receiver_id = ?
            """, (user_id, user_id, user_id))
            partners = [row["partner_id"] for row in cursor.fetchall()]

            conversations = []
            for pid in partners:
                cursor.execute("SELECT * FROM users WHERE id = ?", (pid,))
                partner = cursor.fetchone()
                if not partner:
                    continue

                # Get latest message
                cursor.execute("""
                    SELECT m.*, j.title as job_title 
                    FROM messages m
                    LEFT JOIN jobs j ON m.job_id = j.id
                    WHERE (m.sender_id = ? AND m.receiver_id = ?)
                       OR (m.sender_id = ? AND m.receiver_id = ?)
                    ORDER BY m.created_at DESC, m.id DESC
                    LIMIT 1
                """, (user_id, pid, pid, user_id))
                last_msg = cursor.fetchone()

                # Count unread messages from this partner
                cursor.execute("""
                    SELECT COUNT(*) as unread_count
                    FROM messages
                    WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
                """, (pid, user_id))
                unread = cursor.fetchone()["unread_count"]

                conversations.append({
                    "other_user_id": partner["id"],
                    "other_user_name": partner["full_name"],
                    "other_user_role": partner["role"],
                    "other_user_phone": partner["phone"],
                    "other_user_trade": partner["trade"],
                    "other_user_company": partner["company_name"],
                    "last_message": last_msg["message_text"] if last_msg else "",
                    "last_message_at": str(last_msg["created_at"]) if last_msg else "",
                    "unread_count": unread,
                    "job_id": last_msg["job_id"] if last_msg else None,
                    "job_title": last_msg["job_title"] if last_msg else None
                })

            # Sort conversations by last message timestamp descending
            conversations.sort(key=lambda x: x["last_message_at"], reverse=True)
            return conversations

    @staticmethod
    def get_thread_messages(user_id: int, other_user_id: int) -> List[Dict[str, Any]]:
        """
        Returns the entire back-and-forth chat history between user_id and other_user_id.
        Marks any incoming unread messages as read.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            # Mark unread incoming messages as read
            cursor.execute("""
                UPDATE messages 
                SET is_read = 1 
                WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
            """, (other_user_id, user_id))
            conn.commit()

            cursor.execute("""
                SELECT m.*, 
                       s.full_name as sender_name, s.role as sender_role,
                       r.full_name as receiver_name, r.role as receiver_role
                FROM messages m
                JOIN users s ON m.sender_id = s.id
                JOIN users r ON m.receiver_id = r.id
                WHERE (m.sender_id = ? AND m.receiver_id = ?)
                   OR (m.sender_id = ? AND m.receiver_id = ?)
                ORDER BY m.created_at ASC, m.id ASC
            """, (user_id, other_user_id, other_user_id, user_id))
            rows = cursor.fetchall()

            messages = []
            for r in rows:
                item = dict(r)
                item["is_mine"] = (item["sender_id"] == user_id)
                item["is_read"] = bool(item["is_read"])
                item["created_at"] = str(item["created_at"])
                messages.append(item)

            return messages

    @staticmethod
    def get_or_create_user_for_target(target_type: str, target_id: int) -> Optional[Dict[str, Any]]:
        """
        Resolves or creates a user account for a Worker or Job Employer so that
        clicking 'Message Worker' or 'Message Employer' opens an instant chat thread.
        """
        with get_db() as conn:
            cursor = conn.cursor()

            if target_type == "job":
                job = JobService.get_job(target_id)
                if not job:
                    return None
                phone = job["employer_phone"]
                cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
                user = cursor.fetchone()
                if not user:
                    # Create employer user account
                    emp_name = job["employer_name"]
                    uname = "emp_" + phone[-6:]
                    from app.services.auth_service import AuthService
                    user = AuthService.register_user(
                        username=uname,
                        phone=phone,
                        password="password123",
                        role="employer",
                        full_name=emp_name,
                        company_name=emp_name,
                        city=job.get("city", "Bengaluru")
                    )
                else:
                    user = AuthService._format_user_dict(user)
                return {
                    "other_user": user,
                    "job_id": job["id"],
                    "job_title": job["title"],
                    "trade": job["trade"]
                }

            elif target_type == "worker":
                worker = WorkerService.get_worker(target_id)
                if not worker:
                    return None
                phone = worker["phone"]
                cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
                user = cursor.fetchone()
                if not user:
                    # Create worker user account
                    w_name = worker["name"]
                    uname = "wkr_" + phone[-6:]
                    from app.services.auth_service import AuthService
                    user = AuthService.register_user(
                        username=uname,
                        phone=phone,
                        password="password123",
                        role="worker",
                        full_name=w_name,
                        trade=worker["trade"],
                        daily_rate=worker["daily_rate"],
                        experience_years=worker["experience_years"],
                        city=worker["city"]
                    )
                else:
                    user = AuthService._format_user_dict(user)
                return {
                    "other_user": user,
                    "job_id": None,
                    "job_title": None,
                    "trade": worker["trade"]
                }

        return None
