# 🛠️ KaayakaSetu (ಕಾಯಕಸೇತು / श्रमसेतु)

### Enterprise Blue-Collar Workforce & Employer Microservices Platform
*Role-Based Authentication • Smart Job Matching • Geodesic Distance • Fair Wage Predictor • Kannada & Hindi Regional IVR Telephony Gateway*

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Twilio IVR](https://img.shields.io/badge/Twilio-Voice%20IVR-F22F46.svg)](https://www.twilio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Overview

**KaayakaSetu** is a production-grade, modular Python microservice platform designed specifically for the blue-collar workforce (electricians, plumbers, masons, carpenters, painters, welders, helpers) and employers (households, contractors, commercial establishments).

### Key Highlights:
1. **Zero-Friction Authentication & Strict Role Separation**:
   - Secure SHA-256 token-based authentication.
   - **Worker Workspace**: Live Job Feed, Personal Smart Matching, Fair Wage Predictor, Regional IVR Voice Simulator, 1-to-1 Private Messages.
   - **Employer Workspace**: Available Workers Feed, Post Work Requirement, Candidate Smart Matching, Fair Wage Predictor, 1-to-1 Private Messages.
   - **No Database Leakage**: Smart Matching queries are strictly scoped to the logged-in profile.
2. **Strictly Isolated 1-to-1 Private Messaging Service**:
   - Private, peer-to-peer messaging between workers and employers.
   - Zero eavesdropping: Only the two active participants can see and send messages in a thread. Third parties cannot view or list other users' conversations.
   - 1-click chat initiation directly from Job Cards ("💬 Message Employer") and Worker Cards ("💬 Message Worker").
3. **Real-World Twilio Regional Voice IVR (`+1 (737) 250-8034`)**:
   - Direct integration with Twilio Voice Webhook (`/api/v1/telecom/ivr/twiml`).
   - Automated bilingual voice menus in **Kannada (ಕನ್ನಡ)** and **Hindi (हिन्दी)** using Amazon Polly Neural TTS (`Polly.Aditi`).
   - Supports any standard mobile or feature phone without internet.
4. **Multi-Factor Heuristic Matching Engine**:
   - Geodesic travel distance calculation (Haversine formula).
   - Trade compatibility and skill hierarchy overlap.
   - Wage fairness and budget alignment.
5. **Fair Wage Prediction Engine**:
   - Calibrated against Indian economic city tiers (Tier-1, Tier-2, Tier-3).
   - Experience compounding (+3%/yr) and tool ownership allowances to prevent wage exploitation.

---

## 📞 Live Twilio Hotline

The platform is connected to an active Twilio telecom number:

| Live Hotline | Connected Webhook Endpoint | Regional Languages | Keypad Actions |
| :--- | :--- | :--- | :--- |
| **`+1 (737) 250-8034`** | `POST /api/v1/telecom/ivr/twiml` | Kannada (`kn-IN`) & Hindi (`hi-IN`) | `1` Register, `2` Find Jobs, `3` Fair Wage |

> 📱 **How to Test**: Dial **`+17372508034`** from any physical phone worldwide to experience the automated bilingual voice assistant. Alternatively, use the built-in virtual feature phone simulator on the web dashboard.

---

## 🏛️ Microservice Architecture

```
                                  ┌────────────────────────┐
                                  │   Clients & Devices    │
                                  └───────────┬────────────┘
                                              │
                      ┌───────────────────────┴────────────────────────┐
                      │ Web Dashboard (UI)    │ Voice Call (IVR / Telephony)
                      ▼                       ▼
      ┌────────────────────────────────────────────────────────────────────────┐
      │                   FastAPI Unified API Gateway                          │
      └───────────────────────────────────┬────────────────────────────────────┘
                                          │
    ┌────────────────┬────────────────────┼───────────────────┬────────────────┐
    ▼                ▼                    ▼                   ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐ ┌──────────────┐
│ Auth Service │ │ Worker / Job │ │ Smart Match  │ │ Regional Voice IVR │ │ Fair Wage    │
│ (/auth)      │ │ Feeds        │ │ Engine       │ │ Gateway            │ │ Predictor    │
│              │ │ (/workers)   │ │ (/match)     │ │ (/telecom)         │ │ (/wage)      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └─────────┬──────────┘ └──────┬───────┘
       │                │                │                   │                   │
       └────────────────┴───────┬────────┴───────────────────┴───────────────────┘
                                │
                        ┌───────▼────────┐
                        │ SQLite / Cache │
                        │  Persistence   │
                        └────────────────┘
```

---

## 🔒 Authentication & Role Separation

The platform enforces a dedicated **Authentication Gate**. The main dashboard opens only after successful authentication.

### Role Separation Matrix:

| Feature / Service | Worker Profile | Employer Profile |
| :--- | :---: | :---: |
| **Worker Registration Service** | ❌ Hidden *(Handled at signup)* | ❌ Hidden |
| **Live Job Feed** | ✅ **Visible** *(Default landing)* | ❌ Hidden |
| **IVR Voice Simulator** | ✅ **Visible** | ❌ Hidden |
| **Available Workers Feed** | ❌ Hidden | ✅ **Visible** *(Default landing)* |
| **Post Work Requirement** | ❌ Hidden | ✅ **Visible** |
| **Smart Multi-Factor Matcher** | ✅ **Visible** *(Scoped to Worker)* | ✅ **Visible** *(Scoped to Employer)* |
| **Fair Wage Predictor** | ✅ **Visible** | ✅ **Visible** |
| **1-to-1 Private Messages & Chat** | ✅ **Visible** *(Isolated threads)* | ✅ **Visible** *(Isolated threads)* |
| **Sign Out Option** | ✅ **Visible** in Header | ✅ **Visible** in Header |

### ⚡ 1-Click Evaluation Accounts (Built-in Demo Logins):

You can test either role instantly from the Login page without typing:

| Role | Username | Password | Profile Description |
| :--- | :--- | :--- | :--- |
| 👷 **Worker** | `ramesh_worker` | `password123` | Ramesh Gowda — Electrician, Bengaluru (₹850/day) |
| 🏢 **Employer** | `manjunatha_traders` | `password123` | Shree Manjunatha Traders — Shop Owner, Rajajinagar |
| 👷 **Worker** | `manjunath_plumber` | `password123` | Manjunath Patil — Plumber, Malleshwaram (₹750/day) |
| 🏢 **Employer** | `kiran_constructions` | `password123` | Kiran Constructions — Builder & Contractor, Bengaluru |

---

## 🎯 Smart Matching Microservice (`/api/v1/match`)

Matches are computed using multi-factor heuristic scoring with zero data leakage:
- **Skill Overlap (40%)**: Exact trade match (100%), related trades (70%), or helper fallback (50%).
- **Geographic Proximity (30%)**: Great-circle Haversine formula (100% for $\le 5\text{ km}$, tapering over search radius).
- **Wage Compatibility (20%)**: Checks if employer offer satisfies worker requested wage.
- **Reliability & Availability (10%)**: Verified star ratings and real-time availability.
- **User Scoping**:
  - **Workers** see only jobs matching their linked profile.
  - **Employers** see only candidates matching their active job postings.

---

## ⚖️ Fair Wage Prediction Engine (`/api/v1/wage`)

Protects workers against wage exploitation and assists employers with market benchmarking:
- **City Economic Tiers**:
  - Tier-1 (Bengaluru, Delhi): Baseline +25%
  - Tier-2 (Mysuru, Hubballi, Lucknow, Patna): Baseline 1.0x
  - Tier-3 (Davanagere, Belagavi): Baseline -15%
- **Experience Compounding**: +3% per year of verified experience.
- **Power Tool Ownership Allowance**: +₹150/day.
- **Emergency Surcharge**: +20% for urgent same-day callouts.
- **Multi-lingual Rationale**: Plain-language explanations generated in English, Kannada, and Hindi.

---

## 💬 1-to-1 Private Chat Microservice (`/api/v1/chat`)

Replaces insecure or public contact inquiries with strict peer-to-peer 1-to-1 private messaging:
- **Strict Privacy Isolation**: Every message query explicitly filters by `sender_id = :my_id OR receiver_id = :my_id`. Third parties cannot view or list other users' conversations.
- **Interactive Two-Pane UI**:
  - Left pane displays conversations list with live unread count badges.
  - Right pane features chat header with partner profile, role badge, job context, timestamped message bubbles (`.mine` and `.theirs`), and read receipts.
- **Direct Initiation**: Workers and employers can start messaging directly from any Job card or Candidate card with 1 click.
- **REST Endpoints**:
  - `GET /api/v1/chat/conversations` — Lists active conversations for the authenticated user.
  - `GET /api/v1/chat/thread/{other_user_id}` — Retrieves isolated message history with a partner.
  - `POST /api/v1/chat/send` — Sends a private message with optional job context.
  - `POST /api/v1/chat/initiate` — Resolves recipient from job or worker card and opens instant thread.

---

### 1. Prerequisites
- Python 3.10 or higher installed.
- Git.

### 2. Clone and Install
```bash
# Clone the repository
git clone https://github.com/Aryash-710/wicinternship.git
cd wicinternship

# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Run the Server
```bash
python run.py
```

### 4. Access the Application
- **Web Dashboard / Portal**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## ☁️ Cloud Deployment on Render

This repository includes a ready-to-use **`render.yaml`** configuration for 1-click cloud deployment on [Render](https://render.com/).

### Option A: Using Render Blueprint (Automated)
1. In your Render Dashboard, click **New +** &rarr; select **Blueprint**.
2. Connect your GitHub repository: `Aryash-710/wicinternship`.
3. Render automatically reads `render.yaml` and deploys the service.

### Option B: Manual Web Service Setup
1. In your Render Dashboard, click **New +** &rarr; select **Web Service**.
2. Connect your repository: `Aryash-710/wicinternship`.
3. Configure settings:
   - **Environment:** `Python 3` (or `Docker`)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
4. Add Environment Variables:
   - `HOST` = `0.0.0.0`
   - `DEBUG` = `False`
5. Click **Create Web Service**.

---

## 📞 Twilio Voice Webhook Configuration

To connect your own Twilio number:

1. Log in to the [Twilio Console](https://console.twilio.com/).
2. Navigate to **Phone Numbers** &rarr; **Manage** &rarr; **Active numbers**.
3. Under **Voice Configuration &rarr; A CALL COMES IN**:
   - Set to: **Webhook**
   - URL: `https://<YOUR-RENDER-APP-OR-NGROK-URL>/api/v1/telecom/ivr/twiml`
   - Method: **HTTP POST**
4. Click **Save configuration**.

---

## 🐳 Docker Deployment

To run in an isolated Docker container:

```bash
# Build and start container
docker compose up -d --build

# View container logs
docker compose logs -f

# Stop container
docker compose down
```

---

## 🧪 Automated Testing Suite

Run the full automated test suite covering all microservices, role authentication, and matching:

```bash
pytest app/tests/test_services.py -v
```

### Verified Test Cases:
- `test_health_check` &rarr; System status and microservices UP check.
- `test_location_service_distance` &rarr; Haversine formula accuracy.
- `test_fair_wage_prediction` &rarr; City tiers and experience calculations.
- `test_worker_registration_and_api` &rarr; Worker profile creation and validation.
- `test_job_posting_and_api` &rarr; Employer job postings.
- `test_smart_matching_service` &rarr; Multi-factor heuristic scoring.
- `test_feed_service_endpoints` &rarr; Filtered feeds and aggregations.
- `test_contact_service_and_sms` &rarr; Inquiry dispatch and SMS simulation.
- `test_ivr_service_direct_unit_flows` &rarr; DTMF state machine transitions.
- `test_ivr_voice_bilingual_api_flow` &rarr; TwiML XML and Kannada/Hindi voice scripts.
- `test_auth_service_and_roles` &rarr; Token generation, password hashing, and role checks.
- `test_scoped_matching_queries_worker_and_employer` &rarr; Query scoping and zero data leakage.

---

## 📂 Project Structure

```
bluecollar_platform/
├── app/
│   ├── models/
│   │   └── schemas.py              # Pydantic schemas (Worker, Job, Match, Auth, IVR)
│   ├── routers/
│   │   ├── auth.py                 # Authentication router (register, login, me, logout)
│   │   ├── workers.py              # Worker profiles microservice
│   │   ├── jobs.py                 # Job requirements microservice
│   │   ├── matching.py             # Role-scoped smart matching router
│   │   ├── wage.py                 # Fair wage prediction router
│   │   ├── telecom.py              # Twilio/Exotel IVR voice call router
│   │   ├── feeds.py                # Job & worker feed endpoints
│   │   ├── location.py             # Geodesic distance calculation router
│   │   └── contact.py              # Inquiries and SMS notification bridge
│   ├── services/
│   │   ├── auth_service.py         # Password hashing, token management, session handling
│   │   ├── ivr_service.py          # Dedicated IVR voice state machine & TwiML generator
│   │   ├── matching_service.py     # Heuristic multi-factor matching algorithms
│   │   ├── wage_service.py         # Fair wage prediction engine
│   │   ├── worker_service.py       # Worker CRUD operations
│   │   ├── job_service.py          # Job posting CRUD operations
│   │   └── contact_service.py      # Direct contact inquiry management
│   ├── static/
│   │   ├── css/style.css           # Modern CSS responsive styles & phone styling
│   │   ├── js/app.js               # Frontend controller & role separation logic
│   │   └── index.html              # Single Page Application (Auth screen & Dashboard)
│   ├── config.py                   # Global configuration & environment settings
│   ├── database.py                 # SQLite database initialization & seeding
│   └── main.py                     # FastAPI application factory & router registration
├── app/tests/
│   └── test_services.py            # Comprehensive test suite (12 tests)
├── Dockerfile                      # Production multi-stage Docker build
├── docker-compose.yml              # Local container orchestration
├── render.yaml                     # Render Cloud Deployment Blueprint
├── requirements.txt                # Python package dependencies
├── run.py                          # Single-command application launcher
└── README.md                       # Platform documentation
```

---

## 📜 License
This project is open-source and distributed under the [MIT License](LICENSE).
