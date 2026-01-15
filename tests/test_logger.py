"""Tests for src/monica/logger.py"""

import pytest
from pathlib import Path

from monica.logger import MonicaLogger, get_logger


# Reset the global logger between tests
@pytest.fixture(autouse=True)
def reset_logger():
    """Reset the global logger instance between tests."""
    import monica.logger
    monica.logger._logger = None
    yield
    monica.logger._logger = None


def flush_logger(logger):
    """Flush all handlers to ensure log is written to file."""
    for handler in logger._logger.handlers:
        handler.flush()


class TestMonicaLogger:
    """Tests for MonicaLogger class."""

    def test_logger_creates_file(self, tmp_logs_dir):
        """Test logger creates log file."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.info("Test message")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        assert log_file.exists()

    def test_logger_info_message(self, tmp_logs_dir):
        """Test info messages are logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.info("Test info message")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "INFO" in content
        assert "Test info message" in content

    def test_logger_error_message(self, tmp_logs_dir):
        """Test error messages are logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.error("Test error message")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "ERROR" in content
        assert "Test error message" in content

    def test_logger_warning_message(self, tmp_logs_dir):
        """Test warning messages are logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.warning("Test warning message")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "WARNING" in content
        assert "Test warning message" in content

    def test_logger_debug_message(self, tmp_logs_dir):
        """Test debug messages are logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.debug("Test debug message")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "DEBUG" in content
        assert "Test debug message" in content

    def test_job_start_logged(self, tmp_logs_dir):
        """Test job start is logged with files and recipe."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.job_start(["file1.mp4", "file2.mkv"], "Test Recipe")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "JOB START" in content
        assert "Test Recipe" in content
        assert "file1.mp4" in content

    def test_job_end_success(self, tmp_logs_dir):
        """Test successful job end is logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.job_end(True, "Test Recipe")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "JOB END" in content
        assert "SUCCESS" in content

    def test_job_end_failure(self, tmp_logs_dir):
        """Test failed job end is logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.job_end(False, "Test Recipe")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "JOB END" in content
        assert "FAILED" in content

    def test_item_start_logged(self, tmp_logs_dir):
        """Test item start is logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.item_start("video.mp4")
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "ITEM START" in content
        assert "video.mp4" in content

    def test_item_end_success(self, tmp_logs_dir):
        """Test successful item end is logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.item_end("video.mp4", True)
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "ITEM END" in content
        assert "SUCCESS" in content

    def test_item_end_failure(self, tmp_logs_dir):
        """Test failed item end is logged."""
        logger = MonicaLogger(tmp_logs_dir)
        logger.item_end("video.mp4", False)
        flush_logger(logger)

        log_file = tmp_logs_dir / "monica.log"
        content = log_file.read_text()

        assert "ITEM END" in content
        assert "FAILED" in content


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self, tmp_logs_dir):
        """Test get_logger returns a logger instance."""
        logger = get_logger(tmp_logs_dir)

        assert logger is not None
        assert isinstance(logger, MonicaLogger)

    def test_get_logger_singleton(self, tmp_logs_dir):
        """Test get_logger returns same instance."""
        logger1 = get_logger(tmp_logs_dir)
        logger2 = get_logger(tmp_logs_dir)

        assert logger1 is logger2

    def test_get_logger_without_dir(self, tmp_logs_dir, monkeypatch):
        """Test get_logger works after initial creation."""
        # First call with directory
        logger1 = get_logger(tmp_logs_dir)

        # Subsequent calls without directory
        logger2 = get_logger()

        assert logger2 is logger1
