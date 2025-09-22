import os
import logging
import aiofiles
from datetime import datetime
from typing import Optional, List, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class LoggingService:
    """Simplified service for handling CSV logging operations"""
    
    def __init__(self):
        self.base_log_dir = settings.BASE_LOG_DIR
        os.makedirs(self.base_log_dir, exist_ok=True)
    
    async def _write_csv_row(self, filename: str, headers: List[str], data: List[Any]):
        """Generic CSV writer helper"""
        log_path = os.path.join(self.base_log_dir, filename)
        file_exists = os.path.exists(log_path)
        
        async with aiofiles.open(log_path, mode="a", newline="", encoding="utf-8") as f:
            if not file_exists:
                await f.write(",".join(headers) + "\n")
            await f.write(",".join(map(str, data)) + "\n")
    
    async def log_session_event(self, session_id: str, user_id: str, subject: str, event_type: str):
        """Log session events"""
        now = datetime.now()
        await self._write_csv_row(
            "learning_sessions.csv",
            ["session_id", "user_id", "subject", "event_type", "date", "time", "timestamp"],
            [session_id, user_id, subject, event_type, 
             now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
        )
        logger.info(f"Session event logged: {session_id} - {event_type}")

    async def log_user_message(
        self, session_id: str, user_id_partial: str, subject: str, 
        message_length: int, query_type: str, complexity: str,
        response_length: int, source_count: int, model_used: str
    ):
        """Log user message interactions"""
        now = datetime.now()
        await self._write_csv_row(
            "chat_interactions_enhanced.csv",
            ["session_id", "user_id_partial", "subject", "message_length", "query_type", 
             "complexity", "response_length", "source_count", "model_used", "date", "time", "timestamp"],
            [session_id, user_id_partial, subject, message_length, query_type, complexity,
             response_length, source_count, model_used, 
             now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
        )
        logger.info(f"User message logged: {session_id}")

    async def log_learning_event(
        self, session_id: str, event_type: str, topic: str, confidence_level: Optional[str] = None
    ):
        """Log learning events"""
        now = datetime.now()
        await self._write_csv_row(
            "learning_events.csv",
            ["session_id", "event_type", "topic", "confidence_level", "date", "time", "timestamp"],
            [session_id, event_type, topic, confidence_level or "N/A",
             now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), now.timestamp()]
        )
        logger.info(f"Learning event logged: {session_id} - {event_type}")
