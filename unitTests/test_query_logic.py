import pytest
from domain.query_logic import query_rag
from unittest.mock import patch, MagicMock

def test_query_rag_basic():
    """Test basic RAG query functionality"""
    with patch('domain.query_logic.ChatOpenAI') as mock_chat:
        mock_chat.return_value = MagicMock()
        mock_chat.return_value.invoke.return_value = "Test response"
        
        result = query_rag(
            query_text="test question",
            subject="metaheuristicas",
            use_finetuned=False
        )
        
        assert isinstance(result, dict)
        assert "response" in result

@pytest.mark.asyncio
async def test_query_rag_with_context():
    """Test RAG query with context retrieval"""
    with patch('domain.query_logic.Chroma') as mock_chroma:
        mock_chroma.return_value.similarity_search_with_score.return_value = [
            (MagicMock(page_content="test content"), 0.8)
        ]
        
        result = query_rag(
            query_text="test with context",
            subject="metaheuristicas"
        )
        
        assert isinstance(result, dict)
        assert "sources" in result
        assert len(result["sources"]) > 0

def test_query_rag_finetuned():
    """Test RAG query with fine-tuned model"""
    with patch('domain.query_logic.ChatOpenAI') as mock_chat:
        mock_chat.return_value = MagicMock()
        
        result = query_rag(
            query_text="test question",
            subject="metaheuristicas",
            use_finetuned=True
        )
        
        assert isinstance(result, dict)
        assert result.get("model_used") == "RAG + LoRA"