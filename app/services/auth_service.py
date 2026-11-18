import hashlib
import secrets
import logging
from typing import Optional, Dict, Any, List
from app.database import get_db
from app.models.schemas import WorkerCreate
from app.services.worker_service import WorkerService

logger = logging.getLogger(__name__)


class AuthService:
    """
    Lightweight, secure authentication service for Workers and Employers.
    Supports registration, password verification, token generation,
    and profile association.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.hash_password(plain_password) == hashed_password

    @classmethod
    def register_user(
        cls,
        username: str,
        phone: str,
        password: str,
        role: str,
        full_name: str,
        city: Optional[str] = "Bengaluru",
        trade: Optional[str] = None,
        daily_rate: Optional[float] = None,
        experience_years: Optional[int] = 2,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registers a new user. If the user is a worker, automatically creates
        or links their corresponding Worker record in the workers table.
        """
        username = username.strip().lower()
        phone = phone.strip()
        role = role.strip().lower()
        if role not in ("worker", "employer"):
            raise ValueError("Role must be either 'worker' or 'employer'")

        hashed = cls.hash_password(password)
        worker_id = None

        # Check worker record outside the transaction to prevent nested SQLite connections
        if role == "worker":
            existing_worker = WorkerService.get_worker_by_phone(phone)
            if existing_worker:
                worker_id = existing_worker["id"]
            else:
                new_w = WorkerCreate(
                    name=full_name,
                    phone=phone,
                    trade=trade or "Helper",
                    experience_years=experience_years or 2,
                    daily_rate=daily_rate,
                    city=city or "Bengaluru",
                    source="web"
                )
                created_w = WorkerService.create_worker(new_w)
                worker_id = created_w["id"]

        with get_db() as conn:
            cursor = conn.cursor()
            # Check for existing username or phone
            cursor.execute("SELECT id FROM users WHERE username = ? OR phone = ?", (username, phone))
            if cursor.fetchone():
                raise ValueError("A user with this username or phone number already exists.")

            cursor.execute("""
                INSERT INTO users (username, phone, password_hash, role, full_name, worker_id, city, trade, company_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                username, phone, hashed, role, full_name, worker_id,
                city, trade, company_name or (full_name if role == "employer" else None)
            ))
            user_id = cursor.lastrowid

            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return cls._format_user_dict(user)

    @classmethod
    def authenticate(cls, username_or_phone: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticates a user via either username or phone number and password.
        """
        identifier = username_or_phone.strip()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users
                WHERE lower(username) = lower(?) OR phone = ?
            """, (identifier, identifier))
            user = cursor.fetchone()
            if not user:
                return None

            if not cls.verify_password(password, user["password_hash"]):
                return None

            return cls._format_user_dict(user)

    @classmethod
    def create_session(cls, user_id: int) -> str:
        """
        Generates an active bearer session token and persists it.
        """
        token = "token_" + secrets.token_hex(24)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_sessions (token, user_id) VALUES (?, ?)", (token, user_id))
        return token

    @classmethod
    def get_user_by_username_or_phone(cls, username_or_phone: str) -> Optional[Dict[str, Any]]:
        ident = (username_or_phone or "").strip()
        if not ident:
            return None
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? OR phone = ?", (ident.lower(), ident))
            row = cursor.fetchone()
            if row:
                return cls._format_user_dict(row)
        return None

    @classmethod
    def get_user_by_token(cls, token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        token = token.replace("Bearer ", "").strip()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.* FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.token = ?
            """, (token,))
            user = cursor.fetchone()
            if not user:
                return None
            return cls._format_user_dict(user)

    @classmethod
    def logout(cls, token: str) -> bool:
        if not token:
            return False
        token = token.replace("Bearer ", "").strip()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
            return cursor.rowcount > 0

    @classmethod
    def get_user_by_id(cls, user_id: int) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                return None
            return cls._format_user_dict(user)

    @classmethod
    def get_demo_accounts(cls) -> List[Dict[str, Any]]:
        """
        Returns list of pre-configured accounts for 1-click evaluation.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, phone, role, full_name, trade, company_name, city, worker_id FROM users")
            rows = cursor.fetchall()
            return [cls._format_user_dict(r) for r in rows]

    @staticmethod
    def _format_user_dict(row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "username": row["username"],
            "phone": row["phone"],
            "role": row["role"],
            "full_name": row["full_name"],
            "worker_id": row.get("worker_id"),
            "city": row.get("city"),
            "trade": row.get("trade"),
            "company_name": row.get("company_name")
        }

