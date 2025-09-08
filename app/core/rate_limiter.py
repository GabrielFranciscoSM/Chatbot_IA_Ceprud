"""
Rate limiting functionality for the API.

This module provides in-memory rate limiting capabilities with:
- Per-user request counting
- Sliding window implementation
- Configurable limits and time windows
- Request status checking
- Automatic cleanup of old entries
"""

import os
import time
import logging
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# --- Rate Limiting Configuration ---
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "20"))  # 20 requests per minute
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))      # 60 seconds window

# --- Rate Limiting State ---
# In-memory rate limiting storage (requests per minute per user)
rate_limit_storage: Dict[str, Dict] = {}


def check_rate_limit(user_identifier: str) -> bool:
    """
    Simple rate limiting: Allow max X requests per minute per user.
    Returns True if request is allowed, False if rate limited.
    
    Args:
        user_identifier: Unique identifier for the user (e.g., hashed email)
        
    Returns:
        bool: True if request is allowed, False if rate limited
    """
    current_time = time.time()
    
    # Clean up old entries (older than rate limit window)
    cleanup_time = current_time - RATE_LIMIT_WINDOW
    users_to_remove = []
    
    for user_id, data in rate_limit_storage.items():
        # Remove old requests outside the time window
        data['requests'] = [req_time for req_time in data['requests'] if req_time > cleanup_time]
        if not data['requests']:
            users_to_remove.append(user_id)
    
    # Clean up empty users
    for user_id in users_to_remove:
        del rate_limit_storage[user_id]
    
    # Check current user's rate limit
    if user_identifier not in rate_limit_storage:
        rate_limit_storage[user_identifier] = {'requests': []}
    
    user_requests = rate_limit_storage[user_identifier]['requests']
    
    # Count requests in current window
    recent_requests = [req_time for req_time in user_requests if req_time > cleanup_time]
    
    if len(recent_requests) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for user: {user_identifier[:8]}... ({len(recent_requests)} requests)")
        return False
    
    # Add current request
    user_requests.append(current_time)
    rate_limit_storage[user_identifier]['requests'] = user_requests
    
    return True


def get_rate_limit_info(user_identifier: str) -> Dict[str, int]:
    """
    Get rate limit information for a user.
    
    Args:
        user_identifier: Unique identifier for the user
        
    Returns:
        Dict containing requests_made, requests_remaining, and reset_time
    """
    current_time = time.time()
    cleanup_time = current_time - RATE_LIMIT_WINDOW
    
    if user_identifier not in rate_limit_storage:
        return {
            "requests_made": 0,
            "requests_remaining": RATE_LIMIT_REQUESTS,
            "reset_time": int(current_time + RATE_LIMIT_WINDOW)
        }
    
    user_requests = rate_limit_storage[user_identifier]['requests']
    recent_requests = [req_time for req_time in user_requests if req_time > cleanup_time]
    
    requests_made = len(recent_requests)
    requests_remaining = max(0, RATE_LIMIT_REQUESTS - requests_made)
    
    # Calculate reset time (when the oldest request in window expires)
    if recent_requests:
        oldest_request = min(recent_requests)
        reset_time = int(oldest_request + RATE_LIMIT_WINDOW)
    else:
        reset_time = int(current_time + RATE_LIMIT_WINDOW)
    
    return {
        "requests_made": requests_made,
        "requests_remaining": requests_remaining,
        "reset_time": reset_time
    }


def get_rate_limit_config() -> Dict[str, int]:
    """
    Get the current rate limiting configuration.
    
    Returns:
        Dict containing the rate limiting configuration
    """
    return {
        "requests_per_window": RATE_LIMIT_REQUESTS,
        "window_seconds": RATE_LIMIT_WINDOW
    }


def cleanup_expired_rate_limits() -> int:
    """
    Clean up expired rate limit entries to free memory.
    
    Returns:
        Number of cleaned up entries
    """
    current_time = time.time()
    cleanup_time = current_time - RATE_LIMIT_WINDOW
    users_to_remove = []
    
    for user_id, data in rate_limit_storage.items():
        # Remove old requests outside the time window
        data['requests'] = [req_time for req_time in data['requests'] if req_time > cleanup_time]
        if not data['requests']:
            users_to_remove.append(user_id)
    
    # Clean up empty users
    for user_id in users_to_remove:
        del rate_limit_storage[user_id]
    
    logger.debug(f"Cleaned up {len(users_to_remove)} expired rate limit entries")
    return len(users_to_remove)
