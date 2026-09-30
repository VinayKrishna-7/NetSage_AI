"""
config.py
==============================================================================
NetSage AI - Configuration and Environment Settings
==============================================================================
Centralizes all directory paths, operational modes (Mock vs. API),
confidence thresholds, and human-in-the-loop review categories.
Works seamlessly across Windows, Linux, and macOS using pathlib.Path.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory (directory containing config.py)
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if available
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# -----------------------------------------------------------------------------
# Directory & File Paths
# -----------------------------------------------------------------------------
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"
DASHBOARD_DIR = BASE_DIR / "dashboard"
TESTS_DIR = BASE_DIR / "tests"
DOCS_DIR = BASE_DIR / "docs"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Key file paths
CASES_FILE = DATA_DIR / "cases.csv"
RESPONSIBLE_AI_LOG_FILE = DATA_DIR / "responsible_ai_log.csv"
REVIEWS_FILE = DATA_DIR / "reviews.csv"
DIAGNOSE_PROMPT_FILE = PROMPTS_DIR / "diagnose_prompt.md"
HELPER_PROMPTS_FILE = PROMPTS_DIR / "helper_prompts.md"
SAMPLE_OUTPUTS_FILE = TESTS_DIR / "sample_outputs.txt"

# -----------------------------------------------------------------------------
# AI Engine Configuration
# -----------------------------------------------------------------------------
# Operational modes: 'mock' (offline demo, zero-cost) or 'api' (requires LLM API key)
NETSAGE_MODE = os.getenv("NETSAGE_MODE", "mock").strip().lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
NETSAGE_MODEL = os.getenv("NETSAGE_MODEL", "gpt-4o-mini").strip()

# -----------------------------------------------------------------------------
# Safety & Policy Rules
# -----------------------------------------------------------------------------
SAFETY_DISCLAIMER = (
    "AI diagnosis is advisory. A human reviewer must verify the evidence before accepting any fix."
)
EXECUTION_POLICY = "Automatic configuration changes are strictly prohibited."

# Allowed confidence values & score range
ALLOWED_CONFIDENCE = ["LOW", "MEDIUM", "HIGH"]
MIN_CONFIDENCE_SCORE = 0
MAX_CONFIDENCE_SCORE = 100

# Review decisions
REVIEW_STATUS_ACCEPTED = "ACCEPTED"
REVIEW_STATUS_EDITED = "EDITED"
REVIEW_STATUS_REJECTED = "REJECTED"
ALLOWED_REVIEW_DECISIONS = [
    REVIEW_STATUS_ACCEPTED,
    REVIEW_STATUS_EDITED,
    REVIEW_STATUS_REJECTED,
]

# Networking Fault Categories & OSI Layer Mappings
FAULT_CATEGORIES = [
    "VLAN",
    "Default Gateway",
    "DHCP",
    "DNS",
    "Routing",
    "ACL",
    "NAT",
    "Wireless / Guest Wi-Fi",
    "Interface / Switchport",
    "Trunking",
]

OSI_LAYERS = [
    "Layer 1 - Physical",
    "Layer 2 - Data Link",
    "Layer 3 - Network",
    "Layer 4 - Transport",
    "Layer 7 - Application",
]

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def is_mock_mode() -> bool:
    """Return True if running in offline mock demo mode."""
    return NETSAGE_MODE != "api" or not OPENAI_API_KEY
