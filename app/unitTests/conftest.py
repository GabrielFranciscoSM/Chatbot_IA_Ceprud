"""
Pytest configuration and fixtures for unit tests
"""
import pytest
import os
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_rag_client():
    """Mock RAG service client for testing"""
    with patch('app.services.rag_client.RAGServiceClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client.base_url = "http://localhost:8082"
        mock_client.search_documents.return_value = ([], [])
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_graph():
    """Mock graph for testing"""
    with patch('app.domain.graph.build_graph') as mock_build_graph:
        mock_graph_instance = MagicMock()
        mock_graph_instance.get_state.return_value = None
        mock_graph_instance.stream.return_value = [
            {"response": "Test response", "sources": ["test.pdf"]}
        ]
        mock_build_graph.return_value = mock_graph_instance
        yield mock_graph_instance


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    from langchain_core.documents import Document
    
    return [
        Document(
            page_content="Sample content about artificial intelligence",
            metadata={"source": "ai.pdf", "page": 1}
        ),
        Document(
            page_content="More information about machine learning",
            metadata={"source": "ml.pdf", "page": 1}
        )
    ]


@pytest.fixture
def test_config():
    """Test configuration for graph operations"""
    return {"configurable": {"thread_id": "test_user@example.com"}}


@pytest.fixture
def mock_requests():
    """Mock requests module for HTTP testing"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.delete') as mock_delete:
        
        # Default successful responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_delete.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'delete': mock_delete,
            'response': mock_response
        }


# Set up test environment variables
os.environ.setdefault('RAG_SERVICE_URL', 'http://localhost:8082')
os.environ.setdefault('VLLM_URL', 'http://localhost:8000')
os.environ.setdefault('VLLM_EMBEDDING_URL', 'http://localhost:8001')
os.environ.setdefault('BASE_CHROMA_PATH', '/tmp/test_chroma')
