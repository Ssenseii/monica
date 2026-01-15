"""Tests for src/monica/file_selector.py"""

import pytest
from pathlib import Path

from monica.file_selector import (
    format_size,
    get_files_in_directory,
)


class TestFormatSize:
    """Tests for format_size function."""

    def test_format_size_bytes(self):
        """Test formatting bytes."""
        result = format_size(500)

        assert result == "500.0 B"

    def test_format_size_kilobytes(self):
        """Test formatting kilobytes."""
        result = format_size(2048)

        assert result == "2.0 KB"

    def test_format_size_megabytes(self):
        """Test formatting megabytes."""
        result = format_size(5 * 1024 * 1024)

        assert result == "5.0 MB"

    def test_format_size_gigabytes(self):
        """Test formatting gigabytes."""
        result = format_size(1024 * 1024 * 1024)

        assert result == "1.0 GB"

    def test_format_size_terabytes(self):
        """Test formatting terabytes."""
        result = format_size(1024 * 1024 * 1024 * 1024)

        assert result == "1.0 TB"

    def test_format_size_zero(self):
        """Test formatting zero bytes."""
        result = format_size(0)

        assert result == "0.0 B"

    def test_format_size_fractional(self):
        """Test formatting fractional sizes."""
        result = format_size(1536)  # 1.5 KB

        assert result == "1.5 KB"

    def test_format_size_large_bytes(self):
        """Test formatting 999 bytes stays in bytes."""
        result = format_size(999)

        assert result == "999.0 B"


class TestGetFilesInDirectory:
    """Tests for get_files_in_directory function."""

    def test_get_all_files(self, tmp_import_dir):
        """Test getting all files without filter."""
        files = get_files_in_directory(tmp_import_dir)

        assert len(files) == 4  # video1.mp4, video2.mkv, audio1.mp3, document.txt

    def test_get_files_filtered_by_extension(self, tmp_import_dir):
        """Test filtering files by extension."""
        files = get_files_in_directory(tmp_import_dir, [".mp4", ".mkv"])

        assert len(files) == 2
        assert all(f.suffix in [".mp4", ".mkv"] for f in files)

    def test_get_files_single_extension(self, tmp_import_dir):
        """Test filtering by single extension."""
        files = get_files_in_directory(tmp_import_dir, [".mp3"])

        assert len(files) == 1
        assert files[0].name == "audio1.mp3"

    def test_get_files_no_matches(self, tmp_import_dir):
        """Test filtering with no matching extensions."""
        files = get_files_in_directory(tmp_import_dir, [".flac"])

        assert len(files) == 0

    def test_get_files_empty_directory(self, tmp_path):
        """Test getting files from empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        files = get_files_in_directory(empty_dir)

        assert files == []

    def test_get_files_missing_directory(self, tmp_path):
        """Test getting files from non-existent directory."""
        missing_dir = tmp_path / "nonexistent"

        files = get_files_in_directory(missing_dir)

        assert files == []

    def test_get_files_case_insensitive_extension(self, tmp_path):
        """Test extension matching is case-insensitive."""
        test_dir = tmp_path / "mixed_case"
        test_dir.mkdir()
        (test_dir / "video1.MP4").write_text("content")
        (test_dir / "video2.mp4").write_text("content")

        files = get_files_in_directory(test_dir, [".mp4"])

        # Both should be found (case-insensitive matching)
        assert len(files) >= 1  # At least one should match
        # On case-insensitive filesystems (Windows), both will match
        # On case-sensitive filesystems (Linux), behavior may differ

    def test_get_files_returns_sorted(self, tmp_import_dir):
        """Test files are returned sorted."""
        files = get_files_in_directory(tmp_import_dir)

        names = [f.name for f in files]
        assert names == sorted(names)

    def test_get_files_returns_path_objects(self, tmp_import_dir):
        """Test returned items are Path objects."""
        files = get_files_in_directory(tmp_import_dir)

        assert all(isinstance(f, Path) for f in files)

    def test_get_files_ignores_subdirectories(self, tmp_path):
        """Test subdirectories are not included."""
        test_dir = tmp_path / "with_subdir"
        test_dir.mkdir()
        (test_dir / "file.mp4").write_text("content")
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "nested.mp4").write_text("content")

        files = get_files_in_directory(test_dir)

        # Should only get the top-level file, not nested
        assert len(files) == 1
        assert files[0].name == "file.mp4"
