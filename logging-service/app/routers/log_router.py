from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import SessionEventLog, UserMessageLog, LearningEventLog, ConversationMessageLog, LogResponse
from app.services.logging_service import LoggingService
from app.core.database import MongoDB
from datetime import datetime
from typing import List, Optional
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
        return LogResponse(success=True, message=success_msg, timestamp=datetime.utcnow())
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
    return {"status": "healthy", "service": "logging", "timestamp": datetime.utcnow()}


# New endpoints for querying conversations from MongoDB

@router.get("/conversations/{session_id}")
async def get_conversation_by_session(session_id: str):
    """
    Get a complete conversation by session ID.
    Returns all messages for a specific session.
    """
    try:
        collection = MongoDB.get_collection("conversations")
        conversation = await collection.find_one({"session_id": session_id})
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Convert ObjectId to string
        conversation["_id"] = str(conversation["_id"])
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")


@router.get("/conversations/user/{user_id}")
async def get_conversations_by_user(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all conversations for a specific user.
    Supports pagination.
    """
    try:
        collection = MongoDB.get_collection("conversations")
        cursor = collection.find({"user_id": user_id}).skip(skip).limit(limit).sort("created_at", -1)
        
        conversations = []
        async for conv in cursor:
            conv["_id"] = str(conv["_id"])
            conversations.append(conv)
        
        return {
            "user_id": user_id,
            "count": len(conversations),
            "conversations": conversations
        }
    except Exception as e:
        logger.error(f"Error retrieving user conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations")


@router.get("/conversations/subject/{subject}")
async def get_conversations_by_subject(
    subject: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all conversations for a specific subject.
    Supports pagination.
    """
    try:
        collection = MongoDB.get_collection("conversations")
        cursor = collection.find({"subject": subject}).skip(skip).limit(limit).sort("created_at", -1)
        
        conversations = []
        async for conv in cursor:
            conv["_id"] = str(conv["_id"])
            conversations.append(conv)
        
        return {
            "subject": subject,
            "count": len(conversations),
            "conversations": conversations
        }
    except Exception as e:
        logger.error(f"Error retrieving subject conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations")


@router.get("/analytics/sessions")
async def get_session_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    subject: Optional[str] = None
):
    """
    Get analytics data for sessions.
    Optionally filter by date range and subject.
    """
    try:
        collection = MongoDB.get_collection("session_events")
        
        # Build filter query
        query = {}
        if subject:
            query["subject"] = subject
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date)
        
        # Get events
        cursor = collection.find(query).sort("timestamp", -1)
        events = []
        async for event in cursor:
            event["_id"] = str(event["_id"])
            events.append(event)
        
        return {
            "count": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Error retrieving session analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@router.get("/analytics/interactions")
async def get_interaction_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    subject: Optional[str] = None
):
    """
    Get analytics data for user interactions.
    Optionally filter by date range and subject.
    """
    try:
        collection = MongoDB.get_collection("interaction_analytics")
        
        # Build filter query
        query = {}
        if subject:
            query["subject"] = subject
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date)
        
        # Get interactions
        cursor = collection.find(query).sort("timestamp", -1)
        interactions = []
        async for interaction in cursor:
            interaction["_id"] = str(interaction["_id"])
            interactions.append(interaction)
        
        return {
            "count": len(interactions),
            "interactions": interactions
        }
    except Exception as e:
        logger.error(f"Error retrieving interaction analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")
