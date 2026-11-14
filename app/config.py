import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "bluecollar.db"))

APP_TITLE = "KaayakaSetu (ಕಾಯಕಸೇತು / श्रमसेतु) - Blue Collar Work Platform"
APP_DESCRIPTION = (
    "Microservice platform connecting blue-collar workers and employers with "
    "smart job matching, fair wage prediction, location proximity, and Kannada/Hindi USSD & IVR services."
)
APP_VERSION = "1.0.0"

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Default search radius in kilometers
DEFAULT_RADIUS_KM = 25.0
MAX_RADIUS_KM = 100.0
