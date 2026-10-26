import os
from pathlib import Path

from dotenv import load_dotenv


# ==========================================
# LOAD ENVIRONMENT CONFIGURATION
# ==========================================
# Load .env from the main project folder.
PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


# ==========================================
# PRODUCTION CONFIGURATION CHECK
# ==========================================
# Production must never use fallback credentials.

REQUIRED_ENV_VARS = (
    "FLASK_SECRET_KEY",
    "SAINTS_MASTER_USERNAME",
    "SAINTS_MASTER_PASSWORD",
)

missing = [
    name for name in REQUIRED_ENV_VARS
    if not os.environ.get(name)
]

if missing:
    missing_text = ", ".join(missing)
    raise SystemExit(
        "Production server cannot start because these environment "
        f"variables are missing: {missing_text}. "
        "Configure them in the project-root .env file."
    )

secret_key = os.environ["FLASK_SECRET_KEY"]

if len(secret_key) < 32:
    raise SystemExit(
        "Production server cannot start: FLASK_SECRET_KEY must be "
        "at least 32 characters long."
    )

master_password = os.environ["SAINTS_MASTER_PASSWORD"]

if len(master_password) < 8:
    raise SystemExit(
        "Production server cannot start: SAINTS_MASTER_PASSWORD "
        "must be at least 8 characters long."
    )


from waitress import serve
from app import app


# ==========================================
# PRODUCTION SERVER CONFIGURATION
# ==========================================
HOST = os.environ.get("SAINTS_HOST", "0.0.0.0")
PORT = int(os.environ.get("SAINTS_PORT", "5000"))
THREADS = int(os.environ.get("SAINTS_THREADS", "16"))

# Preserve the existing minimum worker requirement.
if THREADS < 8:
    raise SystemExit(
        "Production server cannot start: SAINTS_THREADS must be "
        "at least 8 because Saints Gym uses a long-lived dashboard "
        "event connection."
    )


if __name__ == "__main__":
    print(f"Saints Gym production server starting on http://{HOST}:{PORT}")
    print(f"Waitress worker threads: {THREADS}")

    serve(
        app,
        host=HOST,
        port=PORT,
        threads=THREADS,
    )