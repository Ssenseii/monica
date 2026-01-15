"""Tests for src/monica/executor.py"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import time
import threading

from monica.executor import (
    parse_duration,
    parse_time,
    format_time,
    generate_output_filename,
    display_progress_bar,
    ProgressIndicator,
)
from monica.recipes import Recipe


class TestParseDuration:
    """Tests for parse_duration function."""

    def test_parse_duration_valid(self):
        """Test parsing valid duration string."""
        line = "  Duration: 00:02:30.50, start: 0.000000"
        result = parse_duration(line)

        assert result == 150.5  # 2*60 + 30 + 0.5

    def test_parse_duration_hours(self):
        """Test parsing duration with hours."""
        line = "Duration: 01:30:00.00, start: 0.000000"
        result = parse_duration(line)

        assert result == 5400  # 1*3600 + 30*60

    def test_parse_duration_zero(self):
        """Test parsing zero duration."""
        line = "Duration: 00:00:00.00"
        result = parse_duration(line)

        assert result == 0

    def test_parse_duration_invalid(self):
        """Test parsing invalid string returns None."""
        line = "No duration here"
        result = parse_duration(line)

        assert result is None

    def test_parse_duration_empty(self):
        """Test parsing empty string returns None."""
        result = parse_duration("")

        assert result is None

    def test_parse_duration_centiseconds(self):
        """Test parsing with centiseconds."""
        line = "Duration: 00:00:10.99"
        result = parse_duration(line)

        assert result == pytest.approx(10.99, rel=0.01)


class TestParseTime:
    """Tests for parse_time function."""

    def test_parse_time_valid(self):
        """Test parsing valid time string."""
        line = "frame=  100 fps= 30 time=00:01:15.50 bitrate=1000kbps"
        result = parse_time(line)

        assert result == 75.5  # 1*60 + 15 + 0.5

    def test_parse_time_hours(self):
        """Test parsing time with hours."""
        line = "time=02:30:45.00"
        result = parse_time(line)

        assert result == 9045  # 2*3600 + 30*60 + 45

    def test_parse_time_zero(self):
        """Test parsing zero time."""
        line = "time=00:00:00.00"
        result = parse_time(line)

        assert result == 0

    def test_parse_time_invalid(self):
        """Test parsing invalid string returns None."""
        line = "No time here"
        result = parse_time(line)

        assert result is None

    def test_parse_time_empty(self):
        """Test parsing empty string returns None."""
        result = parse_time("")

        assert result is None


class TestFormatTime:
    """Tests for format_time function."""

    def test_format_time_seconds_only(self):
        """Test formatting seconds only."""
        result = format_time(45)

        assert result == "00:45"

    def test_format_time_minutes_seconds(self):
        """Test formatting minutes and seconds."""
        result = format_time(125)

        assert result == "02:05"

    def test_format_time_hours(self):
        """Test formatting with hours."""
        result = format_time(3725)

        assert result == "01:02:05"

    def test_format_time_zero(self):
        """Test formatting zero."""
        result = format_time(0)

        assert result == "00:00"

    def test_format_time_negative(self):
        """Test formatting negative value (should clamp to 0)."""
        result = format_time(-10)

        assert result == "00:00"

    def test_format_time_large(self):
        """Test formatting large value."""
        result = format_time(36000)  # 10 hours

        assert result == "10:00:00"

    def test_format_time_float(self):
        """Test formatting float value (truncates)."""
        result = format_time(65.7)

        assert result == "01:05"


class TestGenerateOutputFilename:
    """Tests for generate_output_filename function."""

    def test_generates_correct_format(self, sample_recipe, tmp_export_dir):
        """Test output filename follows naming convention."""
        input_file = Path("/path/to/video.avi")

        result = generate_output_filename(input_file, sample_recipe, tmp_export_dir)

        # Should be: video_YYYYMMDD_HHMMSS_MP4_converted.mp4
        assert result.parent == tmp_export_dir
        assert result.suffix == ".mp4"
        assert "video_" in result.stem
        assert "_MP4_converted" in result.stem

    def test_preserves_original_name(self, sample_recipe, tmp_export_dir):
        """Test original filename is preserved in output."""
        input_file = Path("/path/to/my_cool_video.mkv")

        result = generate_output_filename(input_file, sample_recipe, tmp_export_dir)

        assert "my_cool_video_" in result.stem

    def test_uses_recipe_extension(self, tmp_export_dir):
        """Test output uses recipe's extension."""
        input_file = Path("/path/to/video.avi")
        mp3_recipe = Recipe(
            name="MP3",
            category="audio",
            extension=".mp3",
            ffmpeg_args=[],
            input_extensions=[]
        )

        result = generate_output_filename(input_file, mp3_recipe, tmp_export_dir)

        assert result.suffix == ".mp3"

    def test_includes_timestamp(self, sample_recipe, tmp_export_dir):
        """Test output includes timestamp."""
        input_file = Path("/path/to/video.avi")

        result = generate_output_filename(input_file, sample_recipe, tmp_export_dir)

        # Timestamp format: YYYYMMDD_HHMMSS
        # The stem should contain an 8-digit date and 6-digit time
        stem = result.stem
        parts = stem.split("_")
        # Should have: name, date, time, FORMAT, converted
        assert len(parts) >= 4


class TestProgressIndicator:
    """Tests for ProgressIndicator class."""

    def test_indicator_starts_and_stops(self):
        """Test indicator can start and stop without error."""
        indicator = ProgressIndicator("Testing")

        indicator.start()
        time.sleep(0.2)  # Let it run briefly
        indicator.stop()

        assert indicator.running is False

    def test_indicator_updates_message(self):
        """Test indicator message can be updated."""
        indicator = ProgressIndicator("Initial")

        indicator.update_message("Updated")

        assert indicator.message == "Updated"

    def test_indicator_tracks_start_time(self):
        """Test indicator tracks start time."""
        indicator = ProgressIndicator("Testing")

        indicator.start()
        time.sleep(0.1)
        indicator.stop()

        assert indicator.start_time is not None

    def test_indicator_thread_is_daemon(self):
        """Test indicator thread is a daemon thread."""
        indicator = ProgressIndicator("Testing")

        indicator.start()

        assert indicator.thread.daemon is True

        indicator.stop()


class TestDisplayProgressBar:
    """Tests for display_progress_bar function (output only)."""

    def test_display_progress_bar_runs(self, capsys):
        """Test progress bar displays without error."""
        display_progress_bar(50.0, 10.0, 10.0)

        captured = capsys.readouterr()
        assert "50.0%" in captured.out

    def test_display_progress_bar_100_percent(self, capsys):
        """Test 100% progress bar."""
        display_progress_bar(100.0, 60.0, 0)

        captured = capsys.readouterr()
        assert "100.0%" in captured.out

    def test_display_progress_bar_zero(self, capsys):
        """Test 0% progress bar."""
        display_progress_bar(0.0, 0.0, 0)

        captured = capsys.readouterr()
        assert "0.0%" in captured.out
