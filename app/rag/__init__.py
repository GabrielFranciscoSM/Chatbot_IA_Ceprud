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
from .get_wikipedia_data import *

__all__ = [
    # From get_embedding_function.py
    "get_embedding_function",
    
    # From populate_database.py
    "main",
    "clean_text",
    "load_documents", 
    "split_documents",
    "add_to_chroma",
    "clear_database",

    # From get_wikipedia_data.py
    "clean_wikipedia_text",
    "get_wikipedia_article",
    "save_wikipedia_articles"
]
