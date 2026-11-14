import os
import sqlite3
import json
import logging
from contextlib import contextmanager
from datetime import datetime
from app.config import DB_PATH

logger = logging.getLogger(__name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@contextmanager
def get_db():
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise e
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Workers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            trade TEXT NOT NULL,
            secondary_skills TEXT,
            experience_years INTEGER NOT NULL DEFAULT 1,
            daily_rate REAL NOT NULL,
            hourly_rate REAL,
            city TEXT NOT NULL,
            area TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            availability TEXT NOT NULL DEFAULT 'available',
            rating REAL DEFAULT 4.5,
            jobs_completed INTEGER DEFAULT 0,
            language_pref TEXT NOT NULL DEFAULT 'kannada',
            source TEXT NOT NULL DEFAULT 'web',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Jobs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            trade TEXT NOT NULL,
            description TEXT,
            employer_name TEXT NOT NULL,
            employer_phone TEXT NOT NULL,
            city TEXT NOT NULL,
            area TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            duration_days INTEGER NOT NULL DEFAULT 1,
            wage_offered REAL NOT NULL,
            payment_type TEXT NOT NULL DEFAULT 'daily',
            urgency TEXT NOT NULL DEFAULT 'normal',
            workers_needed INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Contacts / Communication Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_type TEXT NOT NULL, -- 'worker' or 'employer'
            sender_id INTEGER NOT NULL,
            receiver_type TEXT NOT NULL, -- 'worker' or 'employer'
            receiver_id INTEGER NOT NULL,
            job_id INTEGER,
            message TEXT,
            status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'accepted', 'declined'
            phone_shared INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 4. IVR Telecom Sessions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS telecom_sessions (
            session_id TEXT PRIMARY KEY,
            phone_number TEXT NOT NULL,
            session_type TEXT NOT NULL DEFAULT 'ivr',
            current_step TEXT NOT NULL DEFAULT 'welcome',
            language TEXT NOT NULL DEFAULT 'bilingual',
            draft_json TEXT DEFAULT '{}',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Users Authentication Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL, -- 'worker' or 'employer'
            full_name TEXT NOT NULL,
            worker_id INTEGER,
            city TEXT,
            trade TEXT,
            company_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 6. User Sessions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        conn.commit()
        seed_sample_data(conn)


def seed_sample_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM workers;")
    workers_count = cursor.fetchone()["count"]
    if workers_count == 0:
        # Seed Sample Workers across Karnataka & Hindi belt
        sample_workers = [
            (
                "Ramesh Gowda", "9845011223", "Electrician", "Wiring, Inverter, MCB", 5, 850.0, 150.0,
                "Bengaluru", "Rajajinagar", 12.9904, 77.5530, "available", 4.8, 42, "kannada", "web"
            ),
            (
                "Manjunath Patil", "9845022334", "Plumber", "Pipe fitting, Tank cleaning, Taps", 4, 750.0, 120.0,
                "Bengaluru", "Malleshwaram", 13.0031, 77.5643, "available", 4.6, 28, "kannada", "ivr"
            ),
            (
                "Suresh Kumar", "9845033445", "Mason", "Brickwork, Plastering, Tiles", 8, 950.0, 160.0,
                "Bengaluru", "Yeshwanthpur", 13.0238, 77.5458, "available", 4.9, 85, "kannada", "ivr"
            ),
            (
                "Basavaraj K", "9845044556", "Carpenter", "Furniture repair, Doors, Modular fitting", 6, 900.0, 150.0,
                "Hubballi", "Vidyanagar", 15.3647, 75.1240, "available", 4.7, 31, "kannada", "ivr"
            ),
            (
                "Chandrashekhar", "9845055667", "Painter", "Interior painting, Waterproofing, Putty", 3, 700.0, 100.0,
                "Mysuru", "Kuvempunagar", 12.2890, 76.6346, "available", 4.5, 19, "kannada", "web"
            ),
            (
                "Ram Lal Yadav", "9811012345", "Electrician", "House wiring, Fan repair, Meter board", 7, 850.0, 140.0,
                "Delhi", "Laxmi Nagar", 28.6304, 77.2773, "available", 4.8, 55, "hindi", "ivr"
            ),
            (
                "Dinesh Verma", "9811023456", "Plumber", "Sanitary fittings, Motor install", 5, 800.0, 130.0,
                "Lucknow", "Alambagh", 26.8150, 80.9020, "available", 4.6, 34, "hindi", "ivr"
            ),
            (
                "Santosh Chauhan", "9811034567", "Mason", "Construction, Wall tile laying", 10, 1000.0, 170.0,
                "Patna", "Kankarbagh", 25.5941, 85.1376, "available", 4.9, 110, "hindi", "web"
            ),
            (
                "Anand Kumar", "9845099887", "Helper", "Loading, Material shifting, Site cleanup", 2, 550.0, 80.0,
                "Bengaluru", "Peenya", 13.0285, 77.5197, "available", 4.3, 14, "kannada", "ivr"
            ),
            (
                "Sunil Yadav", "9811045678", "Welder", "Grill fabrication, Gate repair, Arc welding", 6, 900.0, 150.0,
                "Delhi", "Okhla", 28.5300, 77.2700, "available", 4.7, 40, "hindi", "web"
            )
        ]

        cursor.executemany("""
        INSERT INTO workers (
            name, phone, trade, secondary_skills, experience_years, daily_rate, hourly_rate,
            city, area, latitude, longitude, availability, rating, jobs_completed, language_pref, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, sample_workers)

        # Seed Sample Jobs
        sample_jobs = [
            (
                "Commercial Shop 3-Phase Wiring Needed", "Electrician",
                "Urgent requirement for complete 3-phase wiring in newly renovated shop.",
                "Shree Manjunatha Traders", "9900112233", "Bengaluru", "Rajajinagar",
                12.9900, 77.5520, 2, 1800.0, "daily", "urgent", 2, "open"
            ),
            (
                "Bathroom Water Line & Tap Repair", "Plumber",
                "Leaking overhead pipe and fitting of new bathroom sink and fixtures.",
                "Raghavendra Rao", "9900223344", "Bengaluru", "Malleshwaram",
                13.0040, 77.5650, 1, 800.0, "daily", "normal", 1, "open"
            ),
            (
                "Compound Wall Masonry Work", "Mason",
                "Building 40 feet brick compound wall and cement plastering.",
                "Kiran Constructions", "9900334455", "Bengaluru", "Yeshwanthpur",
                13.0250, 77.5460, 4, 3800.0, "daily", "normal", 3, "open"
            ),
            (
                "Apartment Repainting (2BHK)", "Painter",
                "Interior walls painting with primer, putty, and 2 coats of emulsion paint.",
                "Naveen Hegde", "9900445566", "Mysuru", "Kuvempunagar",
                12.2900, 76.6350, 3, 2400.0, "daily", "normal", 2, "open"
            ),
            (
                "Showroom Wooden Display Racks Fitting", "Carpenter",
                "Installation of plywood display racks and fixing laminate edges.",
                "Hubli Fashion Hub", "9900556677", "Hubballi", "Vidyanagar",
                15.3650, 75.1250, 2, 1900.0, "daily", "normal", 1, "open"
            ),
            (
                "Factory Main Line Inverter Setup", "Electrician",
                "Industrial panel check and heavy load inverter connection.",
                "Sharma Enterprises", "9810112233", "Delhi", "Okhla",
                28.5320, 77.2710, 1, 1000.0, "daily", "urgent", 1, "open"
            ),
            (
                "School Building Renovation Brickwork", "Mason",
                "Wall repairs, stair renovation, and cement finishing.",
                "Adarsh Vidyalaya", "9810223344", "Lucknow", "Alambagh",
                26.8160, 80.9030, 5, 5200.0, "daily", "normal", 2, "open"
            ),
            (
                "Warehouse Goods Loading & Unloading", "Helper",
                "Heavy boxes unloading from transport container and stacking.",
                "Karnataka Logistics", "9900778899", "Bengaluru", "Peenya",
                13.0290, 77.5200, 1, 650.0, "daily", "urgent", 4, "open"
            )
        ]

        cursor.executemany("""
        INSERT INTO jobs (
            title, trade, description, employer_name, employer_phone, city, area,
            latitude, longitude, duration_days, wage_offered, payment_type, urgency,
            workers_needed, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, sample_jobs)

    cursor.execute("SELECT COUNT(*) as count FROM users;")
    users_count = cursor.fetchone()["count"]
    if users_count == 0:
        # Seed Sample Users (Workers & Employers)
        import hashlib
        def hash_pw(pw: str) -> str:
            return hashlib.sha256(pw.encode("utf-8")).hexdigest()

        sample_users = [
            (
                "ramesh_worker", "9845011223", hash_pw("password123"), "worker",
                "Ramesh Gowda", 1, "Bengaluru", "Electrician", None
            ),
            (
                "manjunath_plumber", "9845022334", hash_pw("password123"), "worker",
                "Manjunath Patil", 2, "Bengaluru", "Plumber", None
            ),
            (
                "manjunatha_traders", "9900112233", hash_pw("password123"), "employer",
                "Shree Manjunatha Traders", None, "Bengaluru", None, "Shree Manjunatha Traders"
            ),
            (
                "kiran_constructions", "9900334455", hash_pw("password123"), "employer",
                "Kiran Constructions", None, "Bengaluru", None, "Kiran Constructions"
            )
        ]

        cursor.executemany("""
        INSERT OR IGNORE INTO users (
            username, phone, password_hash, role, full_name, worker_id, city, trade, company_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, sample_users)

    conn.commit()
    logger.info("Sample database initialized with realistic worker, job, and user profiles!")
