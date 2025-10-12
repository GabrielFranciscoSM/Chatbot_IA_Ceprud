from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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


# MongoDB Document Models

class ConversationMessage(BaseModel):
    """Individual message in a conversation"""
    message_type: str  # 'user' or 'bot'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ConversationDocument(BaseModel):
    """MongoDB document for storing complete conversations per session"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    subject: str = Field(..., description="Subject/course name")
    messages: List[ConversationMessage] = Field(default_factory=list, description="List of messages in conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Conversation start time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last message time")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class SessionEventDocument(BaseModel):
    """MongoDB document for session events"""
    session_id: str
    user_id: str
    subject: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class InteractionAnalyticsDocument(BaseModel):
    """MongoDB document for interaction analytics"""
    session_id: str
    user_id_partial: str
    subject: str
    message_length: int
    query_type: str
    complexity: str
    response_length: int
    source_count: int
    llm_model_used: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class LearningEventDocument(BaseModel):
    """MongoDB document for learning events"""
    session_id: str
    event_type: str
    topic: str
    confidence_level: str = "N/A"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
