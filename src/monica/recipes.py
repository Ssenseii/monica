"""FFmpeg recipes/presets for MONICA."""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Recipe:
    """Represents an FFmpeg recipe/preset."""
    name: str
    category: str  # video, audio, extract, resize, remux, youtube, shortform
    extension: str
    ffmpeg_args: list[str]
    description: str = ""
    input_extensions: list[str] = field(default_factory=list)
    max_duration_seconds: Optional[int] = None  # Platform duration limit
    max_file_size_mb: Optional[int] = None  # Platform file size limit

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        return cls(**data)


# Built-in video conversion recipes
VIDEO_RECIPES = [
    Recipe(
        name="MP4 (H.264)",
        category="video",
        extension=".mp4",
        ffmpeg_args=["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "128k"],
        description="Standard MP4 with H.264 video and AAC audio",
        input_extensions=[".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mp4", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="MP4 (H.264 High Quality)",
        category="video",
        extension=".mp4",
        ffmpeg_args=["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "aac", "-b:a", "192k"],
        description="High quality MP4 with better compression",
        input_extensions=[".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mp4", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="MP4 (H.265/HEVC)",
        category="video",
        extension=".mp4",
        ffmpeg_args=["-c:v", "libx265", "-preset", "medium", "-crf", "28", "-c:a", "aac", "-b:a", "128k"],
        description="MP4 with H.265 video (smaller files, slower encode)",
        input_extensions=[".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mp4", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="WebM (VP9)",
        category="video",
        extension=".webm",
        ffmpeg_args=["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-c:a", "libopus", "-b:a", "128k"],
        description="WebM with VP9 video and Opus audio",
        input_extensions=[".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mp4", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="MKV (H.264)",
        category="video",
        extension=".mkv",
        ffmpeg_args=["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "128k"],
        description="MKV container with H.264 video",
        input_extensions=[".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mp4", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="AVI (MPEG-4)",
        category="video",
        extension=".avi",
        ffmpeg_args=["-c:v", "mpeg4", "-q:v", "5", "-c:a", "libmp3lame", "-b:a", "192k"],
        description="AVI with MPEG-4 video and MP3 audio",
        input_extensions=[".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mp4", ".m4v", ".mpeg", ".mpg"]
    ),
]

# Built-in audio conversion recipes
AUDIO_RECIPES = [
    Recipe(
        name="MP3 (320 kbps)",
        category="audio",
        extension=".mp3",
        ffmpeg_args=["-vn", "-c:a", "libmp3lame", "-b:a", "320k"],
        description="High quality MP3",
        input_extensions=[".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".mp3", ".opus"]
    ),
    Recipe(
        name="MP3 (192 kbps)",
        category="audio",
        extension=".mp3",
        ffmpeg_args=["-vn", "-c:a", "libmp3lame", "-b:a", "192k"],
        description="Standard quality MP3",
        input_extensions=[".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".mp3", ".opus"]
    ),
    Recipe(
        name="MP3 (128 kbps)",
        category="audio",
        extension=".mp3",
        ffmpeg_args=["-vn", "-c:a", "libmp3lame", "-b:a", "128k"],
        description="Smaller file size MP3",
        input_extensions=[".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".mp3", ".opus"]
    ),
    Recipe(
        name="AAC (256 kbps)",
        category="audio",
        extension=".m4a",
        ffmpeg_args=["-vn", "-c:a", "aac", "-b:a", "256k"],
        description="High quality AAC",
        input_extensions=[".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".mp3", ".opus"]
    ),
    Recipe(
        name="FLAC (Lossless)",
        category="audio",
        extension=".flac",
        ffmpeg_args=["-vn", "-c:a", "flac"],
        description="Lossless audio compression",
        input_extensions=[".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".mp3", ".opus"]
    ),
    Recipe(
        name="WAV (Uncompressed)",
        category="audio",
        extension=".wav",
        ffmpeg_args=["-vn", "-c:a", "pcm_s16le"],
        description="Uncompressed PCM audio",
        input_extensions=[".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".mp3", ".opus"]
    ),
    Recipe(
        name="OGG Vorbis",
        category="audio",
        extension=".ogg",
        ffmpeg_args=["-vn", "-c:a", "libvorbis", "-q:a", "6"],
        description="OGG Vorbis audio",
        input_extensions=[".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".mp3", ".opus"]
    ),
    Recipe(
        name="Opus",
        category="audio",
        extension=".opus",
        ffmpeg_args=["-vn", "-c:a", "libopus", "-b:a", "128k"],
        description="Opus audio codec",
        input_extensions=[".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".mp3", ".opus"]
    ),
]

# Audio extraction recipes (from video)
EXTRACT_RECIPES = [
    Recipe(
        name="Extract to MP3 (320 kbps)",
        category="extract",
        extension=".mp3",
        ffmpeg_args=["-vn", "-c:a", "libmp3lame", "-b:a", "320k"],
        description="Extract audio from video as MP3",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Extract to MP3 (192 kbps)",
        category="extract",
        extension=".mp3",
        ffmpeg_args=["-vn", "-c:a", "libmp3lame", "-b:a", "192k"],
        description="Extract audio from video as MP3 (smaller)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Extract to AAC",
        category="extract",
        extension=".m4a",
        ffmpeg_args=["-vn", "-c:a", "aac", "-b:a", "192k"],
        description="Extract audio from video as AAC",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Extract to WAV",
        category="extract",
        extension=".wav",
        ffmpeg_args=["-vn", "-c:a", "pcm_s16le"],
        description="Extract audio from video as uncompressed WAV",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Extract to FLAC",
        category="extract",
        extension=".flac",
        ffmpeg_args=["-vn", "-c:a", "flac"],
        description="Extract audio from video as lossless FLAC",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
]

# Resize/compress recipes
RESIZE_RECIPES = [
    Recipe(
        name="1080p (Full HD)",
        category="resize",
        extension=".mp4",
        ffmpeg_args=["-vf", "scale=-2:1080", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "128k"],
        description="Scale to 1080p height, maintain aspect ratio",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="720p (HD)",
        category="resize",
        extension=".mp4",
        ffmpeg_args=["-vf", "scale=-2:720", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "128k"],
        description="Scale to 720p height, maintain aspect ratio",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="480p (SD)",
        category="resize",
        extension=".mp4",
        ffmpeg_args=["-vf", "scale=-2:480", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "96k"],
        description="Scale to 480p height, maintain aspect ratio",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="360p (Low)",
        category="resize",
        extension=".mp4",
        ffmpeg_args=["-vf", "scale=-2:360", "-c:v", "libx264", "-preset", "medium", "-crf", "25", "-c:a", "aac", "-b:a", "64k"],
        description="Scale to 360p height, maintain aspect ratio",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Compress (High Quality)",
        category="resize",
        extension=".mp4",
        ffmpeg_args=["-c:v", "libx264", "-preset", "slow", "-crf", "20", "-c:a", "aac", "-b:a", "128k"],
        description="Reduce file size with minimal quality loss",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Compress (Medium Quality)",
        category="resize",
        extension=".mp4",
        ffmpeg_args=["-c:v", "libx264", "-preset", "medium", "-crf", "26", "-c:a", "aac", "-b:a", "96k"],
        description="Balance between file size and quality",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Compress (Small File)",
        category="resize",
        extension=".mp4",
        ffmpeg_args=["-c:v", "libx264", "-preset", "medium", "-crf", "32", "-c:a", "aac", "-b:a", "64k"],
        description="Maximum compression, noticeable quality loss",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
]

# YouTube-optimized recipes
YOUTUBE_RECIPES = [
    Recipe(
        name="YouTube 4K (2160p)",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=-2:2160",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-profile:v", "high", "-level", "5.1",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "384k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Best quality for 4K YouTube uploads",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="YouTube 1080p (Full HD)",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=-2:1080",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "384k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Standard HD for most YouTube uploads",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="YouTube 720p (HD)",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=-2:720",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.0",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Good quality with faster upload times",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="YouTube 480p (SD)",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=-2:480",
            "-c:v", "libx264", "-preset", "medium", "-crf", "22",
            "-profile:v", "main", "-level", "3.1",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Low bandwidth option for slower connections",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="YouTube Shorts (1080x1920)",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Vertical 9:16 format for YouTube Shorts (Full HD)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="YouTube Shorts (720x1280)",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "medium", "-crf", "22",
            "-profile:v", "high", "-level", "4.0",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Vertical 9:16 format for YouTube Shorts (smaller)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="YouTube High Quality",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-c:v", "libx264", "-preset", "slow", "-crf", "17",
            "-profile:v", "high", "-level", "5.1",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "384k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Maximum quality, keeps original resolution (slower encode)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="YouTube Fast Upload",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-profile:v", "high",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Balanced quality for quick encoding and upload",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
    Recipe(
        name="YouTube Small File",
        category="youtube",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=-2:720",
            "-c:v", "libx264", "-preset", "medium", "-crf", "26",
            "-profile:v", "main",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Minimize file size for limited bandwidth",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"]
    ),
]

# Remux recipes (no re-encode)
REMUX_RECIPES = [
    Recipe(
        name="Remux to MP4",
        category="remux",
        extension=".mp4",
        ffmpeg_args=["-c", "copy"],
        description="Change container to MP4 without re-encoding",
        input_extensions=[".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Remux to MKV",
        category="remux",
        extension=".mkv",
        ffmpeg_args=["-c", "copy"],
        description="Change container to MKV without re-encoding",
        input_extensions=[".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Remux to MOV",
        category="remux",
        extension=".mov",
        ffmpeg_args=["-c", "copy"],
        description="Change container to MOV without re-encoding",
        input_extensions=[".mp4", ".mkv", ".avi", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Remux to WebM",
        category="remux",
        extension=".webm",
        ffmpeg_args=["-c", "copy"],
        description="Change container to WebM without re-encoding (VP8/VP9 only)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov"]
    ),
]

# Short-form content recipes (vertical video for social media)
SHORTFORM_RECIPES = [
    # === Vertical Video Presets ===
    Recipe(
        name="TikTok/Reels (1080x1920)",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Full HD vertical 9:16 for TikTok and Instagram Reels",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        max_duration_seconds=600,
        max_file_size_mb=287
    ),
    Recipe(
        name="YouTube Shorts (720x1280)",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "22",
            "-profile:v", "high", "-level", "4.0",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="720p vertical for YouTube Shorts (max 60 sec)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        max_duration_seconds=60
    ),
    Recipe(
        name="Instagram/Facebook Stories (1080x1920)",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "22",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-movflags", "+faststart"
        ],
        description="Optimized for Instagram and Facebook Stories",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        max_duration_seconds=60
    ),
    Recipe(
        name="Vertical Compressed (Quick Draft)",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "fast", "-crf", "28",
            "-profile:v", "main",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "96k", "-ar", "44100",
            "-movflags", "+faststart"
        ],
        description="Fast encode, smaller file for drafts and previews",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    # === Repurpose Horizontal to Vertical ===
    Recipe(
        name="Center Crop (16:9 to 9:16)",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "crop=ih*9/16:ih,scale=1080:1920,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Crop center of horizontal video to vertical",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Letterbox with Black Bars",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:-2,pad=1080:1920:0:(oh-ih)/2:black,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Fit horizontal video in vertical frame with black bars",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Blur Background Fill",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-filter_complex",
            "[0:v]split[bg][fg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5,setsar=1[blurred];"
            "[fg]scale=1080:-2[scaled];"
            "[blurred][scaled]overlay=(W-w)/2:(H-h)/2[outv]",
            "-map", "[outv]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Blurred background fill (popular social media effect)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    Recipe(
        name="Split Screen Vertical (Top/Bottom)",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-filter_complex",
            "[0:v]split[top][bottom];"
            "[top]crop=iw:ih/2:0:0,scale=1080:960[t];"
            "[bottom]crop=iw:ih/2:0:ih/2,scale=1080:960[b];"
            "[t][b]vstack[outv]",
            "-map", "[outv]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Split video into top/bottom vertical stack",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]
    ),
    # === Platform-Specific Exports ===
    Recipe(
        name="TikTok Export (optimized)",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart",
            "-fs", "287M"
        ],
        description="TikTok optimized (max 10 min, 287MB limit)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        max_duration_seconds=600,
        max_file_size_mb=287
    ),
    Recipe(
        name="Instagram Reels Export",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Instagram Reels optimized (max 90 sec)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        max_duration_seconds=90
    ),
    Recipe(
        name="YouTube Shorts Export",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="YouTube Shorts optimized (max 60 sec, high quality)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        max_duration_seconds=60
    ),
    Recipe(
        name="Snapchat Spotlight",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "22",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Snapchat Spotlight optimized (max 60 sec)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        max_duration_seconds=60
    ),
    Recipe(
        name="Facebook Reels",
        category="shortform",
        extension=".mp4",
        ffmpeg_args=[
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart"
        ],
        description="Facebook Reels optimized (max 90 sec)",
        input_extensions=[".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        max_duration_seconds=90
    ),
]


# All built-in recipes
BUILTIN_RECIPES = {
    "video": VIDEO_RECIPES,
    "audio": AUDIO_RECIPES,
    "extract": EXTRACT_RECIPES,
    "resize": RESIZE_RECIPES,
    "remux": REMUX_RECIPES,
    "youtube": YOUTUBE_RECIPES,
    "shortform": SHORTFORM_RECIPES,
}


def get_recipes_by_category(category: str) -> list[Recipe]:
    """Get all recipes for a specific category."""
    return BUILTIN_RECIPES.get(category, [])


def get_all_recipes() -> dict[str, list[Recipe]]:
    """Get all built-in recipes organized by category."""
    return BUILTIN_RECIPES.copy()


def load_custom_recipes(recipes_file: Path) -> list[Recipe]:
    """Load custom recipes from a JSON file."""
    if not recipes_file.exists():
        return []

    try:
        with open(recipes_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Recipe.from_dict(r) for r in data]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def save_custom_recipes(recipes: list[Recipe], recipes_file: Path) -> bool:
    """Save custom recipes to a JSON file."""
    try:
        data = [r.to_dict() for r in recipes]
        with open(recipes_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def get_input_extensions_for_category(category: str) -> list[str]:
    """Get all valid input extensions for a category."""
    recipes = get_recipes_by_category(category)
    extensions = set()
    for recipe in recipes:
        extensions.update(recipe.input_extensions)
    return sorted(extensions)
