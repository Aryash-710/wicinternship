# 🛠️ KaayakaSetu (ಕಾಯಕಸೇತು / श्रमसेतु)

### Microservice Platform for Blue-Collar Workers & Employers
*Smart Job Matching • Geodesic Distance • Fair Wage Prediction • Regional Kannada & Hindi Interactive Voice Response (IVR) Gateway*

---

## 🌟 Overview

**KaayakaSetu** is a production-ready, modular Python microservice application designed specifically for the blue-collar workforce (electricians, plumbers, masons, carpenters, painters, welders, helpers, drivers) and employers (households, contractors, businesses).

Because a large segment of India's blue-collar workforce uses basic feature phones or prefers regional dialects, **KaayakaSetu provides an Interactive Voice Response (IVR) telephony engine in Kannada (ಕನ್ನಡ) and Hindi (हिन्दी)** alongside a modern web dashboard and REST API gateway. Workers and employers can dial in, listen to voice prompts, and interact using DTMF keypad tones (1, 2, 3) to register profiles, discover matching jobs, and check fair wage rates.

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
│ Worker       │ │ Jobs         │ │ Smart Match  │ │ Regional Voice IVR │ │ Fair Wage    │
│ Service      │ │ Service      │ │ Engine       │ │ Gateway            │ │ Predictor    │
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
- Profile sources tracked (`web`, `ivr`).

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

### 6. 📞 Regional IVR Voice Service (`/api/v1/telecom`)
Designed for workers and employers on any phone without requiring internet:
- **Bilingual Voice Engine**: Dual-language voice prompts in Kannada and Hindi with Polly/Neural TTS compatibility (`kn-IN` and `hi-IN`).
- **TwiML / Voice XML Standards**: Generates `<Response>`, `<Gather>`, `<Say>`, `<Hangup>` markup compatible with **Twilio**, **Exotel**, and other voice gateways.
- **Keypad DTMF Navigation**:
  - `Press 1`: Auto-registers worker profile linked to caller ID.
  - `Press 2`: Narrates available jobs nearby with employer contact numbers.
  - `Press 3`: Voice calculation of current fair daily wage benchmarks.
- **Browser Speech Synthesizer Simulator**: Test voice flows directly in the web UI using the built-in virtual feature phone simulator.

### 7. 🤝 Contact & Communication Service (`/api/v1/contact`)
- Initiate direct work inquiry between worker and employer.
- Simulated instant SMS / WhatsApp notification dispatch.
- Contact acceptance and direct phone number exchange.

---

## 📞 How to Set Up the IVR Service

The IVR service is accessible via REST/JSON for client apps and via standard Voice XML (`TwiML`) for cloud telephony providers like **Twilio**, **Exotel**, or **Plivo**.

### Step 1: Start the KaayakaSetu Server
```bash
python run.py
```
The application runs on `http://localhost:8000`.

### Step 2: Expose Your Local Server to the Web (for Webhooks)
Telephony providers need a publicly accessible HTTPS webhook URL to reach your local server.
Using **ngrok** (or cloudflared):
```bash
ngrok http 8000
```
Note the HTTPS forwarding URL (e.g. `https://abc1234.ngrok-free.app`).

### Step 3: Configure Your Telephony Provider

#### A. Setting up with Twilio:
1. Log in to the [Twilio Console](https://console.twilio.com/).
2. Buy or select a phone number with **Voice** capabilities.
3. Scroll down to **Voice Configuration**:
   - Set **"A Call Comes In"** to `Webhook`.
   - Set URL to: `https://<YOUR-NGROK-URL>/api/v1/telecom/ivr/twiml`
   - Set HTTP Method to: `HTTP POST`.
4. Click **Save Configuration**.
5. Dial your Twilio number from any phone! You will hear the bilingual Kannada & Hindi greeting.

#### B. Setting up with Exotel:
1. Log in to your [Exotel Dashboard](https://my.exotel.com/).
2. Go to **App Bazaar** &rarr; **Create Flow**.
3. Add a **Passthru / Webhook** applet:
   - URL: `https://<YOUR-NGROK-URL>/api/v1/telecom/ivr/exotel`
   - Method: `POST`.
4. Connect your virtual Exotel phone number to this flow.

### Step 4: Testing the IVR Service Locally (No Telephony Provider Needed)

You can test the entire voice flow without any provider:

#### Option 1: Using the Web Dashboard Simulator
1. Open `http://localhost:8000/` in your browser.
2. Click the **"📞 IVR Voice Simulator"** tab.
3. Enter any test phone number (e.g. `9845011223`).
4. Click **📞 CALL**.
5. The browser speaks the Kannada and Hindi voice prompts aloud!
6. Click `1` on the keypad to register, `2` to hear jobs, or `3` to hear wage rates.
7. Inspect the live generated TwiML XML payload in the right panel.

#### Option 2: Using cURL or Postman

**1. Initial Call (Greeting):**
```bash
curl -X POST "http://localhost:8000/api/v1/telecom/ivr" \
     -H "Content-Type: application/json" \
     -d '{"call_sid": "CALL_101", "caller_phone": "9845011223", "digits": ""}'
```

**2. Send DTMF Digit 1 (Register Profile):**
```bash
curl -X POST "http://localhost:8000/api/v1/telecom/ivr" \
     -H "Content-Type: application/json" \
     -d '{"call_sid": "CALL_101", "caller_phone": "9845011223", "digits": "1"}'
```

**3. Direct Twilio TwiML Endpoint:**
```bash
curl -X POST "http://localhost:8000/api/v1/telecom/ivr/twiml" \
     -d "CallSid=CA12345&From=%2B919845011223&Digits=2"
```

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

You can deploy the full **KaayakaSetu** microservices platform in an isolated Docker container.

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

---

## 🧪 Running Automated Tests

Run the unit test suite covering all microservices:
```bash
pytest app/tests/test_services.py -v
```
