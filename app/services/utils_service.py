"""
Utility functions service.

This module provides:
- User anonymization utilities
- Text processing and sanitization
- Query analysis and classification
- Common utility operations
"""

import hashlib
import logging

logger = logging.getLogger(__name__)


# --- User Anonymization ---

def anonymize_user_id(email: str) -> str:
    """
    Create an anonymized user identifier from email.
    
    Args:
        email: User's email address
        
    Returns:
        Anonymized user identifier (partial email for readability)
    """
    if not email or len(email) < 8:
        return "anonymous"
    return email[:8] + "..."


def anonymize_user_id_hash(email: str) -> str:
    """
    Create a hashed anonymized user identifier from email.
    
    Args:
        email: User's email address
        
    Returns:
        Anonymized user identifier (hash)
    """
    return hashlib.sha256(email.encode()).hexdigest()[:16]


# --- Text Processing ---

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


# --- Query Analysis ---

def classify_query_type(query: str) -> str:
    """
    Simple query classification for analytics.
    
    Args:
        query: User's query text
        
    Returns:
        Query type classification
    """
    query_lower = query.lower()
    
    # Question patterns
    question_words = ['qué', 'cómo', 'cuándo', 'dónde', 'por qué', 'quién', 'cuál']
    if any(word in query_lower for word in question_words) or '?' in query:
        return "question"
    
    # Definition requests
    definition_words = ['define', 'definir', 'concepto', 'significado', 'qué es']
    if any(word in query_lower for word in definition_words):
        return "definition"
    
    # Example requests
    example_words = ['ejemplo', 'ejemplos', 'caso', 'casos', 'muestra', 'ilustra']
    if any(word in query_lower for word in example_words):
        return "example"
    
    # Problem solving
    problem_words = ['problema', 'resolver', 'solución', 'cálculo', 'calcular', 'ejercicio']
    if any(word in query_lower for word in problem_words):
        return "problem_solving"
    
    # Comparison requests
    comparison_words = ['diferencia', 'comparar', 'versus', 'vs', 'mejor', 'peor']
    if any(word in query_lower for word in comparison_words):
        return "comparison"
    
    return "general"


def estimate_query_complexity(query: str) -> str:
    """
    Estimate query complexity for analytics.
    
    Args:
        query: User's query text
        
    Returns:
        Complexity level (simple, medium, complex)
    """
    # Simple heuristics for complexity estimation
    word_count = len(query.split())
    
    # Complex indicators
    complex_words = [
        'análisis', 'evaluar', 'comparar', 'contrastar', 'justificar', 
        'argumentar', 'demostrar', 'optimizar', 'integrar', 'sintetizar'
    ]
    
    # Medium complexity indicators  
    medium_words = [
        'explicar', 'describir', 'identificar', 'clasificar', 'aplicar',
        'resolver', 'calcular', 'determinar', 'establecer'
    ]
    
    query_lower = query.lower()
    
    if word_count > 20 or any(word in query_lower for word in complex_words):
        return "complex"
    elif word_count > 10 or any(word in query_lower for word in medium_words):
        return "medium"
    else:
        return "simple"


# --- Data Processing ---

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
