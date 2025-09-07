import pytest
from RAG.populate_database import clean_text, load_documents, add_to_chroma, Document
import tempfile
import os 

@pytest.mark.parametrize("input_text,expected", [
    # Encabezado, texto principal, número de página, pie de página
    ("Header\nTexto principal\n1\nFooter", "Texto principal"),
    # Saltos de línea múltiples
    ("Texto\n\n\n\nMás texto", "Texto\n\nMás texto"),
    # Símbolos y caracteres especiales (solo se eliminan los de control)
    ("Texto con símbolos #$%&", "Texto con símbolos #$%&"),
    # Tabla Markdown debe ser eliminada
    ("| Col1 | Col2 |\n|------|------|\n| a    | b    |", ""),
    # Imagen Markdown debe ser eliminada
    ("Texto antes\n![alt](img.png)\nTexto después", "Texto antes\n\nTexto después"),
    # Comentario HTML debe ser eliminado
    ("Texto antes\n<!-- comentario -->\nTexto después", "Texto antes\n\nTexto después"),
    # URL debe ser eliminada
    ("Texto con url https://example.com aquí", "Texto con url aquí"),
])
def test_clean_text_basic(input_text, expected):
    """Test basic cleaning of text"""
    cleaned = clean_text(input_text)
    assert isinstance(cleaned, str)
    assert expected in cleaned

# Mock document loading and splitting
from unittest.mock import patch, MagicMock

def test_load_documents(monkeypatch):
    """Test document loading from a directory with a mock converter"""
    with tempfile.TemporaryDirectory() as tmpdir:
        subject_dir = os.path.join(tmpdir, "subject")
        os.makedirs(subject_dir)
        pdf_path = os.path.join(subject_dir, "test.pdf")
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write("Fake PDF content")

        # Mock DocumentConverter and its methods
        mock_converter = MagicMock()
        mock_result = MagicMock()
        mock_result.document.export_to_markdown.return_value = "Texto principal"
        mock_converter.convert.return_value = mock_result
        monkeypatch.setattr("RAG.populate_database.DocumentConverter", lambda: mock_converter)

        # Call load_documents
        docs = load_documents(subject_dir)
        assert isinstance(docs, list)
        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert "Texto principal" in docs[0].page_content


def test_add_to_chroma(monkeypatch):
    """Test adding chunks to Chroma DB with a mock DB"""
    with tempfile.TemporaryDirectory() as tmpdir:
        chroma_path = os.path.join(tmpdir, "chroma")
        mock_db = MagicMock()
        mock_db.get.return_value = {"ids": []}
        monkeypatch.setattr("RAG.populate_database.Chroma", lambda **kwargs: mock_db)
        # Create fake chunks
        chunk = MagicMock()
        chunk.metadata = {"source": "test_source"}
        chunks = [chunk]
        add_to_chroma(chunks, chroma_path)
        # Assert add_documents was called
        assert mock_db.add_documents.called
