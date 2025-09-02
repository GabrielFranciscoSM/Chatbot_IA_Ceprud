import pytest

def test_prometheus_metrics(host):
    """Test if Prometheus metrics endpoint is accessible"""
    socket = host.socket("tcp://0.0.0.0:9090")
    assert socket.is_listening
    
    command = host.run("curl -s http://localhost:9090/metrics")
    assert command.rc == 0
    assert "vllm" in command.stdout

def test_grafana_dashboard(host):
    """Test if Grafana dashboard is accessible"""
    socket = host.socket("tcp://0.0.0.0:3000")
    assert socket.is_listening
    
    command = host.run("curl -s http://localhost:3000")
    assert command.rc == 0
    assert "Grafana" in command.stdout
