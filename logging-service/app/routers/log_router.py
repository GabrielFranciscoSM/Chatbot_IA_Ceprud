from fastapi import APIRouter, HTTPException, Depends
from app.models import SessionEventLog, UserMessageLog, LearningEventLog, ConversationMessageLog, LogResponse
from app.services.logging_service import LoggingService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["logging"])

def get_logging_service() -> LoggingService:
    """Get logging service instance"""
    return LoggingService()

async def handle_log_request(log_func, success_msg: str, **kwargs):
    """Generic log request handler"""
    try:
        await log_func(**kwargs)
        return LogResponse(success=True, message=success_msg, timestamp=datetime.now())
    except Exception as e:
        logger.error(f"Logging error: {e}")
        raise HTTPException(status_code=500, detail="Failed to log event")

@router.post("/logs/session-event", response_model=LogResponse)
async def log_session_event(
    event: SessionEventLog,
    logging_service: LoggingService = Depends(get_logging_service)
):
    """Log a session event"""
    return await handle_log_request(
        logging_service.log_session_event,
        "Session event logged successfully",
        session_id=event.session_id,
        user_id=event.user_id,
        subject=event.subject,
        event_type=event.event_type
    )

@router.post("/logs/user-message", response_model=LogResponse)
async def log_user_message(
    message: UserMessageLog,
    logging_service: LoggingService = Depends(get_logging_service)
):
    """Log a user message"""
    return await handle_log_request(
        logging_service.log_user_message,
        "User message logged successfully",
        session_id=message.session_id,
        user_id_partial=message.user_id_partial,
        subject=message.subject,
        message_length=message.message_length,
        query_type=message.query_type,
        complexity=message.complexity,
        response_length=message.response_length,
        source_count=message.source_count,
        model_used=message.llm_model_used
    )

@router.post("/logs/learning-event", response_model=LogResponse)
async def log_learning_event(
    event: LearningEventLog,
    logging_service: LoggingService = Depends(get_logging_service)
):
    """Log a learning event"""
    return await handle_log_request(
        logging_service.log_learning_event,
        "Learning event logged successfully",
        session_id=event.session_id,
        event_type=event.event_type,
        topic=event.topic,
        confidence_level=event.confidence_level
    )

@router.post("/logs/conversation-message", response_model=LogResponse)
async def log_conversation_message(
    message: ConversationMessageLog,
    logging_service: LoggingService = Depends(get_logging_service)
):
    """Log a conversation message (user or bot)"""
    return await handle_log_request(
        logging_service.log_conversation_message,
        "Conversation message logged successfully",
        session_id=message.session_id,
        user_id=message.user_id,
        subject=message.subject,
        message_type=message.message_type,
        message_content=message.message_content,
        timestamp=message.timestamp
    )

@router.get("/logs/health")
async def logging_health():
    """Health check for logging service"""
    return {"status": "healthy", "service": "logging", "timestamp": datetime.now()}
