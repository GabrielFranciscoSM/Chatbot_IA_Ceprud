"""
RAG (Retrieval-Augmented Generation) system components.

This package contains all RAG-related functionality:
- get_embedding_function: Embedding models and functions
- populate_database: Database population and management
- add_subject: Subject management utilities
- guia_docente_scrapper: Web scraping for educational content
"""

from .get_embedding_function import *
from .populate_database import *

__all__ = [
    # Export main functions - will be populated based on actual exports
]
