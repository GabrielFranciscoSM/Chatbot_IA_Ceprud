"""
Logging service client for communicating with the external logging microservice.

This module replaces direct file-based logging with HTTP calls to the logging service API.
"""

import os
import time
import logging
from typing import List, Optional
import httpx
from fastapi import Request

logger = logging.getLogger(__name__)

# Get logging service URL from environment
LOGGING_SERVICE_URL = os.getenv("LOGGING_SERVICE_URL", "http://localhost:8083")
LOGGING_API_BASE = f"{LOGGING_SERVICE_URL}/api/v1/logs"

# Timeout configuration for logging requests
LOGGING_TIMEOUT = 5.0


async def log_session_event(session_id: str, user_id: str, subject: str, event_type: str):
    """
    Log session-related events via the logging service API.
    
    Args:
        session_id: Session identifier
        user_id: Anonymized user identifier  
        subject: Subject/course name
        event_type: Type of session event
    """
    try:
        async with httpx.AsyncClient(timeout=LOGGING_TIMEOUT) as client:
            payload = {
                "session_id": session_id,
                "user_id": user_id,
                "subject": subject,
                "event_type": event_type
            }
            response = await client.post(
                f"{LOGGING_API_BASE}/session-event",
                json=payload
            )
            response.raise_for_status()
            logger.debug(f"Session event logged successfully: {event_type}")
    except httpx.TimeoutException:
        logger.warning(f"Timeout logging session event: {event_type}")
    except httpx.HTTPError as e:
        logger.warning(f"HTTP error logging session event: {e}")
    except Exception as e:
        logger.error(f"Unexpected error logging session event: {e}")


async def log_user_message(email: str, message: str, subject: str, response: str, sources: List[str], 
                          session_id: str, query_type: str, complexity: str, model_used: str):
    """
    Log comprehensive user interaction data via the logging service API.
    
    Args:
        email: User email (will be anonymized)
        message: User's message
        subject: Subject/course
        response: Bot's response  
        sources: Source documents used
        session_id: Session identifier
        query_type: Classified query type
        complexity: Estimated query complexity
        model_used: Model used for response
    """
    try:
        async with httpx.AsyncClient(timeout=LOGGING_TIMEOUT) as client:
            payload = {
                "session_id": session_id,
                "user_id_partial": email[:8] + "...",  # Partial anonymization
                "subject": subject,
                "message_length": len(message),
                "query_type": query_type,
                "complexity": complexity,
                "response_length": len(response),
                "source_count": len(sources),
                "llm_model_used": model_used  # Changed from model_used to match logging service
            }
            response = await client.post(
                f"{LOGGING_API_BASE}/user-message",
                json=payload
            )
            response.raise_for_status()
            logger.debug(f"User message logged successfully for session: {session_id}")
    except httpx.TimeoutException:
        logger.warning(f"Timeout logging user message for session: {session_id}")
    except httpx.HTTPError as e:
        logger.warning(f"HTTP error logging user message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error logging user message: {e}")


async def log_learning_event(session_id: str, event_type: str, topic: str, confidence_level: Optional[str] = None):
    """
    Log learning-related events via the logging service API.
    
    Args:
        session_id: Session identifier
        event_type: Type of learning event
        topic: Topic or subject matter
        confidence_level: Confidence level if applicable
    """
    try:
        async with httpx.AsyncClient(timeout=LOGGING_TIMEOUT) as client:
            payload = {
                "session_id": session_id,
                "event_type": event_type,
                "topic": topic,
                "confidence_level": confidence_level or "N/A"
            }
            response = await client.post(
                f"{LOGGING_API_BASE}/learning-event",
                json=payload
            )
            response.raise_for_status()
            logger.debug(f"Learning event logged successfully: {event_type}")
    except httpx.TimeoutException:
        logger.warning(f"Timeout logging learning event: {event_type}")
    except httpx.HTTPError as e:
        logger.warning(f"HTTP error logging learning event: {e}")
    except Exception as e:
        logger.error(f"Unexpected error logging learning event: {e}")


def log_request_info(request: Request, start_time: float, status_code: int, response_size: int = 0):
    """
    Log request information for performance monitoring.
    
    This function remains synchronous and uses the standard Python logger
    since it's for internal performance monitoring, not business analytics.
    
    Args:
        request: FastAPI request object
        start_time: Request start timestamp
        status_code: HTTP response status code
        response_size: Size of response in bytes
    """
    duration = time.time() - start_time
    
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Status: {status_code} | "
        f"Duration: {duration:.3f}s | "
        f"Size: {response_size} bytes"
    )


# Import helper functions from analytics_service for backward compatibility
from services.analytics_service import classify_query_type, estimate_query_complexity


async def log_conversation_message(session_id: str, user_id: str, subject: str, 
                                 message_type: str, message_content: str, timestamp: float = None):
    """
    Log individual conversation messages (both user and bot messages).
    
    This creates a detailed conversation log separate from the analytics data.
    
    Args:
        session_id: Session identifier
        user_id: Anonymized user identifier  
        subject: Subject/course name
        message_type: 'user' or 'bot'
        message_content: The actual message content
        timestamp: Optional timestamp (uses current time if not provided)
    """
    try:
        if timestamp is None:
            timestamp = time.time()
            
        async with httpx.AsyncClient(timeout=LOGGING_TIMEOUT) as client:
            payload = {
                "session_id": session_id,
                "user_id": user_id,
                "subject": subject,
                "message_type": message_type,
                "message_content": message_content,
                "timestamp": timestamp
            }
            response = await client.post(
                f"{LOGGING_API_BASE}/conversation-message",
                json=payload
            )
            response.raise_for_status()
            logger.debug(f"Conversation message logged successfully: {message_type}")
    except httpx.TimeoutException:
        logger.warning(f"Timeout logging conversation message for session: {session_id}")
    except httpx.HTTPError as e:
        logger.warning(f"HTTP error logging conversation message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error logging conversation message: {e}")


# Legacy sync wrappers for backward compatibility
# These will be deprecated once all callers are updated to async
def log_session_event_sync(session_id: str, user_id: str, subject: str, event_type: str):
    """Legacy sync wrapper - use async version instead."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we can't use run()
            logger.warning("sync log_session_event called from async context")
            return
        else:
            loop.run_until_complete(log_session_event(session_id, user_id, subject, event_type))
    except RuntimeError:
        # No event loop, create one
        asyncio.run(log_session_event(session_id, user_id, subject, event_type))


def log_user_message_sync(email: str, message: str, subject: str, response: str, sources: List[str], 
                         session_id: str, query_type: str, complexity: str, model_used: str):
    """Legacy sync wrapper - use async version instead."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            logger.warning("sync log_user_message called from async context")
            return
        else:
            loop.run_until_complete(log_user_message(email, message, subject, response, sources,
                                                   session_id, query_type, complexity, model_used))
    except RuntimeError:
        asyncio.run(log_user_message(email, message, subject, response, sources,
                                   session_id, query_type, complexity, model_used))


def log_learning_event_sync(session_id: str, event_type: str, topic: str, confidence_level: Optional[str] = None):
    """Legacy sync wrapper - use async version instead.""" 
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            logger.warning("sync log_learning_event called from async context")
            return
        else:
            loop.run_until_complete(log_learning_event(session_id, event_type, topic, confidence_level))
    except RuntimeError:
        asyncio.run(log_learning_event(session_id, event_type, topic, confidence_level))


def log_conversation_message_sync(session_id: str, user_id: str, subject: str, 
                                 message_type: str, message_content: str, timestamp: float = None):
    """Legacy sync wrapper - use async version instead."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            logger.warning("sync log_conversation_message called from async context")
            return
        else:
            loop.run_until_complete(log_conversation_message(session_id, user_id, subject, 
                                                           message_type, message_content, timestamp))
    except RuntimeError:
        asyncio.run(log_conversation_message(session_id, user_id, subject, 
                                           message_type, message_content, timestamp))
