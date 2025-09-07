    
import pytest
import subprocess  # Use Python's standard library for running processes
import socket      # Use the standard library for network connections

# --- Helper Function 1: Running Generic Shell Commands ---
def run_command(command_args: list[str]):
    """
    Runs a shell command using subprocess, bypassing any testinfra bugs.
    """
    print(f"\n--- Executing command: {' '.join(command_args)} ---")
    
    # Run the command, capture the output, and treat it as text
    result = subprocess.run(
        command_args,
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)  # Set a short timeout (e.g., 2 seconds)
    try:
        # connect_ex returns 0 if the connection is successful (port is open)
        return s.connect_ex((host, port)) == 0
    finally:
        # Ensure the socket is always closed
        s.close()

# --- Your Tests, Rewritten for Reliability ---

def test_prometheus_metrics():
    """Test if Prometheus metrics endpoint is accessible"""
    prometheus_port = 9090
    prometheus_host = "127.0.0.1"

    # 1. Check if the port is open and listening
    assert is_port_listening(prometheus_host, prometheus_port), f"Port {prometheus_port} is not listening."

    # 2. Use curl to get the metrics page content
    curl_result = run_command(["curl", "-s", f"http://{prometheus_host}:{prometheus_port}/metrics"])
    
    # 3. Check if the curl command was successful
    assert curl_result.returncode == 0, f"curl command failed. Stderr: {curl_result.stderr}"
    
    # 4. Check if the expected content is in the page
    assert "vllm" in curl_result.stdout, "The word 'vllm' was not found in Prometheus metrics."

def test_grafana_dashboard():
    """Test if Grafana dashboard is accessible"""
    grafana_port = 3000
    grafana_host = "127.0.0.1"

    # 1. Check if the port is open and listening
    assert is_port_listening(grafana_host, grafana_port), f"Port {grafana_port} is not listening."

    # 2. Use curl to get the Grafana home page content
    curl_result = run_command(["curl", "-s", "-L", f"http://{grafana_host}:{grafana_port}"])
    
    # 3. Check if the curl command was successful
    assert curl_result.returncode == 0, f"curl command failed. Stderr: {curl_result.stderr}"
    
    # 4. Check if the expected content is in the page
    assert "Grafana" in curl_result.stdout, "The word 'Grafana' was not found on the Grafana homepage."

  