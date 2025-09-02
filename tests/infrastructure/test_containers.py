import pytest
import testinfra
import docker

def test_vllm_container_running(host):
    """Test if vLLM container is running and healthy"""
    docker = host.docker("vllm-openai")
    assert docker.is_running
    
    # Check container resources
    assert docker.container_id is not None
    
    # Check if the port is listening
    socket = host.socket("tcp://0.0.0.0:8000")
    assert socket.is_listening

def test_chatbot_container_running(host):
    """Test if the main chatbot container is running"""
    docker = host.docker("chatbot")
    assert docker.is_running
    
    # Check if Flask app is responding
    socket = host.socket("tcp://0.0.0.0:5001")
    assert socket.is_listening

def test_prometheus_metrics(host):
    """Test if Prometheus metrics are accessible"""
    socket = host.socket("tcp://0.0.0.0:9090")
    assert socket.is_listening
    
    # Check if metrics endpoint is responding
    command = host.run("curl -s http://localhost:9090/metrics")
    assert command.rc == 0
    assert "vllm" in command.stdout

def test_container_logs(host):
    """Test if containers are logging properly"""
    for container in ["vllm-openai", "chatbot"]:
        docker = host.docker(container)
        logs = docker.logs()
        assert logs
        assert "error" not in logs.lower()

def test_container_resources(host):
    """Test container resource limits"""
    for container in ["vllm-openai", "chatbot"]:
        docker = host.docker(container)
        info = docker.inspect()
        
        # Check memory limits
        assert info["HostConfig"]["Memory"]
        
        # Check CPU limits
        assert info["HostConfig"]["CpuShares"]
