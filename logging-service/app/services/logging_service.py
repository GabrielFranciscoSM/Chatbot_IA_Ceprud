import os
import logging
import aiofiles
from datetime import datetime
from typing import Optional, List, Any
from app.core.config import settings
from app.core.database import MongoDB
from app.models import (
    ConversationMessage, 
    ConversationDocument,
    SessionEventDocument,
    InteractionAnalyticsDocument,
    LearningEventDocument
)

logger = logging.getLogger(__name__)

class LoggingService:
    """Service for handling MongoDB logging operations with CSV fallback"""
    
    def __init__(self):
        self.base_log_dir = settings.BASE_LOG_DIR
        os.makedirs(self.base_log_dir, exist_ok=True)
        self.use_mongodb = True  # Flag to control MongoDB usage
    
    async def _write_csv_row(self, filename: str, headers: List[str], data: List[Any]):
        """Generic CSV writer helper (legacy support)"""
        log_path = os.path.join(self.base_log_dir, filename)
        file_exists = os.path.exists(log_path)
        
        async with aiofiles.open(log_path, mode="a", newline="", encoding="utf-8") as f:
            if not file_exists:
                await f.write(",".join(headers) + "\n")
            await f.write(",".join(map(str, data)) + "\n")
    
    async def log_session_event(self, session_id: str, user_id: str, subject: str, event_type: str):
        """Log session events to MongoDB"""
        now = datetime.utcnow()
        
        try:
            if self.use_mongodb:
                collection = MongoDB.get_collection("session_events")
                document = SessionEventDocument(
                    session_id=session_id,
                    user_id=user_id,
                    subject=subject,
                    event_type=event_type,
                    timestamp=now
                )
                await collection.insert_one(document.model_dump())
                logger.info(f"Session event logged to MongoDB: {session_id} - {event_type}")
            else:
                # Fallback to CSV
                await self._write_csv_row(
                    "learning_sessions.csv",
                    ["session_id", "user_id", "subject", "event_type", "date", "time", "timestamp"],
                    [session_id, user_id, subject, event_type, 
                     now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
                )
                logger.info(f"Session event logged to CSV: {session_id} - {event_type}")
        except Exception as e:
            logger.error(f"Error logging session event to MongoDB: {e}")
            # Fallback to CSV on error
            await self._write_csv_row(
                "learning_sessions.csv",
                ["session_id", "user_id", "subject", "event_type", "date", "time", "timestamp"],
                [session_id, user_id, subject, event_type, 
                 now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
            )

    async def log_user_message(
        self, session_id: str, user_id_partial: str, subject: str, 
        message_length: int, query_type: str, complexity: str,
        response_length: int, source_count: int, model_used: str
    ):
        """Log user message interactions to MongoDB"""
        now = datetime.utcnow()
        
        try:
            if self.use_mongodb:
                collection = MongoDB.get_collection("interaction_analytics")
                document = InteractionAnalyticsDocument(
                    session_id=session_id,
                    user_id_partial=user_id_partial,
                    subject=subject,
                    message_length=message_length,
                    query_type=query_type,
                    complexity=complexity,
                    response_length=response_length,
                    source_count=source_count,
                    llm_model_used=model_used,
                    timestamp=now
                )
                await collection.insert_one(document.model_dump())
                logger.info(f"User message analytics logged to MongoDB: {session_id}")
            else:
                # Fallback to CSV
                await self._write_csv_row(
                    "chat_interactions_enhanced.csv",
                    ["session_id", "user_id_partial", "subject", "message_length", "query_type", 
                     "complexity", "response_length", "source_count", "model_used", "date", "time", "timestamp"],
                    [session_id, user_id_partial, subject, message_length, query_type, complexity,
                     response_length, source_count, model_used, 
                     now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
                )
                logger.info(f"User message logged to CSV: {session_id}")
        except Exception as e:
            logger.error(f"Error logging user message to MongoDB: {e}")
            # Fallback to CSV on error
            await self._write_csv_row(
                "chat_interactions_enhanced.csv",
                ["session_id", "user_id_partial", "subject", "message_length", "query_type", 
                 "complexity", "response_length", "source_count", "model_used", "date", "time", "timestamp"],
                [session_id, user_id_partial, subject, message_length, query_type, complexity,
                 response_length, source_count, model_used, 
                 now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
            )

    async def log_learning_event(
        self, session_id: str, event_type: str, topic: str, confidence_level: Optional[str] = None
    ):
        """Log learning events to MongoDB"""
        now = datetime.utcnow()
        
        try:
            if self.use_mongodb:
                collection = MongoDB.get_collection("learning_events")
                document = LearningEventDocument(
                    session_id=session_id,
                    event_type=event_type,
                    topic=topic,
                    confidence_level=confidence_level or "N/A",
                    timestamp=now
                )
                await collection.insert_one(document.model_dump())
                logger.info(f"Learning event logged to MongoDB: {session_id} - {event_type}")
            else:
                # Fallback to CSV
                await self._write_csv_row(
                    "learning_events.csv",
                    ["session_id", "event_type", "topic", "confidence_level", "date", "time", "timestamp"],
                    [session_id, event_type, topic, confidence_level or "N/A",
                     now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
                )
                logger.info(f"Learning event logged to CSV: {session_id} - {event_type}")
        except Exception as e:
            logger.error(f"Error logging learning event to MongoDB: {e}")
            # Fallback to CSV on error
            await self._write_csv_row(
                "learning_events.csv",
                ["session_id", "event_type", "topic", "confidence_level", "date", "time", "timestamp"],
                [session_id, event_type, topic, confidence_level or "N/A",
                 now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
            )

    async def log_conversation_message(
        self, session_id: str, user_id: str, subject: str, 
        message_type: str, message_content: str, timestamp: float
    ):
        """
        Log individual conversation messages to MongoDB.
        Creates or updates a conversation document per session.
        """
        conv_datetime = datetime.fromtimestamp(timestamp)
        
        try:
            if self.use_mongodb:
                collection = MongoDB.get_collection("conversations")
                
                # Create message object
                message = ConversationMessage(
                    message_type=message_type,
                    content=message_content,
                    timestamp=conv_datetime
                )
                
                # Try to find existing conversation for this session
                existing = await collection.find_one({"session_id": session_id})
                
                if existing:
                    # Update existing conversation by appending the message
                    await collection.update_one(
                        {"session_id": session_id},
                        {
                            "$push": {"messages": message.model_dump()},
                            "$set": {"updated_at": conv_datetime}
                        }
                    )
                    logger.info(f"Message appended to conversation in MongoDB: {session_id} - {message_type}")
                else:
                    # Create new conversation document
                    conversation = ConversationDocument(
                        session_id=session_id,
                        user_id=user_id,
                        subject=subject,
                        messages=[message],
                        created_at=conv_datetime,
                        updated_at=conv_datetime
                    )
                    await collection.insert_one(conversation.model_dump())
                    logger.info(f"New conversation created in MongoDB: {session_id} - {message_type}")
            else:
                # Fallback to CSV
                escaped_content = message_content.replace('"', '""').replace('\n', '\\n').replace('\r', '\\r')
                await self._write_csv_row(
                    "conversations.csv",
                    ["session_id", "user_id", "subject", "message_type", "message_content", "date", "time", "timestamp"],
                    [session_id, user_id, subject, message_type, f'"{escaped_content}"',
                     conv_datetime.strftime("%Y-%m-%d"), conv_datetime.strftime("%H:%M:%S"), timestamp]
                )
                logger.info(f"Conversation message logged to CSV: {session_id} - {message_type}")
        except Exception as e:
            logger.error(f"Error logging conversation message to MongoDB: {e}")
            # Fallback to CSV on error
            escaped_content = message_content.replace('"', '""').replace('\n', '\\n').replace('\r', '\\r')
            await self._write_csv_row(
                "conversations.csv",
                ["session_id", "user_id", "subject", "message_type", "message_content", "date", "time", "timestamp"],
                [session_id, user_id, subject, message_type, f'"{escaped_content}"',
                 conv_datetime.strftime("%Y-%m-%d"), conv_datetime.strftime("%H:%M:%S"), timestamp]
            )
