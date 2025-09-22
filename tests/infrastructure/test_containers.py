import pytest
import subprocess  # Use Python's standard library for running processes
import json        # Use the standard library for parsing JSON
import socket      # Use the standard library for network connections
import requests    # For HTTP health checks

# --- Helper Function 1: Running Podman Commands Reliably ---
def run_podman_command(command_args: list[str]):
    """
    Runs a Podman command using subprocess, bypassing any testinfra bugs.
    """
    base_command = ["podman"]
    command_to_run = base_command + command_args
    
    # Run the command, capture the output, and treat it as text
    result = subprocess.run(
        command_to_run,
        capture_output=True,
        text=True
    )
    return result

# --- Helper Function 2: Checking Sockets Reliably ---
def is_port_listening(host: str, port: int) -> bool:
    """
    Checks if a port is open and listening using Python's native socket library.
    Returns True if listening, False otherwise.
    """
    # Create a new socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set a short timeout to prevent the test from hanging
    s.settimeout(1)
    try:
        # connect_ex returns 0 if the connection is successful
        result = s.connect_ex((host, port))
        return result == 0
    finally:
        # Always close the socket
        s.close()

# --- Your Tests, Now Fully Bypassing the Testinfra Bug ---

def test_vllm_container_running():
    """Test if vLLM container is running and healthy"""
    # Use our reliable helper to run 'podman inspect my-vllm-service'
    inspect_result = run_podman_command(["inspect", "my-vllm-service"])
    assert inspect_result.returncode == 0, f"Container 'my-vllm-service' not found. Stderr: {inspect_result.stderr}"

    container_info = json.loads(inspect_result.stdout)
    assert container_info[0]["State"]["Running"], "Container 'my-vllm-service' is not running."

    # Use our reliable helper to check the port
    assert is_port_listening("127.0.0.1", 8000), "Port 8000 is not listening."

def test_chatbot_container_running():
    """Test if the main chatbot container is running"""
    inspect_result = run_podman_command(["inspect", "chatbot-backend"])
    assert inspect_result.returncode == 0, f"Container 'chatbot-backend' not found. Stderr: {inspect_result.stderr}"

    container_info = json.loads(inspect_result.stdout)
    assert container_info[0]["State"]["Running"], "Container 'chatbot-backend' is not running."

    # Use our reliable helper to check the port
    assert is_port_listening("127.0.0.1", 8080), "Port 8080 is not listening."

def test_embeddings_container_running():
    """Test if the embeddings service container is running"""
    inspect_result = run_podman_command(["inspect", "my-embedding-service"])
    assert inspect_result.returncode == 0, f"Container 'my-embedding-service' not found. Stderr: {inspect_result.stderr}"

    container_info = json.loads(inspect_result.stdout)
    assert container_info[0]["State"]["Running"], "Container 'my-embedding-service' is not running."

    # Use our reliable helper to check the port
    assert is_port_listening("127.0.0.1", 8001), "Port 8001 is not listening."


def test_container_logs():
    """Test if containers are logging properly"""
    containers = [
        "my-embedding-service", 
        "chatbot-backend", 
        "chatbot-rag-service", 
        "chatbot-logging-service",
        "chatbot-frontend"
    ]
    
    for container in containers:
        logs_result = run_podman_command(["logs", container])
        assert logs_result.returncode == 0, f"Could not get logs for '{container}'. Stderr: {logs_result.stderr}"
        
        logs = logs_result.stdout + logs_result.stderr
        assert logs, f"Logs for container '{container}' are empty."
        # Note: For nginx/frontend containers, some "error" level logs might be normal
        # so we only check for critical errors
        if container == "chatbot-frontend":
            assert "emerg" not in logs.lower() and "alert" not in logs.lower(), f"Found critical errors in logs for '{container}'"
        else:
            assert "error" not in logs.lower(), f"Found the word 'error' in the logs for '{container}'"

def test_rag_service_container_running():
    """Test if the RAG service container is running"""
    inspect_result = run_podman_command(["inspect", "chatbot-rag-service"])
    assert inspect_result.returncode == 0, f"Container 'chatbot-rag-service' not found. Stderr: {inspect_result.stderr}"

    container_info = json.loads(inspect_result.stdout)
    assert container_info[0]["State"]["Running"], "Container 'chatbot-rag-service' is not running."

    # Use our reliable helper to check the port
    assert is_port_listening("127.0.0.1", 8082), "Port 8082 is not listening."

def test_logging_service_container_running():
    """Test if the logging service container is running"""
    inspect_result = run_podman_command(["inspect", "chatbot-logging-service"])
    assert inspect_result.returncode == 0, f"Container 'chatbot-logging-service' not found. Stderr: {inspect_result.stderr}"

    container_info = json.loads(inspect_result.stdout)
    assert container_info[0]["State"]["Running"], "Container 'chatbot-logging-service' is not running."

    # Use our reliable helper to check the port
    assert is_port_listening("127.0.0.1", 8002), "Port 8002 is not listening."

def test_rag_service_health_endpoint():
    """Test if the RAG service health endpoint is responding"""
    try:
        response = requests.get("http://127.0.0.1:8082/health", timeout=5)
        assert response.status_code == 200, f"RAG service health endpoint returned status {response.status_code}"
        
        health_data = response.json()
        assert "status" in health_data, "Health response missing 'status' field"
        assert health_data["status"] == "healthy", f"RAG service status is {health_data['status']}, expected 'healthy'"
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to RAG service health endpoint at http://127.0.0.1:8082/health")
    except requests.exceptions.Timeout:
        pytest.fail("RAG service health endpoint timed out")

def test_logging_service_health_endpoint():
    """Test if the logging service health endpoint is responding"""
    try:
        response = requests.get("http://127.0.0.1:8002/health", timeout=5)
        assert response.status_code == 200, f"Logging service health endpoint returned status {response.status_code}"
        
        health_data = response.json()
        assert "status" in health_data, "Health response missing 'status' field"
        assert health_data["status"] == "healthy", f"Logging service status is {health_data['status']}, expected 'healthy'"
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to logging service health endpoint at http://127.0.0.1:8002/health")
    except requests.exceptions.Timeout:
        pytest.fail("Logging service health endpoint timed out")

def test_backend_service_health_endpoint():
    """Test if the backend service health endpoint is responding"""
    try:
        response = requests.get("http://127.0.0.1:8080/health", timeout=5)
        assert response.status_code == 200, f"Backend service health endpoint returned status {response.status_code}"
        
        health_data = response.json()
        assert "status" in health_data, "Health response missing 'status' field"
        assert health_data["status"] == "healthy", f"Backend service status is {health_data['status']}, expected 'healthy'"
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to backend service health endpoint at http://127.0.0.1:8080/health")
    except requests.exceptions.Timeout:
        pytest.fail("Backend service health endpoint timed out")

def test_embeddings_service_health_endpoint():
    """Test if the embeddings service health endpoint is responding"""
    try:
        # vLLM services typically provide a /health endpoint
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        assert response.status_code == 200, f"Embeddings service health endpoint returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to embeddings service health endpoint at http://127.0.0.1:8001/health")
    except requests.exceptions.Timeout:
        pytest.fail("Embeddings service health endpoint timed out")

def test_vllm_service_health_endpoint():
    """Test if the vLLM service health endpoint is responding (if running)"""
    try:
        # Check if the vLLM service is available via health endpoint
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        assert response.status_code == 200, f"vLLM service health endpoint returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        # Skip this test if vLLM service is not running (since it's commented out in docker-compose)
        pytest.skip("vLLM service is not running or not available at http://127.0.0.1:8000/health")
    except requests.exceptions.Timeout:
        pytest.fail("vLLM service health endpoint timed out")

def test_frontend_container_running():
    """Test if the frontend container is running"""
    inspect_result = run_podman_command(["inspect", "chatbot-frontend"])
    assert inspect_result.returncode == 0, f"Container 'chatbot-frontend' not found. Stderr: {inspect_result.stderr}"

    container_info = json.loads(inspect_result.stdout)
    assert container_info[0]["State"]["Running"], "Container 'chatbot-frontend' is not running."

    # Use our reliable helper to check the port
    assert is_port_listening("127.0.0.1", 8090), "Port 8090 is not listening."

def test_frontend_health_endpoint():
    """Test if the frontend service is responding and serving content"""
    try:
        # Test the main page
        response = requests.get("http://127.0.0.1:8090/", timeout=10)
        assert response.status_code == 200, f"Frontend service returned status {response.status_code}"
        
        # Check if it's serving HTML content
        content_type = response.headers.get('content-type', '')
        assert 'text/html' in content_type, f"Frontend not serving HTML content, got: {content_type}"
        
        # Check for basic HTML structure
        content = response.text.lower()
        assert '<html' in content or '<!doctype html' in content, "Response does not contain valid HTML"
        
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to frontend service at http://127.0.0.1:8090/")
    except requests.exceptions.Timeout:
        pytest.fail("Frontend service request timed out")

def test_frontend_api_proxy():
    """Test if the frontend correctly proxies API requests to the backend"""
    try:
        # Test the API proxy through the frontend (should forward to backend)
        response = requests.get("http://127.0.0.1:8090/api/health", timeout=10)
        assert response.status_code == 200, f"Frontend API proxy returned status {response.status_code}"
        
        # This should be the same response as the backend health endpoint
        health_data = response.json()
        assert "status" in health_data, "API proxy response missing 'status' field"
        assert health_data["status"] == "healthy", f"API proxy status is {health_data['status']}, expected 'healthy'"
        
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to frontend API proxy at http://127.0.0.1:8090/api/health")
    except requests.exceptions.Timeout:
        pytest.fail("Frontend API proxy request timed out")