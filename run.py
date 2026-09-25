#!/usr/bin/env python3
"""
KaayakaSetu (ಕಾಯಕಸೇತು / श्रमसेತು) - Main Server Runner
Single-command launcher for all microservices, API gateway, and Web Dashboard.
"""
import sys
import os

# Ensure safe UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.config import HOST, PORT, DEBUG, APP_TITLE

if __name__ == "__main__":
    banner = f"""
================================================================================
  {APP_TITLE}
================================================================================
  Platform Status: Online
  Web Dashboard:      http://{HOST}:{PORT}/
  API Docs (Swagger): http://{HOST}:{PORT}/docs
  ReDoc API Guide:    http://{HOST}:{PORT}/redoc
  Health Check:       http://{HOST}:{PORT}/health

Microservices Loaded:
  * Workers Microservice          -> /api/v1/workers
  * Jobs Microservice             -> /api/v1/jobs
  * Smart Matching Engine         -> /api/v1/match
  * Feeds & Insights Service      -> /api/v1/feeds
  * Location & Geodesic Service   -> /api/v1/location
  * Fair Wage Predictor           -> /api/v1/wage
  * Direct Contact & SMS Bridge   -> /api/v1/contact
  * Regional USSD & IVR Gateway   -> /api/v1/telecom
    [Kannada (ಕನ್ನಡ) & Hindi (हिन्दी) Enabled]
================================================================================
"""
    print(banner)
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
