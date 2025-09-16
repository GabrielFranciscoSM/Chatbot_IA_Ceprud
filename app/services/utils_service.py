"""
Utility functions service.

This module provides:
- User anonymization utilities
- Helper functions for data processing
- Common utility operations
"""

import hashlib
import logging

logger = logging.getLogger(__name__)


def anonymize_user_id(email: str) -> str:
    """
    Create an anonymized user identifier from email.
    
    Args:
        email: User's email address
        
    Returns:
        Anonymized user identifier (hash)
    """
    return hashlib.sha256(email.encode()).hexdigest()[:16]


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by removing potentially harmful content.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    # Basic sanitization
    sanitized = text.strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return sanitized


def format_sources_list(sources: list) -> list:
    """
    Format and clean sources list for display.
    
    Args:
        sources: List of source strings
        
    Returns:
        Cleaned and formatted sources list
    """
    if not sources:
        return []
    
    # Remove duplicates while preserving order
    seen = set()
    unique_sources = []
    for source in sources:
        if source not in seen:
            seen.add(source)
            unique_sources.append(source)
    
    return unique_sources


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to specified length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
