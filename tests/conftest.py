import pytest
from fastapi.testclient import TestClient
from app import app
from rag.get_embedding_function import get_embedding_function
import os
import docker

@pytest.fixture(scope="session")
def test_client():
    """Create a test client for our FastAPI app"""
    return TestClient(app)

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """Get the Docker Compose file path"""
    return os.path.join(
        str(pytestconfig.rootdir),
        "docker-compose-vllm.yml"
    )

@pytest.fixture(scope="session")
def docker_services(docker_compose_file):
    """Start up Docker Compose services"""
    docker_client = docker.from_env()
    yield docker_client
    # Cleanup will happen automatically

@pytest.fixture(scope="session")
def embedding_function():
    """Get the embedding function for testing"""
    return get_embedding_function()

@pytest.fixture(scope="session")
def test_data():
    """Sample test data for various tests"""
    return {
        "sample_query": "¿Qué es una metaheurística?",
        "sample_subject": "metaheuristicas",
        "sample_email": "test@test.com"
    }

@pytest.fixture(scope="session")
def mock_chroma_path(tmp_path_factory):
    """Create a temporary Chroma DB for testing"""
    test_dir = tmp_path_factory.mktemp("test_chroma")
    return str(test_dir)
