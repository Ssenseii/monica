"""Tests for main.py"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from monica.main import setup_directories, main


class TestSetupDirectories:
    """Tests for setup_directories function."""

    def test_creates_import_directory(self, tmp_path):
        """Test import directory is created."""
        setup_directories(tmp_path)

        assert (tmp_path / "import").exists()
        assert (tmp_path / "import").is_dir()

    def test_creates_export_directory(self, tmp_path):
        """Test export directory is created."""
        setup_directories(tmp_path)

        assert (tmp_path / "export").exists()
        assert (tmp_path / "export").is_dir()

    def test_creates_logs_directory(self, tmp_path):
        """Test logs directory is created."""
        setup_directories(tmp_path)

        assert (tmp_path / "logs").exists()
        assert (tmp_path / "logs").is_dir()

    def test_idempotent(self, tmp_path):
        """Test calling twice doesn't raise error."""
        setup_directories(tmp_path)
        setup_directories(tmp_path)  # Should not raise

        assert (tmp_path / "import").exists()
        assert (tmp_path / "export").exists()
        assert (tmp_path / "logs").exists()

    def test_returns_directories(self, tmp_path):
        """Test returns tuple of directories."""
        result = setup_directories(tmp_path)

        assert len(result) == 3
        import_dir, export_dir, logs_dir = result
        assert import_dir == tmp_path / "import"
        assert export_dir == tmp_path / "export"
        assert logs_dir == tmp_path / "logs"

    def test_existing_files_preserved(self, tmp_path):
        """Test existing files in directories are preserved."""
        import_dir = tmp_path / "import"
        import_dir.mkdir()
        test_file = import_dir / "existing.mp4"
        test_file.write_text("content")

        setup_directories(tmp_path)

        assert test_file.exists()
        assert test_file.read_text() == "content"


class TestMain:
    """Tests for main function."""

    def test_main_success(self, mocker, tmp_path):
        """Test main returns 0 on success."""
        mocker.patch("main.Path.cwd", return_value=tmp_path)
        mocker.patch("main.init")  # colorama
        mocker.patch("main.get_logger")
        mocker.patch("main.ensure_ffmpeg", return_value="/usr/bin/ffmpeg")
        mocker.patch("main.run_menu_loop")

        result = main()

        assert result == 0

    def test_main_no_ffmpeg(self, mocker, tmp_path):
        """Test main returns 1 when FFmpeg not available."""
        mocker.patch("main.Path.cwd", return_value=tmp_path)
        mocker.patch("main.init")
        mocker.patch("main.get_logger")
        mocker.patch("main.ensure_ffmpeg", return_value=None)

        result = main()

        assert result == 1

    def test_main_keyboard_interrupt(self, mocker, tmp_path):
        """Test main returns 130 on KeyboardInterrupt."""
        mocker.patch("main.Path.cwd", return_value=tmp_path)
        mocker.patch("main.init")
        mocker.patch("main.get_logger")
        mocker.patch("main.ensure_ffmpeg", return_value="/usr/bin/ffmpeg")
        mocker.patch("main.run_menu_loop", side_effect=KeyboardInterrupt)

        result = main()

        assert result == 130

    def test_main_exception(self, mocker, tmp_path):
        """Test main returns 1 on exception."""
        mocker.patch("main.Path.cwd", return_value=tmp_path)
        mocker.patch("main.init")
        mocker.patch("main.get_logger")
        mocker.patch("main.ensure_ffmpeg", return_value="/usr/bin/ffmpeg")
        mocker.patch("main.run_menu_loop", side_effect=Exception("Test error"))

        result = main()

        assert result == 1

    def test_main_calls_setup_directories(self, mocker, tmp_path):
        """Test main calls setup_directories."""
        mocker.patch("main.Path.cwd", return_value=tmp_path)
        mocker.patch("main.init")
        mocker.patch("main.get_logger")
        mocker.patch("main.ensure_ffmpeg", return_value="/usr/bin/ffmpeg")
        mocker.patch("main.run_menu_loop")
        mock_setup = mocker.patch("main.setup_directories", return_value=(
            tmp_path / "import",
            tmp_path / "export",
            tmp_path / "logs"
        ))

        main()

        mock_setup.assert_called_once()

    def test_main_initializes_logger(self, mocker, tmp_path):
        """Test main initializes logger."""
        mocker.patch("main.Path.cwd", return_value=tmp_path)
        mocker.patch("main.init")
        mock_get_logger = mocker.patch("main.get_logger")
        mocker.patch("main.ensure_ffmpeg", return_value="/usr/bin/ffmpeg")
        mocker.patch("main.run_menu_loop")

        main()

        mock_get_logger.assert_called()
