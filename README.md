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

### Prerequisites

- Python 3.10 or higher
- FFmpeg (auto-downloaded if not present)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/monica.git
   cd monica
   ```

2. Create and activate virtual environment:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```
   
   **Note:** Make sure the virtual environment is activated before running the application. You should see `(venv)` in your terminal prompt.

On first run, MONICA will check for FFmpeg and offer to download it automatically if not found.

## Usage

1. Place your input files in the `/import` folder
2. Activate virtual environment (if not already activated):
   ```bash
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate      # Windows
   ```
3. Run `python main.py`
4. Use arrow keys to navigate the menu
5. Select an operation (e.g., "Convert video")
6. Choose a preset (e.g., "MP4 (H.264)")
7. Select files to process using Space, then press Enter
8. Converted files appear in the `/export` folder

### Quick Access (Optional)

You can create an alias or wrapper script to run MONICA from any directory without manually activating the virtual environment. See the project's installation script or create a wrapper that activates the venv automatically.

### Output Naming

Output files are automatically named with a timestamp:
```
<original_name>_<YYYYMMDD_HHMMSS>_<FORMAT>_converted.<ext>
```

Example: `video_20260108_143210_MP4_converted.mp4`

## Project Structure

```
monica/
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── import/             # Input files go here
├── export/             # Output files appear here
├── logs/               # Log files
├── docs/               # Documentation
│   ├── introduction.md # Project specification
│   ├── usage.md        # User guide
│   └── recipes.md      # Recipe documentation
└── src/
    ├── __init__.py
    ├── ffmpeg_manager.py   # FFmpeg detection/download
    ├── menu.py             # Interactive menus
    ├── recipes.py          # Conversion presets
    ├── file_selector.py    # File picker
    ├── executor.py         # Job execution
    └── logger.py           # Logging
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
