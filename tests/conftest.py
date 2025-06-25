"""Pytest configuration and fixtures for text2file tests."""

import os
import sys
import shutil
import tempfile
from pathlib import Path

import pytest

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def test_content():
    """Return sample test content."""
    return """This is a test content for text2file.

It spans multiple lines and paragraphs.

With some special characters: !@#$%^&*()_+{}|:<>?
And some unicode: こんにちは 世界"""
