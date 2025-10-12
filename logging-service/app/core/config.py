import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration settings for the logging service"""
    
    # Base paths (legacy CSV support)
    BASE_LOG_DIR: str = os.getenv("BASE_LOG_DIR", "/app/logs")
    
    # MongoDB configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "chatbot_logs")
    
    # Service configuration
    service_host: str = "0.0.0.0"
    service_port: int = 8002
    
    # Logging configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
