#!/usr/bin/env python3
"""MONICA - FFmpeg Interactive CLI Tool

Entry point for the application.
"""

import sys
from pathlib import Path

# Initialize colorama for Windows
from colorama import init, Fore, Style
init()

from monica.ffmpeg_manager import ensure_ffmpeg
from monica.logger import get_logger
from monica.menu import run_menu_loop


def setup_directories(base_dir: Path) -> tuple[Path, Path, Path]:
    """Create required directories if they don't exist.

    Args:
        base_dir: The base directory for the application

    Returns:
        Tuple of (import_dir, export_dir, logs_dir)
    """
    import_dir = base_dir / "import"
    export_dir = base_dir / "export"
    logs_dir = base_dir / "logs"

    for directory in [import_dir, export_dir, logs_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    return import_dir, export_dir, logs_dir


def main() -> int:
    """Main entry point."""
    base_dir = Path().resolve()

    # Setup directories
    import_dir, export_dir, logs_dir = setup_directories(base_dir)

    # Initialize logger
    logger = get_logger(logs_dir)
    logger.info("MONICA started")

    # Check/download FFmpeg
    ffmpeg_path = ensure_ffmpeg(base_dir)
    if ffmpeg_path is None:
        logger.error("FFmpeg not available - exiting")
        return 1

    logger.info(f"Using FFmpeg: {ffmpeg_path}")

    # Run the main menu loop
    try:
        run_menu_loop(
            ffmpeg_path=ffmpeg_path,
            base_dir=base_dir,
            import_dir=import_dir,
            export_dir=export_dir,
            logs_dir=logs_dir
        )
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted. Exiting...{Style.RESET_ALL}")
        logger.info("MONICA interrupted by user")
        return 130
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        logger.error(f"Unexpected error: {e}")
        return 1

    logger.info("MONICA exited normally")
    return 0


if __name__ == "__main__":
    sys.exit(main())
