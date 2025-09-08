import pytest
from app.rag.guia_docente_scrapper import parse_profesorado, parse_section_content, guardar_en_json
from bs4 import BeautifulSoup
import os
import tempfile

def test_parse_profesorado_empty():
    """Test parse_profesorado with empty input"""
    assert parse_profesorado(None) == []

def test_parse_section_content_plain():
    """Test parse_section_content with plain text"""
    html = "<div>Texto plano de la sección</div>"
    soup = BeautifulSoup(html, "html.parser")
    result = parse_section_content(soup.div, base_url="http://test")
    assert "Texto plano" in result

def test_guardar_en_json_creates_file():
    """Test guardar_en_json creates a file and writes JSON"""
    data = {"test": "value"}
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "test.json")
        guardar_en_json(data, json_path)
        assert os.path.exists(json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "test" in content
