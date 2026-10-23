import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")

# Model Configuration
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "smart-industrial-edge-ai-dev")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Engine Settings
MAX_GENERATION_WORKERS = int(os.getenv("MAX_GENERATION_WORKERS", "4"))
DEFAULT_BASE_URL = os.getenv("DEFAULT_BASE_URL", "https://incubrix.com")
CAMPAIGN_NAME = os.getenv("CAMPAIGN_NAME", "growth_engine_q1")

# Directories
DATA_DIR = BASE_DIR / "data"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = DATA_DIR / "outputs"
ASSETS_DIR = BASE_DIR / "assets"
FINAL_ASSETS_DIR = ASSETS_DIR / "final"
SOURCE_ASSETS_DIR = ASSETS_DIR / "source"
TEMPLATES_DIR = ASSETS_DIR / "templates"

# Ensure runtime directories exist
for path in [INPUTS_DIR, OUTPUTS_DIR, FINAL_ASSETS_DIR, SOURCE_ASSETS_DIR, TEMPLATES_DIR]:
    path.mkdir(parents=True, exist_ok=True)
