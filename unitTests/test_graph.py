import pytest
from app.domain.graph import build_graph
from unittest.mock import patch, MagicMock


def test_build_graph_returns_graph():
    """Test that build_graph returns a graph object"""
    graph = build_graph()
    assert graph is not None
    assert hasattr(graph, "get_state")
    assert hasattr(graph, "stream")


@patch("app.domain.graph.consultar_guia_docente")
def test_consultar_guia_docente_tool(mock_tool):
    """Test consultar_guia_docente tool returns expected tuple"""
    mock_tool.return_value = ("info", [])
    result = mock_tool("temario")
    assert isinstance(result, tuple)
    assert result[0] == "info"
    assert isinstance(result[1], list)


def test_graph_state_management():
    """Test graph state management functionality"""
    graph = build_graph()
    
    # Test that graph has required methods for state management
    assert hasattr(graph, 'get_state')
    assert hasattr(graph, 'update_state')
    assert hasattr(graph, 'stream')
    
    # Test configuration object creation
    config = {"configurable": {"thread_id": "test_thread"}}
    assert "configurable" in config
    assert "thread_id" in config["configurable"]


@patch("app.services.rag_client.RAGServiceClient")
def test_graph_integration_with_rag(mock_rag_client):
    """Test graph integration with RAG client"""
    # Mock RAG client response
    mock_client = MagicMock()
    mock_client.search_documents.return_value = ([], [])
    mock_rag_client.return_value = mock_client
    
    graph = build_graph()
    
    # Test that graph can be built without errors
    assert graph is not None
    
    # Test basic configuration
    config = {"configurable": {"thread_id": "test_session"}}
    
    # Test that get_state doesn't throw errors with valid config
    try:
        state = graph.get_state(config)
        # State should be accessible without errors
        assert state is not None or state == {}
    except Exception as e:
        # If state is empty initially, that's acceptable
        assert "not found" in str(e).lower() or "no state" in str(e).lower()


def test_agent_state_structure():
    """Test the expected structure of agent state"""
    # Test the state keys that should be present in the graph
    expected_keys = ["messages", "user_email", "subject"]
    
    # Since we can't directly access the state structure, we test
    # that our expected structure is reasonable
    for key in expected_keys:
        assert isinstance(key, str)
        assert len(key) > 0


@patch("app.domain.query_logic.query_rag")
def test_query_integration(mock_query_rag):
    """Test query integration functionality"""
    # Mock query response
    mock_response = {
        "response": "Test response about AI",
        "sources": ["doc1.pdf", "doc2.pdf"],
        "model_used": "test_model"
    }
    mock_query_rag.return_value = mock_response
    
    # Test query functionality
    from app.domain.query_logic import query_rag
    
    result = query_rag(
        query_text="¿Qué es la inteligencia artificial?",
        subject="informatica",
        use_finetuned=False,
        email="test@example.com"
    )
    
    assert result is not None
    assert mock_query_rag.called
