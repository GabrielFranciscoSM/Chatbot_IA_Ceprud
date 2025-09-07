import pytest
import subprocess  # Use Python's standard library for running processes
import json        # Use the standard library for parsing JSON
import socket      # Use the standard library for network connections

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
    inspect_result = run_podman_command(["inspect", "my-chatbot-app"])
    assert inspect_result.returncode == 0, f"Container 'my-chatbot-app' not found. Stderr: {inspect_result.stderr}"

    container_info = json.loads(inspect_result.stdout)
    assert container_info[0]["State"]["Running"], "Container 'my-chatbot-app' is not running."

    # Use our reliable helper to check the port
    assert is_port_listening("127.0.0.1", 5001), "Port 5001 is not listening."

def test_container_logs():
    """Test if containers are logging properly"""
    for container in ["my-vllm-service", "my-chatbot-app"]:
        logs_result = run_podman_command(["logs", container])
        assert logs_result.returncode == 0, f"Could not get logs for '{container}'. Stderr: {logs_result.stderr}"
        
        logs = logs_result.stdout + logs_result.stderr
        assert logs, f"Logs for container '{container}' are empty."
        assert "error" not in logs.lower(), f"Found the word 'error' in the logs for '{container}'"