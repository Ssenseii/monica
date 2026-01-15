"""Tests for src/monica/recipes.py"""

import pytest
import json
from pathlib import Path

from monica.recipes import (
    Recipe,
    get_recipes_by_category,
    get_all_recipes,
    get_input_extensions_for_category,
    load_custom_recipes,
    save_custom_recipes,
    VIDEO_RECIPES,
    AUDIO_RECIPES,
    SHORTFORM_RECIPES,
    BUILTIN_RECIPES,
)


class TestRecipeDataclass:
    """Tests for Recipe dataclass."""

    def test_recipe_creation(self, sample_recipe):
        """Test basic recipe instantiation."""
        assert sample_recipe.name == "Test Recipe"
        assert sample_recipe.category == "video"
        assert sample_recipe.extension == ".mp4"
        assert sample_recipe.ffmpeg_args == ["-c:v", "libx264", "-crf", "23"]
        assert sample_recipe.description == "A test recipe"
        assert sample_recipe.input_extensions == [".avi", ".mkv", ".mov"]

    def test_recipe_with_constraints(self, sample_recipe_with_constraints):
        """Test recipe with duration/size constraints."""
        assert sample_recipe_with_constraints.max_duration_seconds == 60
        assert sample_recipe_with_constraints.max_file_size_mb == 100

    def test_recipe_default_constraints(self, sample_recipe):
        """Test default constraint values are None."""
        assert sample_recipe.max_duration_seconds is None
        assert sample_recipe.max_file_size_mb is None

    def test_recipe_to_dict(self, sample_recipe):
        """Test recipe serialization to dict."""
        result = sample_recipe.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "Test Recipe"
        assert result["category"] == "video"
        assert result["extension"] == ".mp4"
        assert result["ffmpeg_args"] == ["-c:v", "libx264", "-crf", "23"]

    def test_recipe_from_dict(self):
        """Test recipe deserialization from dict."""
        data = {
            "name": "From Dict Recipe",
            "category": "audio",
            "extension": ".mp3",
            "ffmpeg_args": ["-c:a", "libmp3lame"],
            "description": "Created from dict",
            "input_extensions": [".wav"],
            "max_duration_seconds": None,
            "max_file_size_mb": None,
        }

        recipe = Recipe.from_dict(data)

        assert recipe.name == "From Dict Recipe"
        assert recipe.category == "audio"
        assert recipe.extension == ".mp3"

    def test_recipe_roundtrip(self, sample_recipe):
        """Test serialization/deserialization roundtrip."""
        data = sample_recipe.to_dict()
        restored = Recipe.from_dict(data)

        assert restored.name == sample_recipe.name
        assert restored.category == sample_recipe.category
        assert restored.extension == sample_recipe.extension
        assert restored.ffmpeg_args == sample_recipe.ffmpeg_args


class TestGetRecipesByCategory:
    """Tests for get_recipes_by_category function."""

    def test_get_video_recipes(self):
        """Test retrieving video recipes."""
        recipes = get_recipes_by_category("video")

        assert len(recipes) > 0
        assert all(r.category == "video" for r in recipes)

    def test_get_audio_recipes(self):
        """Test retrieving audio recipes."""
        recipes = get_recipes_by_category("audio")

        assert len(recipes) > 0
        assert all(r.category == "audio" for r in recipes)

    def test_get_shortform_recipes(self):
        """Test retrieving shortform recipes."""
        recipes = get_recipes_by_category("shortform")

        assert len(recipes) > 0
        assert all(r.category == "shortform" for r in recipes)

    def test_get_invalid_category(self):
        """Test retrieving non-existent category returns empty list."""
        recipes = get_recipes_by_category("nonexistent")

        assert recipes == []

    def test_get_empty_category(self):
        """Test retrieving empty string category."""
        recipes = get_recipes_by_category("")

        assert recipes == []


class TestGetAllRecipes:
    """Tests for get_all_recipes function."""

    def test_returns_dict(self):
        """Test that get_all_recipes returns a dictionary."""
        result = get_all_recipes()

        assert isinstance(result, dict)

    def test_contains_all_categories(self):
        """Test that all expected categories are present."""
        result = get_all_recipes()

        expected_categories = ["video", "audio", "extract", "resize", "remux", "youtube", "shortform"]
        for category in expected_categories:
            assert category in result

    def test_returns_copy(self):
        """Test that modifying result doesn't affect original."""
        result = get_all_recipes()
        result["new_category"] = []

        assert "new_category" not in BUILTIN_RECIPES


class TestGetInputExtensionsForCategory:
    """Tests for get_input_extensions_for_category function."""

    def test_video_extensions(self):
        """Test video category has expected extensions."""
        extensions = get_input_extensions_for_category("video")

        assert ".mp4" in extensions
        assert ".mkv" in extensions
        assert ".avi" in extensions

    def test_audio_extensions(self):
        """Test audio category has expected extensions."""
        extensions = get_input_extensions_for_category("audio")

        assert ".mp3" in extensions
        assert ".wav" in extensions
        assert ".flac" in extensions

    def test_invalid_category(self):
        """Test invalid category returns empty list."""
        extensions = get_input_extensions_for_category("nonexistent")

        assert extensions == []

    def test_extensions_are_sorted(self):
        """Test that extensions are returned sorted."""
        extensions = get_input_extensions_for_category("video")

        assert extensions == sorted(extensions)


class TestBuiltinRecipeCounts:
    """Tests to verify expected recipe counts."""

    def test_video_recipe_count(self):
        """Test VIDEO_RECIPES has expected count."""
        assert len(VIDEO_RECIPES) == 6

    def test_audio_recipe_count(self):
        """Test AUDIO_RECIPES has expected count."""
        assert len(AUDIO_RECIPES) == 8

    def test_shortform_recipe_count(self):
        """Test SHORTFORM_RECIPES has expected count."""
        assert len(SHORTFORM_RECIPES) == 13


class TestCustomRecipesFileIO:
    """Tests for load/save custom recipes."""

    def test_load_custom_recipes_valid(self, tmp_path, sample_custom_recipes_json):
        """Test loading valid custom recipes JSON."""
        recipes_file = tmp_path / "custom_recipes.json"
        recipes_file.write_text(sample_custom_recipes_json)

        recipes = load_custom_recipes(recipes_file)

        assert len(recipes) == 1
        assert recipes[0].name == "Custom Recipe 1"

    def test_load_custom_recipes_missing_file(self, tmp_path):
        """Test loading from non-existent file returns empty list."""
        recipes_file = tmp_path / "nonexistent.json"

        recipes = load_custom_recipes(recipes_file)

        assert recipes == []

    def test_load_custom_recipes_invalid_json(self, tmp_path):
        """Test loading invalid JSON returns empty list."""
        recipes_file = tmp_path / "invalid.json"
        recipes_file.write_text("not valid json {{{")

        recipes = load_custom_recipes(recipes_file)

        assert recipes == []

    def test_load_custom_recipes_empty_array(self, tmp_path):
        """Test loading empty JSON array."""
        recipes_file = tmp_path / "empty.json"
        recipes_file.write_text("[]")

        recipes = load_custom_recipes(recipes_file)

        assert recipes == []

    def test_save_custom_recipes(self, tmp_path, sample_recipe):
        """Test saving custom recipes to file."""
        recipes_file = tmp_path / "saved_recipes.json"

        result = save_custom_recipes([sample_recipe], recipes_file)

        assert result is True
        assert recipes_file.exists()

        # Verify content
        content = json.loads(recipes_file.read_text())
        assert len(content) == 1
        assert content[0]["name"] == "Test Recipe"

    def test_save_and_load_roundtrip(self, tmp_path, sample_recipe):
        """Test save then load produces same recipes."""
        recipes_file = tmp_path / "roundtrip.json"

        save_custom_recipes([sample_recipe], recipes_file)
        loaded = load_custom_recipes(recipes_file)

        assert len(loaded) == 1
        assert loaded[0].name == sample_recipe.name
        assert loaded[0].category == sample_recipe.category
