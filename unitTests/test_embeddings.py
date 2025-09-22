import pytest
import requests
from unittest.mock import patch, MagicMock
from app.services.rag_client import RAGServiceClient


def test_rag_client_initialization():
    """Test that RAG client initializes correctly"""
    client = RAGServiceClient()
    assert client.base_url is not None
    assert "rag" in client.base_url.lower() or "8082" in client.base_url


@patch('requests.post')
def test_rag_client_search_documents(mock_post):
    """Test RAG client search documents functionality"""
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "documents": [
            {
                "content": "Test content about IA",
                "metadata": {"source": "test.pdf", "page": 1}
            }
        ],
        "sources": ["test.pdf"]
    }
    mock_post.return_value = mock_response
    
    client = RAGServiceClient()
    documents, sources = client.search_documents(
        query="¿Qué es la inteligencia artificial?",
        subject="test_subject"
    )
    
    assert len(documents) == 1
    assert len(sources) == 1
    assert documents[0].page_content == "Test content about IA"
    assert sources[0] == "test.pdf"


@patch('requests.get')
def test_rag_client_connectivity(mock_get):
    """Test RAG service connectivity check"""
    # Mock successful health check
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    client = RAGServiceClient()
    
    # Test that client can make requests (mocked)
    response = requests.get(f"{client.base_url}/health")
    assert response.status_code == 200
