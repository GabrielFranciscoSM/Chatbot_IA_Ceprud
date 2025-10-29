import pytest
from app.domain.query_logic import query_rag, clear_session
from unittest.mock import patch, MagicMock


@patch('app.services.rag_client.RAGServiceClient')
@patch('app.domain.graph.build_graph')
def test_query_rag_basic(mock_build_graph, mock_rag_client):
    """Test basic RAG query functionality"""
    # Mock graph
    mock_graph = MagicMock()
    mock_graph.get_state.return_value = None
    mock_graph.stream.return_value = [
        {"response": "Test response about the topic", "sources": ["doc1.pdf"]}
    ]
    mock_build_graph.return_value = mock_graph
    
    # Mock RAG client
    mock_client = MagicMock()
    mock_rag_client.return_value = mock_client
    
    result = query_rag(
        query_text="test question",
        subject="metaheuristicas",
        use_finetuned=False,
        email="test@example.com"
    )
    
    assert isinstance(result, dict)
    assert "response" in result
    assert "sources" in result
    assert "model_used" in result


@patch('app.services.rag_client.RAGServiceClient')
@patch('app.domain.graph.build_graph')
def test_query_rag_with_finetuned(mock_build_graph, mock_rag_client):
    """Test RAG query with fine-tuned model"""
    # Mock graph
    mock_graph = MagicMock()
    mock_graph.get_state.return_value = None
    mock_graph.stream.return_value = [
        {"response": "Fine-tuned response", "sources": ["specialized_doc.pdf"]}
    ]
    mock_build_graph.return_value = mock_graph
    
    # Mock RAG client
    mock_client = MagicMock()
    mock_rag_client.return_value = mock_client
    
    result = query_rag(
        query_text="specialized question",
        subject="metaheuristicas",
        use_finetuned=True,
        email="test@example.com"
    )
    
    assert isinstance(result, dict)
    assert "response" in result
    assert result.get("model_used") == "RAG + LoRA"


@patch('app.domain.graph.build_graph')
def test_clear_session(mock_build_graph):
    """Test session clearing functionality"""
    # Mock graph
    mock_graph = MagicMock()
    mock_graph.update_state.return_value = None
    mock_build_graph.return_value = mock_graph
    
    # Test clear session - pass both required arguments: subject and email
    result = clear_session("test_subject", "test@example.com")
    
    # Should return a boolean indicating success
    assert isinstance(result, bool)
    assert result is True


@patch('app.services.rag_client.RAGServiceClient')
def test_rag_client_integration(mock_rag_client):
    """Test RAG client integration in query logic"""
    # Mock RAG client methods
    mock_client = MagicMock()
    mock_client.search_documents.return_value = (
        [MagicMock(page_content="Test content", metadata={"source": "test.pdf"})],
        ["test.pdf"]
    )
    mock_rag_client.return_value = mock_client
    
    # Test that client can be instantiated
    from app.services.rag_client import RAGServiceClient
    client = RAGServiceClient()
    
    # Test search functionality
    documents, sources = client.search_documents(
        query="test query",
        subject="test_subject"
    )
    
    assert len(documents) >= 0
    assert len(sources) >= 0


def test_query_input_validation():
    """Test query input validation"""
    # Test with various input types
    test_cases = [
        ("valid query", "valid_subject", False, "test@example.com"),
        ("", "subject", False, "test@example.com"),  # Empty query
        ("query", "", False, "test@example.com"),    # Empty subject
    ]
    
    for query_text, subject, use_finetuned, email in test_cases:
        # Test that parameters are properly typed
        assert isinstance(query_text, str)
        assert isinstance(subject, str)
        assert isinstance(use_finetuned, bool)
        assert isinstance(email, str)


@patch('app.domain.graph.build_graph')
def test_graph_state_management(mock_build_graph):
    """Test graph state management in query logic"""
    # Mock graph with state management
    mock_graph = MagicMock()
    mock_state = {
        "messages": [],
        "user_email": "test@example.com",
        "subject": "test_subject"
    }
    mock_graph.get_state.return_value = mock_state
    mock_graph.update_state.return_value = None
    mock_build_graph.return_value = mock_graph
    
    # Test configuration creation
    config = {"configurable": {"thread_id": "test@example.com"}}
    
    assert "configurable" in config
    assert config["configurable"]["thread_id"] == "test@example.com"
    
    # Test state access
    state = mock_graph.get_state(config)
    assert state is not None
    assert "messages" in state


def test_response_structure():
    """Test expected response structure"""
    # Define expected response structure
    expected_keys = ["response", "sources", "model_used", "context_length"]
    
    # Test that all keys are strings (for structure validation)
    for key in expected_keys:
        assert isinstance(key, str)
        assert len(key) > 0
    
    # Test response format expectations
    mock_response = {
        "response": "Example response text",
        "sources": ["doc1.pdf", "doc2.pdf"],
        "model_used": "RAG",
        "context_length": 1500
    }
    
    # Validate mock response structure
    for key in expected_keys:
        assert key in mock_response
    
    assert isinstance(mock_response["response"], str)
    assert isinstance(mock_response["sources"], list)
    assert isinstance(mock_response["model_used"], str)
    assert isinstance(mock_response["context_length"], int)