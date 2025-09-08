import pytest
from domain.graph import build_graph
from unittest.mock import patch, MagicMock

def test_build_graph_returns_graph():
    """Test that build_graph returns a graph object"""
    graph = build_graph()
    assert graph is not None
    assert hasattr(graph, "get_state")

@patch("domain.graph.consultar_guia_docente")
def test_consultar_guia_docente_tool(mock_tool):
    """Test consultar_guia_docente tool returns expected tuple"""
    mock_tool.return_value = ("info", [])
    result = mock_tool("temario")
    assert isinstance(result, tuple)
    assert result[0] == "info"
    assert isinstance(result[1], list)
