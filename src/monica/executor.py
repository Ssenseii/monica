"""FFmpeg job executor with progress display."""

import re
import subprocess
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style

from monica.recipes import Recipe
from monica.logger import get_logger


# Spinner animation frames
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class ProgressIndicator:
    """Animated progress indicator for long-running operations."""

    def __init__(self, message: str = "Processing"):
        self.message = message
        self.running = False
        self.thread = None
        self.start_time = None
        self.frame_idx = 0

    def _animate(self):
        """Animation loop running in background thread."""
        while self.running:
            elapsed = time.time() - self.start_time
            spinner = SPINNER_FRAMES[self.frame_idx % len(SPINNER_FRAMES)]
            print(f"\r{Fore.CYAN}{spinner}{Style.RESET_ALL} {self.message}... ({elapsed:.0f}s)", end="", flush=True)
            self.frame_idx += 1
            time.sleep(0.1)

    def start(self):
        """Start the animated indicator."""
        self.running = True
        self.start_time = time.time()
        self.frame_idx = 0
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self, clear: bool = True):
        """Stop the animated indicator."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        if clear:
            # Clear the line
            print("\r" + " " * 60 + "\r", end="", flush=True)

    def update_message(self, message: str):
        """Update the status message."""
        self.message = message


def generate_output_filename(input_file: Path, recipe: Recipe, export_dir: Path) -> Path:
    """Generate the output filename based on naming convention.

    Format: <original_name>_<YYYYMMDD_HHMMSS>_<format>_converted.<ext>
    """
    original_name = input_file.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    format_name = recipe.extension.lstrip(".").upper()

    output_name = f"{original_name}_{timestamp}_{format_name}_converted{recipe.extension}"
    return export_dir / output_name


def parse_duration(line: str) -> float | None:
    """Parse duration from FFmpeg output (in seconds)."""
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)", line)
    if match:
        hours, minutes, seconds, centiseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
    return None


def parse_time(line: str) -> float | None:
    """Parse current time from FFmpeg progress output (in seconds)."""
    match = re.search(r"time=(\d+):(\d+):(\d+)\.(\d+)", line)
    if match:
        hours, minutes, seconds, centiseconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
    return None


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    if seconds < 0:
        seconds = 0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def display_progress_bar(percent: float, elapsed: float = 0, eta: float = 0, width: int = 30) -> None:
    """Display a progress bar with elapsed time and ETA."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)

    elapsed_str = format_time(elapsed)

    if eta > 0 and percent < 100:
        eta_str = format_time(eta)
        print(f"\r    {Fore.GREEN}{bar}{Style.RESET_ALL} {percent:5.1f}% | {elapsed_str} elapsed | ETA: {eta_str}  ", end="", flush=True)
    else:
        print(f"\r    {Fore.GREEN}{bar}{Style.RESET_ALL} {percent:5.1f}% | {elapsed_str} elapsed  ", end="", flush=True)


def run_ffmpeg_job(
    ffmpeg_path: str,
    input_file: Path,
    output_file: Path,
    recipe: Recipe
) -> tuple[bool, str]:
    """Run a single FFmpeg job with progress display.

    Args:
        ffmpeg_path: Path to FFmpeg executable
        input_file: Input file path
        output_file: Output file path
        recipe: The recipe to apply

    Returns:
        Tuple of (success, error_message)
    """
    # Use -stats for stderr progress (more reliable than -progress pipe on Windows)
    cmd = [
        ffmpeg_path,
        "-i", str(input_file),
        "-y",  # Overwrite output
        *recipe.ffmpeg_args,
        str(output_file)
    ]

    logger = get_logger()
    logger.debug(f"Running command: {' '.join(cmd)}")

    # Start spinner for initialization
    spinner = ProgressIndicator("Analyzing file")
    spinner.start()

    try:
        # First, get the duration using ffprobe-style call
        duration_cmd = [
            ffmpeg_path,
            "-i", str(input_file),
            "-f", "null",
            "-"
        ]

        duration = None
        probe_result = subprocess.run(
            duration_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        # Duration is in stderr
        for line in probe_result.stderr.split("\n"):
            duration = parse_duration(line)
            if duration:
                break

        spinner.stop()
        print(f"    Duration: {format_time(duration) if duration else 'unknown'}")

        # Run the actual conversion with stderr for progress
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        job_start_time = time.time()
        last_percent = 0
        stderr_output = []

        # Read stderr in a separate thread to avoid blocking
        def read_stderr():
            for line in process.stderr:
                stderr_output.append(line)

        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        # Poll for progress
        while process.poll() is None:
            time.sleep(0.3)
            elapsed = time.time() - job_start_time

            # Parse latest stderr for time= pattern
            current_time = 0
            for line in reversed(stderr_output[-20:]):  # Check last 20 lines
                time_match = parse_time(line)
                if time_match:
                    current_time = time_match
                    break

            if duration and duration > 0 and current_time > 0:
                percent = min(99.9, (current_time / duration) * 100)
                eta = 0
                if percent > 0:
                    eta = (elapsed / percent) * (100 - percent)
                display_progress_bar(percent, elapsed, eta)
                last_percent = percent
            else:
                # Show elapsed time even without duration
                spinner_char = SPINNER_FRAMES[int(elapsed * 10) % len(SPINNER_FRAMES)]
                print(f"\r    {Fore.CYAN}{spinner_char}{Style.RESET_ALL} Encoding... ({format_time(elapsed)} elapsed)  ", end="", flush=True)

        # Process finished
        stderr_thread.join(timeout=2)
        elapsed = time.time() - job_start_time

        if process.returncode == 0:
            display_progress_bar(100, elapsed, 0)
            print()  # New line after progress bar
            return True, ""
        else:
            print()  # New line
            full_stderr = "".join(stderr_output)
            logger.error(f"FFmpeg failed: {full_stderr}")
            return False, full_stderr

    except subprocess.TimeoutExpired:
        spinner.stop()
        process.kill()
        return False, "Process timed out"
    except Exception as e:
        spinner.stop()
        return False, str(e)


def execute_jobs(
    ffmpeg_path: str,
    files: list[Path],
    recipe: Recipe,
    export_dir: Path
) -> bool:
    """Execute a queue of FFmpeg jobs.

    Processes files one at a time. Stops immediately on error.

    Args:
        ffmpeg_path: Path to FFmpeg executable
        files: List of input files
        recipe: The recipe to apply
        export_dir: The export directory

    Returns:
        True if all jobs completed successfully, False otherwise
    """
    logger = get_logger()
    logger.job_start([str(f) for f in files], recipe.name)

    total = len(files)
    print(f"\n{Fore.CYAN}Processing {total} file(s) with '{recipe.name}'...{Style.RESET_ALL}")

    for i, input_file in enumerate(files, 1):
        output_file = generate_output_filename(input_file, recipe, export_dir)

        print(f"\n{Fore.CYAN}[{i}/{total}]{Style.RESET_ALL} {input_file.name}")
        print(f"    -> {output_file.name}")

        logger.item_start(input_file.name)

        success, error = run_ffmpeg_job(ffmpeg_path, input_file, output_file, recipe)

        if success:
            logger.item_end(input_file.name, True)
            print(f"{Fore.GREEN}Done!{Style.RESET_ALL}")
        else:
            logger.item_end(input_file.name, False)
            logger.error(f"Error processing {input_file.name}: {error}")

            print(f"\n{Fore.RED}Error:{Style.RESET_ALL} Failed to process {input_file.name}")
            print(f"{Fore.RED}Job stopped. See logs for details.{Style.RESET_ALL}")

            logger.job_end(False, recipe.name)
            return False

    logger.job_end(True, recipe.name)
    print(f"\n{Fore.GREEN}All {total} file(s) processed successfully!{Style.RESET_ALL}")
    return True
