"""
Services package for the chatbot application.

This package contains all business service modules:
- session_service: User session management
- analytics_service: Logging and analytics
- utils_service: Utility functions
"""

from .session_service import (
    get_or_create_session,
    update_session_activity,
    cleanup_old_sessions,
    get_session_info,
    get_active_sessions_count,
    active_sessions
)

from .analytics_service import (
    log_session_event,
    log_request_info,
    log_user_message,
    log_learning_event,
    classify_query_type,
    estimate_query_complexity
)

from .utils_service import (
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
    
    # Analytics service
    'log_session_event',
    'log_request_info',
    'log_user_message',
    'log_learning_event',
    'classify_query_type',
    'estimate_query_complexity',
    
    # Utils service
    'anonymize_user_id',
    'sanitize_input',
    'format_sources_list',
    'truncate_text'
]
