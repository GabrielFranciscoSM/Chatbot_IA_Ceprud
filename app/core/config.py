"""
Configuration module for the chatbot API.

This module handles:
- Environment variable loading and validation
- Logging configuration setup
- Path configuration and directory creation
- Application constants
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Path Configuration ---
BASE_CHROMA_PATH = os.getenv("BASE_CHROMA_PATH", "rag/chroma")
BASE_LOG_DIR = os.getenv("BASE_LOG_DIR", "storage/logs")

# --- Application Constants ---
API_VERSION = "1.0.0"
SESSION_TIMEOUT_MINUTES = 30
MAX_MESSAGE_LENGTH = 1000
DEFAULT_SUBJECT = "default"
DEFAULT_EMAIL = "anonimo"

# --- Logging Configuration ---
def setup_logging():
    """
    Configure logging for the application.
    
    Sets up both file and console logging with appropriate formatting.
    """
    # Ensure logs directory exists
    os.makedirs(BASE_LOG_DIR, exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(BASE_LOG_DIR, 'api.log')),
            logging.StreamHandler()
        ]
    )
    
    # Set specific log levels for third-party libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def ensure_directories():
    """
    Ensure all required directories exist.
    """
    directories = [
        BASE_LOG_DIR,
        BASE_CHROMA_PATH,
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_config() -> dict:
    """
    Get all configuration as a dictionary.
    
    Returns:
        dict: Configuration dictionary with all settings
    """
    return {
        "base_chroma_path": BASE_CHROMA_PATH,
        "base_log_dir": BASE_LOG_DIR,
        "api_version": API_VERSION,
        "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,
        "max_message_length": MAX_MESSAGE_LENGTH,
        "default_subject": DEFAULT_SUBJECT,
        "default_email": DEFAULT_EMAIL,
    }


# Initialize configuration on import
setup_logging()
ensure_directories()
