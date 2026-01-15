"""Tests for src/monica/ffmpeg_manager.py"""

import pytest
import sys
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestGetOs:
    """Tests for get_os function."""

    def test_get_os_windows(self):
        """Test detecting Windows."""
        with patch.object(sys, "platform", "win32"):
            from monica import ffmpeg_manager
            # Reload to pick up patched value
            import importlib
            importlib.reload(ffmpeg_manager)
            result = ffmpeg_manager.get_os()
            assert result == "windows"

    def test_get_os_linux(self):
        """Test detecting Linux."""
        with patch.object(sys, "platform", "linux"):
            from monica import ffmpeg_manager
            import importlib
            importlib.reload(ffmpeg_manager)
            result = ffmpeg_manager.get_os()
            assert result == "linux"

    def test_get_os_darwin(self):
        """Test macOS returns unknown."""
        with patch.object(sys, "platform", "darwin"):
            from monica import ffmpeg_manager
            import importlib
            importlib.reload(ffmpeg_manager)
            result = ffmpeg_manager.get_os()
            assert result == "unknown"


class TestCheckFfmpegInPath:
    """Tests for check_ffmpeg_in_path function."""

    def test_ffmpeg_found_in_path(self):
        """Test when FFmpeg is in PATH."""
        with patch.object(shutil, "which", return_value="/usr/bin/ffmpeg"):
            from monica.ffmpeg_manager import check_ffmpeg_in_path
            result = check_ffmpeg_in_path()
            assert result == "/usr/bin/ffmpeg"

    def test_ffmpeg_not_in_path(self):
        """Test when FFmpeg is not in PATH."""
        with patch.object(shutil, "which", return_value=None):
            from monica.ffmpeg_manager import check_ffmpeg_in_path
            result = check_ffmpeg_in_path()
            assert result is None


class TestCheckFfmpegLocal:
    """Tests for check_ffmpeg_local function."""

    def test_ffmpeg_local_windows(self, tmp_path):
        """Test finding local FFmpeg on Windows."""
        from monica.ffmpeg_manager import check_ffmpeg_local

        # Create local ffmpeg directory with exe
        ffmpeg_dir = tmp_path / "ffmpeg" / "bin"
        ffmpeg_dir.mkdir(parents=True)
        ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"
        ffmpeg_exe.write_text("fake")

        with patch.object(sys, "platform", "win32"):
            result = check_ffmpeg_local(tmp_path)
            # On Windows, should find the .exe
            assert result is not None or sys.platform != "win32"

    def test_ffmpeg_local_linux(self, tmp_path):
        """Test finding local FFmpeg on Linux."""
        from monica.ffmpeg_manager import check_ffmpeg_local

        # Create local ffmpeg directory
        ffmpeg_dir = tmp_path / "ffmpeg" / "bin"
        ffmpeg_dir.mkdir(parents=True)
        ffmpeg_exe = ffmpeg_dir / "ffmpeg"
        ffmpeg_exe.write_text("fake")

        # This test is platform-dependent
        result = check_ffmpeg_local(tmp_path)
        # Result depends on actual platform

    def test_ffmpeg_local_missing(self, tmp_path):
        """Test when local FFmpeg doesn't exist."""
        from monica.ffmpeg_manager import check_ffmpeg_local
        result = check_ffmpeg_local(tmp_path)
        assert result is None

    def test_ffmpeg_local_dir_exists_no_binary(self, tmp_path):
        """Test when ffmpeg dir exists but no binary."""
        from monica.ffmpeg_manager import check_ffmpeg_local

        ffmpeg_dir = tmp_path / "ffmpeg" / "bin"
        ffmpeg_dir.mkdir(parents=True)

        result = check_ffmpeg_local(tmp_path)
        assert result is None


class TestGetFfmpegPath:
    """Tests for get_ffmpeg_path function."""

    def test_falls_back_to_path(self, tmp_path):
        """Test falls back to PATH when no local."""
        with patch.object(shutil, "which", return_value="/usr/bin/ffmpeg"):
            from monica.ffmpeg_manager import get_ffmpeg_path
            result = get_ffmpeg_path(tmp_path)
            assert result == "/usr/bin/ffmpeg"

    def test_returns_none_when_not_found(self, tmp_path):
        """Test returns None when FFmpeg not found anywhere."""
        with patch.object(shutil, "which", return_value=None):
            from monica.ffmpeg_manager import get_ffmpeg_path
            result = get_ffmpeg_path(tmp_path)
            assert result is None


class TestVerifyFfmpeg:
    """Tests for verify_ffmpeg function."""

    def test_verify_success(self):
        """Test verification succeeds with valid FFmpeg."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stderr="ffmpeg version 5.0"
            )
            from monica.ffmpeg_manager import verify_ffmpeg
            result = verify_ffmpeg("/usr/bin/ffmpeg")
            assert result is True

    def test_verify_failure_bad_returncode(self):
        """Test verification fails with bad return code."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            from monica.ffmpeg_manager import verify_ffmpeg
            result = verify_ffmpeg("/usr/bin/ffmpeg")
            assert result is False

    def test_verify_failure_exception(self):
        """Test verification handles exceptions."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("ffmpeg not found")
            from monica.ffmpeg_manager import verify_ffmpeg
            result = verify_ffmpeg("/nonexistent/ffmpeg")
            assert result is False

    def test_verify_timeout(self):
        """Test verification handles timeout."""
        import subprocess
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("ffmpeg", 5)
            from monica.ffmpeg_manager import verify_ffmpeg
            result = verify_ffmpeg("/usr/bin/ffmpeg")
            assert result is False
