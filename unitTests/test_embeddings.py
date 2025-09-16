import pytest
from rag.get_embedding_function import get_embedding_function

def test_embedding_function_type():
    """Test that get_embedding_function returns a valid embedding object"""
    embedding_fn = get_embedding_function()
    assert hasattr(embedding_fn, "embed_documents")
    assert hasattr(embedding_fn, "embed_query")

def test_embedding_function_embed_query():
    """Test embedding function on a sample query"""
    embedding_fn = get_embedding_function()
    result = embedding_fn.embed_query("¿Qué es la inteligencia artificial?")
    assert isinstance(result, list)
    assert len(result) > 0
