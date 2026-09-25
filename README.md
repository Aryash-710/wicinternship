# 🛠️ KaayakaSetu (ಕಾಯಕಸೇತು / श्रमसेतु)

### Microservice Platform for Blue-Collar Workers & Employers
*Smart Job Matching • Location & Distance • Fair Wage Prediction • Regional Kannada & Hindi USSD & IVR Telecom Gateway*

---

## 🌟 Overview

**KaayakaSetu** is a production-ready, modular Python microservice application designed specifically for the blue-collar workforce (electricians, plumbers, masons, carpenters, painters, welders, helpers, drivers) and employers (households, contractors, businesses).

Because a large segment of India's blue-collar workforce uses feature phones (basic non-smartphones) or prefers regional dialects, **KaayakaSetu provides first-class USSD (`*345#`) and interactive Voice IVR capabilities in Kannada (ಕನ್ನಡ) and Hindi (हिन्दी)** alongside a modern web dashboard and REST API gateway.

---

## 🏛️ Microservice Architecture

```
                                  ┌────────────────────────┐
                                  │   Clients & Devices    │
                                  └───────────┬────────────┘
                                              │
                      ┌───────────────────────┼────────────────────────┐
                      │ Web Dashboard (UI)    │ Feature Phone (*345#)  │ Voice Call (IVR)
                      ▼                       ▼                        ▼
      ┌────────────────────────────────────────────────────────────────────────┐
      │                   FastAPI Unified API Gateway                          │
      └───────────────────────────────────┬────────────────────────────────────┘
                                          │
    ┌────────────────┬────────────────────┼───────────────────┬────────────────┐
    ▼                ▼                    ▼                   ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐ ┌──────────────┐
│ Worker       │ │ Jobs         │ │ Smart Match  │ │ Regional Telecom   │ │ Fair Wage    │
│ Service      │ │ Service      │ │ Engine       │ │ Gateway (USSD/IVR) │ │ Predictor    │
│ (/workers)   │ │ (/jobs)      │ │ (/match)     │ │ (/telecom)         │ │ (/wage)      │
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

## 🚀 Key Microservices & Features

### 1. 👷 Worker Profile Service (`/api/v1/workers`)
- Create and manage blue-collar profiles (electrician, plumber, mason, carpenter, painter, etc.).
- Daily & hourly wage expectations, years of verified experience, trade specialization.
- Multi-lingual preference (`kannada`, `hindi`, `english`).
- Profile sources tracked (`web`, `ussd`, `ivr`).

### 2. 💼 Jobs Service (`/api/v1/jobs`)
- Employers post work vacancies with trade requirements, duration, daily wage, and urgency.
- Real-time status tracking (`open`, `in_progress`, `completed`, `cancelled`).

### 3. 🎯 Smart Job Matching Service (`/api/v1/match`)
Multi-factor AI/heuristic compatibility engine scoring:
- **Skill Overlap (40%)**: Exact trade match (100%), related trades (70%), or helper fallback (50%).
- **Geographic Distance (30%)**: Great-circle Haversine formula (100% for <= 5km, tapering off over radius).
- **Wage Compatibility (20%)**: Checks if employer offer satisfies worker expectation.
- **Reliability & Availability (10%)**: Verified star rating and availability status.
- **Explainability**: Returns transparent reasoning for every match in plain language.

### 4. ⚖️ Fair Wage Prediction Service (`/api/v1/wage`)
Protects blue-collar workers from wage exploitation:
- Calibrated against Indian minimum wage benchmarks and market standards.
- **City Economic Tiers**: Tier-1 (Bengaluru, Delhi, Mumbai: +25%), Tier-2 (Mysuru, Hubballi, Lucknow, Patna: 1.0x baseline), Tier-3 (-15%).
- **Compounding Experience**: +3% per year of trade experience.
- **Tool Ownership Premium**: Extra daily allowance (+₹150/day) if workers bring power tools.
- **Urgency Surcharge**: +20% for same-day emergency calls.
- **Multi-lingual Explanations**: Generates complete wage rationale in English, **Kannada (ಕನ್ನಡ)**, and **Hindi (हिन्दी)**.

### 5. 📍 Location Service (`/api/v1/location`)
- High-performance geodesic Haversine distance calculator.
- Built-in geo-coordinate database for major Indian hubs across Karnataka (Bengaluru, Mysuru, Hubballi, Belagavi, Davanagere, etc.) and Hindi-speaking states (Delhi, Lucknow, Patna, Kanpur, Jaipur, Indore).

### 6. 📱 Regional USSD & IVR Service (`/api/v1/telecom`)
Designed for non-smartphone feature phones:
- **USSD Engine (`*345#`)**:
  - Session state machine compliant with telecom standards (`CON` / `END`).
  - **Kannada & Hindi navigation**: Workers register their trade, experience, wage expectation, and city by pressing 1, 2, 3 on their keypad.
  - **Job Finder via USSD**: Workers dial `*345#`, select their trade, and immediately get SMS/flash text with the top 3 matching jobs, wage rate, and employer phone number!
- **IVR Voice Call Engine**:
  - Dual-language voice prompts with `<Gather>` and `<Say voice="Polly.Aditi">` compatible TwiML/Voice XML.
  - Generates spoken Kannada and Hindi audio scripts for interactive voice response.

### 7. 🤝 Contact & Communication Service (`/api/v1/contact`)
- Initiate direct work inquiry between worker and employer.
- Simulated instant SMS / WhatsApp notification dispatch.
- Contact acceptance and direct phone number exchange.

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+ installed.

### 2. Run the Platform
```bash
# Navigate to the project directory
cd bluecollar_platform

# Install dependencies (FastAPI, Uvicorn, Pydantic, HTTPX)
python -m pip install -r requirements.txt

# Start all microservices and web UI
python run.py
```

### 3. Open in Browser
- **Interactive Web Dashboard**: `http://localhost:8000/`
- **Interactive Swagger API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **System Health Check**: `http://localhost:8000/health`

---

## 🐳 Docker Deployment

You can deploy the full **KaayakaSetu** microservices platform in an isolated, production-ready Docker container.

### Option A: Using Docker Compose (Recommended)

1. **Build and launch the platform:**
   ```bash
   docker compose up -d --build
   ```

2. **Verify container status and health:**
   ```bash
   docker compose ps
   ```

3. **View live logs:**
   ```bash
   docker compose logs -f
   ```

4. **Stop the platform:**
   ```bash
   docker compose down
   ```

> **Data Persistence:** The SQLite database is automatically persisted in the `kaayakasetu_sqlite_data` Docker volume across container restarts and builds.

---

### Option B: Using Docker CLI Directly

1. **Build the image:**
   ```bash
   docker build -t kaayakasetu-platform:latest .
   ```

2. **Run the container with persistent volume:**
   ```bash
   docker volume create kaayakasetu_data
   docker run -d \
     --name kaayakasetu-platform \
     -p 8000:8000 \
     -e HOST=0.0.0.0 \
     -e PORT=8000 \
     -v kaayakasetu_data:/app/data \
     --restart unless-stopped \
     kaayakasetu-platform:latest
   ```

3. **Check health and logs:**
   ```bash
   docker ps
   docker logs -f kaayakasetu-platform
   ```

---

## 🧪 Running Automated Tests

Run the full automated test suite covering all microservices:
```bash
pytest app/tests/test_services.py -v
```

