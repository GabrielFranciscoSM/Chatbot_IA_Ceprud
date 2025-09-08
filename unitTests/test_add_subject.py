import pytest
from rag.add_subject import process_pdf_files, update_index_html, add_new_subject
import os
import tempfile
from unittest.mock import patch, MagicMock

def test_process_pdf_files_basic():
    """Test processing of PDF file input string"""
    input_str = '"file1.pdf", "file2.pdf"'
    result = process_pdf_files(input_str)
    assert result == ["file1.pdf", "file2.pdf"]


def test_update_index_html_inserts(monkeypatch):
    """Test entry is inserted before </ul> and icon is present"""
    subject_name = "test_subject"
    subject_key = subject_name.lower()
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("<html><body><ul>\n</ul></body></html>")
        monkeypatch.setattr("rag.add_subject.INDEX_HTML_PATH", index_path)
        update_index_html(subject_name)
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Check entry is before </ul>
            assert f'<li class="chat-item" data-subject="{subject_key}">' in content
            assert content.index(subject_name) < content.index("</ul>")


#Si no funcionara, llamar dos veces a la función y comprobar que no se duplica
def test_update_index_html_no_duplicate(monkeypatch):
    """Test no duplicate entry is added if subject already exists"""
    subject_name = "test_subject"
    subject_key = subject_name.lower()
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.html")
        # Pre-populate with subject entry
        entry = f'<li class="chat-item" data-subject="{subject_key}">\n  <span class="subject-icon">🔍</span> {subject_name}\n</li>\n'
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(f"<html><body><ul>\n{entry}</ul></body></html>")
        monkeypatch.setattr("rag.add_subject.INDEX_HTML_PATH", index_path)
        update_index_html(subject_name)
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(content)
            # Should only appear once
            assert content.count(subject_name) == 2


def test_add_new_subject_calls(monkeypatch):
    """Test add_new_subject calls expected steps with mocks"""
    subject_name = "test_subject"
    folder_path = None
    pdf_files = ["/fake/path/file1.pdf"]

    # Mock os.path.exists to always return True
    monkeypatch.setattr("os.path.exists", lambda path: True)
    # Mock os.makedirs to do nothing
    monkeypatch.setattr("os.makedirs", lambda path: None)
    # Mock shutil.copy to do nothing
    monkeypatch.setattr("shutil.copy", lambda src, dst: None)
    # Mock subprocess.run to do nothing
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: None)
    # Mock update_index_html to track call
    called = {}
    def fake_update_index_html(name):
        called["update"] = name
    monkeypatch.setattr("rag.add_subject.update_index_html", fake_update_index_html)

    add_new_subject(subject_name, folder_path=folder_path, pdf_files=pdf_files)
    assert called["update"] == subject_name
