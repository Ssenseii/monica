"""Shared test fixtures for MONICA test suite."""

import pytest
from pathlib import Path
import sys

from monica.recipes import Recipe


@pytest.fixture
def sample_recipe():
    """Create a sample recipe for testing."""
    return Recipe(
        name="Test Recipe",
        category="video",
        extension=".mp4",
        ffmpeg_args=["-c:v", "libx264", "-crf", "23"],
        description="A test recipe",
        input_extensions=[".avi", ".mkv", ".mov"]
    )


@pytest.fixture
def sample_recipe_with_constraints():
    """Create a sample recipe with duration/size constraints."""
    return Recipe(
        name="Test Short Recipe",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=["-c:v", "libx264", "-crf", "20"],
        description="A test short-form recipe",
        input_extensions=[".mp4", ".mkv"],
        max_duration_seconds=60,
        max_file_size_mb=100
    )


@pytest.fixture
def tmp_import_dir(tmp_path):
    """Create a temporary import directory with sample files."""
    import_dir = tmp_path / "import"
    import_dir.mkdir()

    # Create some test files
    (import_dir / "video1.mp4").write_text("fake video content")
    (import_dir / "video2.mkv").write_text("fake video content")
    (import_dir / "audio1.mp3").write_text("fake audio content")
    (import_dir / "document.txt").write_text("not a media file")

    return import_dir


@pytest.fixture
def tmp_export_dir(tmp_path):
    """Create a temporary export directory."""
    export_dir = tmp_path / "export"
    export_dir.mkdir()
    return export_dir


@pytest.fixture
def tmp_logs_dir(tmp_path):
    """Create a temporary logs directory."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    return logs_dir


@pytest.fixture
def mock_ffmpeg_path():
    """Return a mock FFmpeg path."""
    return "ffmpeg"


@pytest.fixture
def sample_custom_recipes_json():
    """Sample custom recipes JSON content."""
    return '''[
    {
        "name": "Custom Recipe 1",
        "category": "video",
        "extension": ".mp4",
        "ffmpeg_args": ["-c:v", "libx264"],
        "description": "Custom test recipe",
        "input_extensions": [".avi"]
    }
]'''
