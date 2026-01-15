"""File selection UI for MONICA."""

from pathlib import Path
import questionary
from colorama import Fore, Style


def get_files_in_directory(directory: Path, extensions: list[str] = None) -> list[Path]:
    """Get all files in a directory, optionally filtered by extension.

    Args:
        directory: The directory to search
        extensions: List of extensions to filter by (e.g., ['.mp4', '.mkv'])

    Returns:
        List of file paths
    """
    if not directory.exists():
        return []

    files = []
    for item in directory.iterdir():
        if item.is_file():
            if extensions is None or item.suffix.lower() in extensions:
                files.append(item)

    return sorted(files, key=lambda x: x.name.lower())


def select_files(
    import_dir: Path,
    extensions: list[str] = None,
    message: str = "Select files to process"
) -> list[Path]:
    """Display a multi-select file picker for the import directory.

    Args:
        import_dir: The import directory path
        extensions: Optional list of extensions to filter by
        message: The prompt message to display

    Returns:
        List of selected file paths, or empty list if cancelled
    """
    files = get_files_in_directory(import_dir, extensions)

    if not files:
        if extensions:
            ext_str = ", ".join(extensions)
            print(f"\n{Fore.YELLOW}No files found in /import with extensions: {ext_str}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}No files found in /import{Style.RESET_ALL}")
        print(f"Place your files in: {import_dir}")
        return []

    # Create choices with file info
    choices = []
    for f in files:
        size = f.stat().st_size
        size_str = format_size(size)
        choices.append(questionary.Choice(
            title=f"{f.name} ({size_str})",
            value=f
        ))

    print()  # Add spacing
    selected = questionary.checkbox(
        message,
        choices=choices,
        instruction="(Use arrow keys to navigate, Space to select, Enter to confirm)"
    ).ask()

    if selected is None:
        return []

    return selected


def format_size(size_bytes: int) -> str:
    """Format a file size in bytes to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def display_selected_files(files: list[Path]) -> None:
    """Display the selected files to the user."""
    if not files:
        return

    print(f"\n{Fore.CYAN}Selected {len(files)} file(s):{Style.RESET_ALL}")
    for f in files:
        print(f"  - {f.name}")
