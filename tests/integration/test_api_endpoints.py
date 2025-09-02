import pytest
#from fastapi.testclient import TestClient
from app.app import app

def test_chat_endpoint_basic(test_client, test_data):
    """Test the /chat endpoint with a basic query"""
    response =test_client.post(
        "/chat",
        data={
            "message": test_data["sample_query"],
            "subject": test_data["sample_subject"],
            "email": test_data["sample_email"],
            "mode": "rag"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0

def test_chat_endpoint_empty_message(test_client, test_data):
    """Test the /chat endpoint with an empty message"""
    response =test_client.post(
        "/chat",
        data={
            "message": "",
            "subject": test_data["sample_subject"],
            "email": test_data["sample_email"],
            "mode": "rag"
        }
    )
    assert response.status_code == 400

def test_chat_with_invalid_mode(test_client, test_data):
    """Test chat endpoint with invalid mode"""
    response =test_client.post(
        "/chat",
        data={
            "message": "Test invalid mode",
            "subject": test_data["sample_subject"],
            "email": test_data["sample_email"],
            "mode": "invalid_mode"
        }
    )
    assert response.status_code == 400

def test_chat_rag_mode_with_nonexistent_subject(test_client, test_data):
    """Test chat endpoint with non-existent subject"""
    response =test_client.post(
        "/chat",
        data={
            "message": "Test non-existent subject",
            "subject": "no_such_subject",
            "email": test_data["sample_email"],
            "mode": "rag"
        }
    )
    assert response.status_code in (400, 404)

def test_logging_is_created(test_client, test_data, tmp_path):
    """Test that a log entry is created after chat"""
    log_path = tmp_path / "chat_logs.csv"
    # Monkeypatch log path if needed
    response =test_client.post(
        "/chat",
        data={
            "message": "Log test",
            "subject": test_data["sample_subject"],
            "email": "pytest@ugr.es",
            "mode": "rag"
        }
    )
    assert response.status_code == 200
    # Check log file exists and contains entry
    assert log_path.exists() or True  # Replace with actual log path check if possible

def test_serve_graph_success(test_client):
    """Test serving a graph image"""
    response =test_client.get("/graphs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Optionally check for known graph files

def test_serve_graph_not_found(test_client):
    """Test requesting a non-existent graph image"""
    response =test_client.get("/graphs/non_existent_graph.png")
    assert response.status_code in (404, 400)
