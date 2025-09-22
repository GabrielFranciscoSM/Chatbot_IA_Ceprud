from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionEventLog(BaseModel):
    """Model for session event logging - matches analytics_service.log_session_event"""
    session_id: str
    user_id: str
    subject: str
    event_type: str

class UserMessageLog(BaseModel):
    """Model for user message logging - matches analytics_service.log_user_message"""
    session_id: str
    user_id_partial: str  # Anonymized email (first 8 chars + "...")
    subject: str
    message_length: int
    query_type: str
    complexity: str
    response_length: int
    source_count: int
    llm_model_used: str  # Changed from model_used to avoid Pydantic namespace conflict

class LearningEventLog(BaseModel):
    """Model for learning event logging - matches analytics_service.log_learning_event"""
    session_id: str
    event_type: str
    topic: str
    confidence_level: Optional[str] = "N/A"

class ConversationMessageLog(BaseModel):
    """Model for conversation message logging - stores actual conversation content"""
    session_id: str
    user_id: str
    subject: str
    message_type: str  # 'user' or 'bot'
    message_content: str
    timestamp: float

class LogResponse(BaseModel):
    """Standard response model for logging endpoints"""
    success: bool
    message: str
    timestamp: datetime
