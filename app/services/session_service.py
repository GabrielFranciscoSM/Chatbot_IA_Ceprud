"""
Session management service.

This module handles:
- User session creation and management
- Session tracking and timeout handling
- Session cleanup and maintenance
"""

import time
import uuid
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Session management for learning analytics
active_sessions: Dict[str, Dict] = {}

# Configuration
SESSION_TIMEOUT_SECONDS = 30 * 60  # 30 minutes


def get_or_create_session(user_email: str, subject: str) -> str:
    """
    Get existing session ID or create a new one for the user.
    Sessions are tied to email + subject combination.
    
    Args:
        user_email: User's email address
        subject: Subject/course name
        
    Returns:
        Session ID string
    """
    session_key = f"{user_email}_{subject}"
    current_time = time.time()
    
    # Check if we have an active session for this user+subject
    if session_key in active_sessions:
        last_activity = active_sessions[session_key]['last_activity']
        if current_time - last_activity < SESSION_TIMEOUT_SECONDS:
            active_sessions[session_key]['last_activity'] = current_time
            return active_sessions[session_key]['session_id']
    
    # Create new session
    session_id = str(uuid.uuid4())
    active_sessions[session_key] = {
        'session_id': session_id,
        'email': user_email,
        'subject': subject,
        'created': current_time,
        'last_activity': current_time,
        'message_count': 0
    }
    
    logger.info(f"Created new session for user {user_email[:8]}... in subject {subject}")
    return session_id


def update_session_activity(user_email: str, subject: str) -> Optional[str]:
    """
    Update session activity and increment message count.
    
    Args:
        user_email: User's email address
        subject: Subject/course name
        
    Returns:
        Session ID if session exists, None otherwise
    """
    session_key = f"{user_email}_{subject}"
    
    if session_key in active_sessions:
        active_sessions[session_key]['message_count'] += 1
        active_sessions[session_key]['last_activity'] = time.time()
        return active_sessions[session_key]['session_id']
    
    return None


def get_session_info(session_id: str) -> Optional[Dict]:
    """
    Get session information by session ID.
    
    Args:
        session_id: Session ID to look up
        
    Returns:
        Session information dict or None if not found
    """
    for session_data in active_sessions.values():
        if session_data['session_id'] == session_id:
            return session_data.copy()
    return None


def cleanup_old_sessions() -> int:
    """
    Remove sessions that have been inactive for too long.
    
    Returns:
        Number of sessions cleaned up
    """
    if len(active_sessions) <= 10:  # Only cleanup when we have many sessions
        return 0
        
    current_time = time.time()
    sessions_to_remove = []
    
    for session_key, session_data in active_sessions.items():
        if current_time - session_data['last_activity'] > SESSION_TIMEOUT_SECONDS:
            sessions_to_remove.append(session_key)
    
    for session_key in sessions_to_remove:
        logger.info(f"Cleaning up inactive session: {active_sessions[session_key]['session_id']}")
        del active_sessions[session_key]
    
    logger.info(f"Cleaned up {len(sessions_to_remove)} inactive sessions")
    return len(sessions_to_remove)


def get_active_sessions_count() -> int:
    """
    Get the current number of active sessions.
    
    Returns:
        Number of active sessions
    """
    return len(active_sessions)


def get_all_sessions() -> Dict[str, Dict]:
    """
    Get all active sessions (for debugging/monitoring).
    
    Returns:
        Copy of all active sessions
    """
    return active_sessions.copy()
