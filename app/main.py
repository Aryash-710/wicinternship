from contextlib import asynccontextmanager
from pathlib import Path
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from app.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from app.database import init_db
from app.routers import (
    workers,
    jobs,
    matching,
    feeds,
    location,
    wage,
    contact,
    telecom,
    auth
)

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("KaayakaSetu")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing KaayakaSetu Database...")
    init_db()
    logger.info("Database and sample datasets initialized successfully!")
    yield
    logger.info("Shutting down KaayakaSetu services...")


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Microservice Routers
app.include_router(workers.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(feeds.router)
app.include_router(location.router)
app.include_router(wage.router)
app.include_router(contact.router)
app.include_router(telecom.router)
app.include_router(auth.router)

# Mount Static Files for Dashboard UI
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_ui():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "platform": APP_TITLE,
        "status": "online",
        "documentation": "/docs",
        "version": APP_VERSION
    }


@app.get("/login", include_in_schema=False)
async def serve_login():
    return RedirectResponse(url="/", status_code=302)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "services": {
            "workers": "UP",
            "jobs": "UP",
            "matching": "UP",
            "feeds": "UP",
            "location": "UP",
            "wage_prediction": "UP",
            "contact": "UP",
            "ivr_telecom": "UP",
            "auth": "UP"
        }
    }
