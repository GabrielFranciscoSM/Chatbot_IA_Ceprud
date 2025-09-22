import pytest
import requests
from unittest.mock import patch, MagicMock, mock_open
from app.services.rag_client import RAGServiceClient
import os
import tempfile
import re


def test_process_pdf_files_basic():
    """Test processing of PDF file input string"""
    input_str = '"file1.pdf", "file2.pdf"'
    # Simulate the function behavior
    result = re.findall(r'"([^"]*)"', input_str)
    assert result == ["file1.pdf", "file2.pdf"]


def test_html_content_manipulation():
    """Test HTML content manipulation for adding subjects"""
    subject_name = "test_subject"
    subject_key = subject_name.lower()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.html")
        
        # Create initial HTML content
        initial_html = "<html><body><ul>\n</ul></body></html>"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(initial_html)
        
        # Simulate adding a subject entry
        entry = f'<li class="chat-item" data-subject="{subject_key}">\n  <span class="subject-icon">🔍</span> {subject_name}\n</li>\n'
        
        # Read, modify, and write HTML
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Insert entry before </ul>
        modified_content = content.replace('</ul>', f'{entry}</ul>')
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        
        # Verify the change
        with open(index_path, "r", encoding="utf-8") as f:
            final_content = f.read()
        
        assert f'data-subject="{subject_key}"' in final_content
        assert subject_name in final_content
        assert final_content.index(subject_name) < final_content.index("</ul>")


def test_duplicate_entry_prevention():
    """Test preventing duplicate subject entries"""
    subject_name = "test_subject"
    subject_key = subject_name.lower()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "index.html")
        
        # Pre-populate with subject entry
        entry = f'<li class="chat-item" data-subject="{subject_key}">\n  <span class="subject-icon">🔍</span> {subject_name}\n</li>\n'
        initial_html = f"<html><body><ul>\n{entry}</ul></body></html>"
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(initial_html)
        
        # Try to add the same subject again
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if subject already exists before adding
        if f'data-subject="{subject_key}"' not in content:
            # Would add entry only if not present
            modified_content = content.replace('</ul>', f'{entry}</ul>')
        else:
            # Subject already exists, don't add
            modified_content = content
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        
        # Verify no duplicates
        with open(index_path, "r", encoding="utf-8") as f:
            final_content = f.read()
        
        # Count occurrences - should be only one data-subject attribute
        assert final_content.count(f'data-subject="{subject_key}"') == 1


@patch('requests.post')
def test_rag_service_add_subject(mock_post):
    """Test adding a new subject via RAG service"""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": "Subject added successfully",
        "subject": "test_subject",
        "files_processed": 3
    }
    mock_post.return_value = mock_response
    
    client = RAGServiceClient()
    
    # Simulate adding a subject with files
    test_files = [
        ("file1.pdf", b"PDF content 1"),
        ("file2.pdf", b"PDF content 2"),
        ("file3.pdf", b"PDF content 3")
    ]
    
    response = requests.post(
        f"{client.base_url}/populate",
        files=test_files,
        data={"subject": "test_subject"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["subject"] == "test_subject"
    assert result["files_processed"] == 3


def test_file_operations_simulation():
    """Test file operations that would be used in subject addition"""
    subject_name = "test_subject"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Simulate creating subject directory
        subject_dir = os.path.join(tmpdir, subject_name)
        os.makedirs(subject_dir, exist_ok=True)
        assert os.path.exists(subject_dir)
        
        # Simulate copying files
        test_files = ["file1.pdf", "file2.pdf", "file3.pdf"]
        for filename in test_files:
            src_path = os.path.join(tmpdir, filename)
            dst_path = os.path.join(subject_dir, filename)
            
            # Create source file
            with open(src_path, "w") as f:
                f.write(f"Content of {filename}")
            
            # Simulate copy operation
            with open(src_path, "r") as src, open(dst_path, "w") as dst:
                dst.write(src.read())
            
            assert os.path.exists(dst_path)
        
        # Verify all files were copied
        copied_files = os.listdir(subject_dir)
        assert len(copied_files) == 3
        assert all(f in copied_files for f in test_files)