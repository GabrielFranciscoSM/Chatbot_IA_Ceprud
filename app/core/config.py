"""
Minimal configuration constants for the chatbot API.
No logging setup - using logging service microservice.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Application Constants ---
API_VERSION = "1.0.0"
SESSION_TIMEOUT_MINUTES = 30
MAX_MESSAGE_LENGTH = 1000
DEFAULT_SUBJECT = "default"
DEFAULT_EMAIL = "anonimo"

# --- Path Configuration ---
BASE_CHROMA_PATH = os.getenv("BASE_CHROMA_PATH", "rag/chroma")

# --- Logging Service Configuration ---
LOGGING_SERVICE_URL = os.getenv("LOGGING_SERVICE_URL", "http://localhost:8083")
LOGGING_TIMEOUT = float(os.getenv("LOGGING_TIMEOUT", "5.0"))

# --- Deprecated/Legacy ---
# Only kept for backward compatibility - not used for actual logging
BASE_LOG_DIR = "storage/logs"  # Legacy, not used

def ensure_directories():
    """Ensure required directories exist."""
    os.makedirs(BASE_CHROMA_PATH, exist_ok=True)

def get_config() -> dict:
    """Get configuration as dictionary."""
    return {
        "api_version": API_VERSION,
        "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,
        "max_message_length": MAX_MESSAGE_LENGTH,
        "default_subject": DEFAULT_SUBJECT,
        "default_email": DEFAULT_EMAIL,
        "base_chroma_path": BASE_CHROMA_PATH,
        "logging_service_url": LOGGING_SERVICE_URL,
        "logging_timeout": LOGGING_TIMEOUT,
    }

# No logging setup - using microservice
def setup_logging():
    """Deprecated - logging handled by microservice."""
    pass

# Initialize on import
ensure_directories()
