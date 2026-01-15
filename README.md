# MONICA

**M**edia **O**perations **N**avigator with **I**nteractive **C**ommand-line **A**ssistance

A simple, keyboard-driven interactive CLI application that makes FFmpeg easy to use without exposing FFmpeg syntax.

## Features

- **Interactive menu** - No need to remember command-line flags
- **Keyboard navigation** - Arrow keys to move, Enter to select, Space to multi-select
- **Auto FFmpeg setup** - Automatically downloads FFmpeg if not installed
- **Recipe-based operations** - Pre-configured presets for common tasks
- **Progress display** - Visual progress bar during conversions
- **Multi-file processing** - Select multiple files and process them in queue
- **Cross-platform** - Works on Windows and Linux

## Supported Operations

| Category | Description |
|----------|-------------|
| **Convert Video** | MP4, MKV, WebM, AVI with various codecs (H.264, H.265, VP9) |
| **Convert Audio** | MP3, AAC, FLAC, WAV, OGG, Opus |
| **Extract Audio** | Extract audio tracks from video files |
| **Resize/Compress** | Scale to 1080p, 720p, 480p, 360p or compress with quality presets |
| **Remux** | Change container format without re-encoding |

## Installation

On first run, MONICA will check for FFmpeg and offer to download it automatically if not found.

### Prerequisites

- Python 3.10 or higher
- uv (optional)
- FFmpeg (auto-downloaded if not present)

### Method 1: Using uv or pip

```bash
uv tool install git+https://github.com/tclasen/monica
```

or

```bash
pip install git+https://github.com/tclasen/monica
```

### Method 2: Local git clone and install (development mode)

1. Clone the repository:
   ```bash
   git clone https://github.com/tclasen/monica.git
   cd monica
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

   or

   ```bash
   pip install -e .
   ```

## Usage

1. Place your input files in the `/import` folder
2. Run `monica`
3. Use arrow keys to navigate the menu
4. Select an operation (e.g., "Convert video")
5. Choose a preset (e.g., "MP4 (H.264)")
6. Select files to process using Space, then press Enter
7. Converted files appear in the `/export` folder

### Output Naming

Output files are automatically named with a timestamp:
```
<original_name>_<YYYYMMDD_HHMMSS>_<FORMAT>_converted.<ext>
```

Example: `video_20260108_143210_MP4_converted.mp4`

## Project Structure

```
├── README.md           # This file
├── docs/               # Documentation
│   ├── introduction.md # Project specification
│   ├── usage.md        # User guide
│   └── recipes.md      # Recipe documentation
├── logs/               # Log files
├── src
│   └── monica
│       ├── __init__.py
│       ├── executor.py         # Job execution
│       ├── ffmpeg_manager.py   # FFmpeg detection/download
│       ├── file_selector.py    # File picker
│       ├── logger.py           # Logging
│       ├── main.py             # Entry point
│       ├── menu.py             # Interactive menus
│       └── recipes.py          # Conversion presets
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_executor.py
│   ├── test_ffmpeg_manager.py
│   ├── test_file_selector.py
│   ├── test_logger.py
│   ├── test_main.py
│   └── test_recipes.py
├── pyproject.toml      # Project Metadata
└── uv.lock             # Dependency lock file
```

## Configuration

### Custom Recipes

You can add custom recipes by creating a `custom_recipes.json` file in the project root. See [docs/recipes.md](docs/recipes.md) for details.

## Dependencies

- `questionary` - Interactive prompts and menus
- `colorama` - Cross-platform colored terminal output
- `requests` - HTTP client for FFmpeg download

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
