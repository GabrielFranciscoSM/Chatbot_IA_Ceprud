import pytest

# Use the test_client fixture from conftest.py

def test_full_chat_flow(test_client):
    """Simulate a full chat flow with multiple messages"""
    messages = [
        "¿Qué es una metaheurística?",
        "¿Quién es el profesor de la asignatura?",
        "¿Cómo se evalúa la asignatura?"
    ]
    for msg in messages:
        response = test_client.post(
            "/chat",
            data={
                "message": msg,
                "subject": "metaheuristicas",
                "email": "test@ugr.es",
                "mode": "rag"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

def test_chatbot_memory_name(test_client):
    """Test chatbot remembers user's name in conversation"""
    email = "memorytest@ugr.es"
    subject = "metaheuristicas"
    # Step 1: Tell the chatbot your name
    response1 = test_client.post(
        "/chat",
        data={
            "message": "Me llamo Gabriel.",
            "subject": subject,
            "email": email,
            "mode": "rag"
        }
    )
    assert response1.status_code == 200
    # Step 2: Ask the chatbot to recall your name
    response2 = test_client.post(
        "/chat",
        data={
            "message": "¿Cuál es mi nombre?",
            "subject": subject,
            "email": email,
            "mode": "rag"
        }
    )
    assert response2.status_code == 200
    data = response2.json()
    assert "response" in data
    assert "Gabriel" in data["response"]
