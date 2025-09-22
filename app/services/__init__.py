"""
Services package for the chatbot application.

This package contains all business service modules:
- session_service: User session management
- logging_service: Microservice-based logging
- utils_service: Utility functions and query analysis helpers
"""

from .session_service import (
    get_or_create_session,
    update_session_activity,
    cleanup_old_sessions,
    get_session_info,
    get_active_sessions_count,
    active_sessions
)

from .logging_service import (
    log_session_event_sync as log_session_event,
    log_request_info,
    log_user_message_sync as log_user_message,
    log_learning_event_sync as log_learning_event,
)

from .utils_service import (
    classify_query_type,
    estimate_query_complexity,
    anonymize_user_id,
    sanitize_input,
    format_sources_list,
    truncate_text
)

__all__ = [
    # Session service
    'get_or_create_session',
    'update_session_activity', 
    'cleanup_old_sessions',
    'get_session_info',
    'get_active_sessions_count',
    'active_sessions',
    
    # Logging service (microservice-based)
    'log_session_event',
    'log_request_info',
    'log_user_message',
    'log_learning_event',
    
    # Utils service (includes query analysis)
    'classify_query_type',
    'estimate_query_complexity',
    'anonymize_user_id',
    'sanitize_input',
    'format_sources_list',
    'truncate_text'
]
