"""FFmpeg detection and auto-download manager."""

import os
import sys
import platform
import shutil
import subprocess
import zipfile
import tarfile
from pathlib import Path
from colorama import Fore, Style

from monica.logger import log_info, log_error, log_warning


# FFmpeg download URLs
FFMPEG_URLS = {
    "windows": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
    "linux": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
}


def get_os() -> str:
    """Detect the current operating system."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def check_ffmpeg_in_path() -> bool:
    """Check if FFmpeg is available in the system PATH."""
    return shutil.which("ffmpeg") is not None


def check_ffmpeg_local(base_dir: Path) -> str | None:
    """Check if FFmpeg exists in the local ffmpeg directory."""
    ffmpeg_dir = base_dir / "ffmpeg"
    if get_os() == "windows":
        ffmpeg_path = ffmpeg_dir / "ffmpeg.exe"
    else:
        ffmpeg_path = ffmpeg_dir / "ffmpeg"

    if ffmpeg_path.exists():
        return str(ffmpeg_path)
    return None


def get_ffmpeg_path(base_dir: Path) -> str | None:
    """Get the path to FFmpeg, checking local first then PATH."""
    local_path = check_ffmpeg_local(base_dir)
    if local_path:
        return local_path
    if check_ffmpeg_in_path():
        return "ffmpeg"
    return None


def download_ffmpeg(base_dir: Path) -> bool:
    """Download and extract FFmpeg to the local ffmpeg directory."""
    import requests

    os_type = get_os()
    if os_type == "unknown":
        log_error("Unsupported operating system for auto-download")
        return False

    url = FFMPEG_URLS.get(os_type)
    if not url:
        log_error(f"No download URL for {os_type}")
        return False

    ffmpeg_dir = base_dir / "ffmpeg"
    ffmpeg_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{Fore.YELLOW}Downloading FFmpeg...{Style.RESET_ALL}")
    log_info(f"Downloading FFmpeg from {url}")

    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        if os_type == "windows":
            archive_path = ffmpeg_dir / "ffmpeg.zip"
        else:
            archive_path = ffmpeg_dir / "ffmpeg.tar.xz"

        with open(archive_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = int(downloaded * 100 / total_size)
                        bar_length = 30
                        filled = int(bar_length * downloaded / total_size)
                        bar = "=" * filled + "-" * (bar_length - filled)
                        print(f"\r[{bar}] {percent}%", end="", flush=True)

        print()  # New line after progress
        log_info("Download complete, extracting...")
        print(f"{Fore.YELLOW}Extracting FFmpeg...{Style.RESET_ALL}")

        # Extract the archive
        if os_type == "windows":
            with zipfile.ZipFile(archive_path, "r") as zf:
                # Find the ffmpeg.exe in the archive
                for name in zf.namelist():
                    if name.endswith("bin/ffmpeg.exe"):
                        # Extract just the exe
                        source = zf.open(name)
                        target = ffmpeg_dir / "ffmpeg.exe"
                        with open(target, "wb") as f:
                            f.write(source.read())
                        break
                    if name.endswith("bin/ffprobe.exe"):
                        source = zf.open(name)
                        target = ffmpeg_dir / "ffprobe.exe"
                        with open(target, "wb") as f:
                            f.write(source.read())
        else:
            with tarfile.open(archive_path, "r:xz") as tf:
                for member in tf.getmembers():
                    if member.name.endswith("bin/ffmpeg"):
                        member.name = "ffmpeg"
                        tf.extract(member, ffmpeg_dir)
                        os.chmod(ffmpeg_dir / "ffmpeg", 0o755)
                    elif member.name.endswith("bin/ffprobe"):
                        member.name = "ffprobe"
                        tf.extract(member, ffmpeg_dir)
                        os.chmod(ffmpeg_dir / "ffprobe", 0o755)

        # Clean up archive
        archive_path.unlink()

        log_info("FFmpeg extracted successfully")
        print(f"{Fore.GREEN}FFmpeg installed successfully!{Style.RESET_ALL}")
        return True

    except requests.RequestException as e:
        log_error(f"Failed to download FFmpeg: {e}")
        print(f"{Fore.RED}Failed to download FFmpeg: {e}{Style.RESET_ALL}")
        return False
    except (zipfile.BadZipFile, tarfile.TarError) as e:
        log_error(f"Failed to extract FFmpeg: {e}")
        print(f"{Fore.RED}Failed to extract FFmpeg: {e}{Style.RESET_ALL}")
        return False
    except Exception as e:
        log_error(f"Unexpected error during FFmpeg setup: {e}")
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        return False


def verify_ffmpeg(ffmpeg_path: str) -> bool:
    """Verify that FFmpeg works by running a version check."""
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def ensure_ffmpeg(base_dir: Path) -> str | None:
    """Ensure FFmpeg is available, downloading if necessary.

    Returns the path to FFmpeg, or None if it couldn't be set up.
    """
    print(f"\n{Fore.CYAN}Checking FFmpeg availability...{Style.RESET_ALL}")

    # Check if FFmpeg is already available
    ffmpeg_path = get_ffmpeg_path(base_dir)

    if ffmpeg_path and verify_ffmpeg(ffmpeg_path):
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} FFmpeg is available")
        log_info(f"FFmpeg found at: {ffmpeg_path}")
        return ffmpeg_path

    # FFmpeg not found, offer to download
    print(f"{Fore.RED}[X]{Style.RESET_ALL} FFmpeg not found")
    log_warning("FFmpeg not found in PATH or local directory")

    os_type = get_os()
    if os_type == "unknown":
        print(f"\n{Fore.RED}Unsupported operating system.{Style.RESET_ALL}")
        print("Please install FFmpeg manually and ensure it's in your PATH.")
        return None

    print(f"\n{Fore.YELLOW}FFmpeg is required to use MONICA.{Style.RESET_ALL}")
    print("Would you like to download it automatically?")

    import questionary
    if questionary.confirm("Download FFmpeg now?", default=True).ask():
        if download_ffmpeg(base_dir):
            ffmpeg_path = get_ffmpeg_path(base_dir)
            if ffmpeg_path and verify_ffmpeg(ffmpeg_path):
                return ffmpeg_path

    print(f"\n{Fore.RED}FFmpeg is not available. Cannot continue.{Style.RESET_ALL}")
    return None


def print_ffmpeg_status(base_dir: Path) -> None:
    """Print the current FFmpeg status with colored indicator."""
    ffmpeg_path = get_ffmpeg_path(base_dir)

    if ffmpeg_path and verify_ffmpeg(ffmpeg_path):
        location = "local" if "ffmpeg" in str(base_dir) and ffmpeg_path != "ffmpeg" else "PATH"
        print(f"FFmpeg: {Fore.GREEN}Available{Style.RESET_ALL} ({location})")
    else:
        print(f"FFmpeg: {Fore.RED}Not Available{Style.RESET_ALL}")
