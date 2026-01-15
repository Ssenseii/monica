"""Rolling log handler for MONICA."""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path


class MonicaLogger:
    """Handles logging for MONICA with rolling file support."""

    _instance = None
    _logger = None

    def __new__(cls, logs_dir: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, logs_dir: str = None):
        if self._logger is not None:
            return

        if logs_dir is None:
            logs_dir = Path(__file__).parent.parent / "logs"

        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger("monica")
        self._logger.setLevel(logging.DEBUG)

        if not self._logger.handlers:
            log_file = self.logs_dir / "monica.log"
            handler = RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=5,
                encoding="utf-8"
            )

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(message)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)

    def job_start(self, files: list, recipe_name: str) -> None:
        """Log the start of a job."""
        self.info(f"JOB START: Recipe '{recipe_name}' with {len(files)} file(s)")
        for f in files:
            self.info(f"  - {f}")

    def job_end(self, success: bool, recipe_name: str) -> None:
        """Log the end of a job."""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"JOB END: Recipe '{recipe_name}' - {status}")

    def item_start(self, filename: str) -> None:
        """Log start of processing a single item."""
        self.info(f"ITEM START: {filename}")

    def item_end(self, filename: str, success: bool) -> None:
        """Log end of processing a single item."""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"ITEM END: {filename} - {status}")


# Global logger instance
_logger = None


def get_logger(logs_dir: str = None) -> MonicaLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = MonicaLogger(logs_dir)
    return _logger


def log_info(message: str) -> None:
    """Log an info message."""
    get_logger().info(message)


def log_warning(message: str) -> None:
    """Log a warning message."""
    get_logger().warning(message)


def log_error(message: str) -> None:
    """Log an error message."""
    get_logger().error(message)


def log_debug(message: str) -> None:
    """Log a debug message."""
    get_logger().debug(message)
