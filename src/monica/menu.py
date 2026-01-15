"""Interactive menu system for MONICA."""

from pathlib import Path
import questionary
from colorama import Fore, Style

from monica.recipes import (
    Recipe,
    get_recipes_by_category,
    get_input_extensions_for_category
)
from monica.file_selector import select_files, display_selected_files
from monica.executor import execute_jobs
from monica.ffmpeg_manager import print_ffmpeg_status


# Main menu options
MAIN_MENU_OPTIONS = [
    ("Convert video", "video"),
    ("Convert audio", "audio"),
    ("Extract audio", "extract"),
    ("Resize / compress", "resize"),
    ("Remux (no re-encode)", "remux"),
    ("YouTube", "youtube"),
    ("Short-form content", "shortform"),
    ("Logs / status", "status"),
    ("Help", "help"),
    ("Exit", "exit"),
]


# Help menu content
HELP_TOPICS = {
    "about": {
        "title": "About MONICA",
        "content": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                        ABOUT MONICA                               ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.WHITE}MONICA{Style.RESET_ALL} - {Fore.YELLOW}M{Style.RESET_ALL}edia {Fore.YELLOW}O{Style.RESET_ALL}perations {Fore.YELLOW}N{Style.RESET_ALL}avigator with {Fore.YELLOW}I{Style.RESET_ALL}nteractive {Fore.YELLOW}C{Style.RESET_ALL}ommand-line {Fore.YELLOW}A{Style.RESET_ALL}ssistance

{Fore.CYAN}What is MONICA?{Style.RESET_ALL}
MONICA is a friendly wrapper around FFmpeg that makes media conversion
accessible to everyone. No need to memorize complex command-line syntax
or understand codec parameters - just pick what you want and go!

{Fore.CYAN}How It Works:{Style.RESET_ALL}
1. {Fore.GREEN}You place files{Style.RESET_ALL} in the /import folder
2. {Fore.GREEN}You select an operation{Style.RESET_ALL} from the menu (convert, resize, etc.)
3. {Fore.GREEN}You choose a preset{Style.RESET_ALL} that matches your needs
4. {Fore.GREEN}MONICA builds the FFmpeg command{Style.RESET_ALL} automatically
5. {Fore.GREEN}Your converted files{Style.RESET_ALL} appear in /export

{Fore.CYAN}Why It Works:{Style.RESET_ALL}
MONICA uses a "recipe" system - pre-configured FFmpeg commands that have
been tested and optimized for common use cases. Each recipe knows:
  - Which codec to use
  - What quality settings work best
  - How to balance file size vs quality
  - Which containers are compatible

{Fore.CYAN}The Magic Behind the Scenes:{Style.RESET_ALL}
When you select "MP4 (H.264)", MONICA translates that to:
  {Fore.YELLOW}ffmpeg -i input.avi -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k output.mp4{Style.RESET_ALL}

You don't need to know any of that - MONICA handles it all!
"""
    },
    "menu_guide": {
        "title": "Menu Guide",
        "content": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                         MENU GUIDE                                ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}Convert Video{Style.RESET_ALL}
  Re-encodes video files to different formats. Use this when you need
  to change the video codec or make files compatible with specific devices.
  {Fore.YELLOW}Best for:{Style.RESET_ALL} Format compatibility, reducing file size, device playback

{Fore.GREEN}Convert Audio{Style.RESET_ALL}
  Converts audio files between formats like MP3, FLAC, WAV, etc.
  {Fore.YELLOW}Best for:{Style.RESET_ALL} Music libraries, podcast editing, format standardization

{Fore.GREEN}Extract Audio{Style.RESET_ALL}
  Pulls the audio track out of video files. The video is discarded,
  and you get just the sound.
  {Fore.YELLOW}Best for:{Style.RESET_ALL} Music from videos, podcast audio, voice recordings

{Fore.GREEN}Resize / Compress{Style.RESET_ALL}
  Reduces video resolution (1080p, 720p, etc.) or compresses to
  reduce file size while keeping the same resolution.
  {Fore.YELLOW}Best for:{Style.RESET_ALL} Saving storage, sharing online, mobile devices

{Fore.GREEN}Remux (No Re-encode){Style.RESET_ALL}
  Changes the container format WITHOUT re-encoding. This is instant
  and completely lossless - the video/audio data stays identical.
  {Fore.YELLOW}Best for:{Style.RESET_ALL} MKV to MP4 for Apple devices, quick format fixes

{Fore.GREEN}Logs / Status{Style.RESET_ALL}
  View FFmpeg status, check logs, and see what MONICA has been doing.
  Useful for troubleshooting if something goes wrong.

{Fore.GREEN}Help{Style.RESET_ALL}
  You're here! Learn about MONICA, formats, and how everything works.
"""
    },
    "video_formats": {
        "title": "Video Formats Explained",
        "content": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                    VIDEO FORMATS EXPLAINED                        ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}═══ CONTAINERS (File Extensions) ═══{Style.RESET_ALL}

{Fore.YELLOW}MP4 (.mp4){Style.RESET_ALL}
  The universal standard. Plays on virtually everything - phones,
  TVs, browsers, game consoles. Your safest choice for sharing.
  {Fore.CYAN}Compatibility:{Style.RESET_ALL} ★★★★★  {Fore.CYAN}Features:{Style.RESET_ALL} ★★★☆☆

{Fore.YELLOW}MKV (.mkv){Style.RESET_ALL}
  The "Swiss Army knife" of containers. Supports multiple audio
  tracks, subtitles, chapters, and almost any codec. Great for
  archiving movies with all their extras intact.
  {Fore.CYAN}Compatibility:{Style.RESET_ALL} ★★★☆☆  {Fore.CYAN}Features:{Style.RESET_ALL} ★★★★★

{Fore.YELLOW}WebM (.webm){Style.RESET_ALL}
  Designed for the web. Optimized for streaming and supported by
  all modern browsers. Open-source and royalty-free.
  {Fore.CYAN}Compatibility:{Style.RESET_ALL} ★★★★☆  {Fore.CYAN}Features:{Style.RESET_ALL} ★★★☆☆

{Fore.YELLOW}AVI (.avi){Style.RESET_ALL}
  The classic format from the Windows 95 era. Still works but
  lacks modern features. Use only for legacy compatibility.
  {Fore.CYAN}Compatibility:{Style.RESET_ALL} ★★★★☆  {Fore.CYAN}Features:{Style.RESET_ALL} ★☆☆☆☆

{Fore.YELLOW}MOV (.mov){Style.RESET_ALL}
  Apple's format. Excellent quality and great for Apple devices
  and professional editing software like Final Cut Pro.
  {Fore.CYAN}Compatibility:{Style.RESET_ALL} ★★★☆☆  {Fore.CYAN}Features:{Style.RESET_ALL} ★★★★☆

{Fore.GREEN}═══ CODECS (The Actual Compression) ═══{Style.RESET_ALL}

{Fore.YELLOW}H.264 (AVC){Style.RESET_ALL}
  The workhorse codec. Fast encoding, universal playback, good
  compression. If unsure, use H.264 - it just works everywhere.
  {Fore.CYAN}Quality:{Style.RESET_ALL} ★★★★☆  {Fore.CYAN}Speed:{Style.RESET_ALL} ★★★★☆  {Fore.CYAN}Size:{Style.RESET_ALL} ★★★☆☆

{Fore.YELLOW}H.265 (HEVC){Style.RESET_ALL}
  The successor to H.264. Same quality at half the file size!
  But slower to encode and some older devices can't play it.
  {Fore.CYAN}Quality:{Style.RESET_ALL} ★★★★★  {Fore.CYAN}Speed:{Style.RESET_ALL} ★★☆☆☆  {Fore.CYAN}Size:{Style.RESET_ALL} ★★★★★

{Fore.YELLOW}VP9{Style.RESET_ALL}
  Google's answer to H.265. Open-source, royalty-free. Used by
  YouTube for 4K videos. Great for web streaming.
  {Fore.CYAN}Quality:{Style.RESET_ALL} ★★★★★  {Fore.CYAN}Speed:{Style.RESET_ALL} ★★☆☆☆  {Fore.CYAN}Size:{Style.RESET_ALL} ★★★★☆

{Fore.YELLOW}MPEG-4{Style.RESET_ALL}
  Older codec, predecessor to H.264. Larger files but very
  compatible. Good for older devices and DVD players.
  {Fore.CYAN}Quality:{Style.RESET_ALL} ★★★☆☆  {Fore.CYAN}Speed:{Style.RESET_ALL} ★★★★★  {Fore.CYAN}Size:{Style.RESET_ALL} ★★☆☆☆

{Fore.GREEN}═══ QUICK RECOMMENDATIONS ═══{Style.RESET_ALL}

  {Fore.CYAN}For sharing online:{Style.RESET_ALL}     MP4 + H.264
  {Fore.CYAN}For saving space:{Style.RESET_ALL}       MP4 + H.265
  {Fore.CYAN}For archiving:{Style.RESET_ALL}          MKV + H.264
  {Fore.CYAN}For web streaming:{Style.RESET_ALL}     WebM + VP9
  {Fore.CYAN}For Apple devices:{Style.RESET_ALL}     MP4 + H.264 or MOV
"""
    },
    "audio_formats": {
        "title": "Audio Formats Explained",
        "content": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                    AUDIO FORMATS EXPLAINED                        ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}═══ LOSSY FORMATS (Smaller Files) ═══{Style.RESET_ALL}

{Fore.YELLOW}MP3 (.mp3){Style.RESET_ALL}
  The king of audio formats. Every device on Earth plays MP3.
  At 320kbps, most people can't tell it from the original.

  {Fore.CYAN}320 kbps:{Style.RESET_ALL} Near-CD quality, ~2.4 MB per minute
  {Fore.CYAN}192 kbps:{Style.RESET_ALL} Great for most listeners, ~1.4 MB per minute
  {Fore.CYAN}128 kbps:{Style.RESET_ALL} Acceptable quality, ~1 MB per minute

  {Fore.GREEN}Best for:{Style.RESET_ALL} Music libraries, podcasts, universal sharing

{Fore.YELLOW}AAC (.m4a){Style.RESET_ALL}
  Apple's preferred format. Better quality than MP3 at the same
  bitrate. Used by iTunes, YouTube, and streaming services.

  {Fore.GREEN}Best for:{Style.RESET_ALL} Apple devices, modern players, streaming

{Fore.YELLOW}OGG Vorbis (.ogg){Style.RESET_ALL}
  Open-source and royalty-free. Excellent quality, but less
  compatible than MP3. Popular in games and Linux.

  {Fore.GREEN}Best for:{Style.RESET_ALL} Game development, open-source projects

{Fore.YELLOW}Opus (.opus){Style.RESET_ALL}
  The newest and most efficient codec. Beats everything at low
  bitrates. Used by WhatsApp, Discord, and WebRTC.

  {Fore.GREEN}Best for:{Style.RESET_ALL} Voice calls, streaming, low-bandwidth situations

{Fore.GREEN}═══ LOSSLESS FORMATS (Perfect Quality) ═══{Style.RESET_ALL}

{Fore.YELLOW}FLAC (.flac){Style.RESET_ALL}
  Lossless compression - bit-for-bit identical to the original,
  but ~50-60% of the size. The audiophile's choice.

  {Fore.CYAN}Size:{Style.RESET_ALL} ~25-35 MB per minute (varies by content)
  {Fore.GREEN}Best for:{Style.RESET_ALL} Music archival, audiophiles, source files

{Fore.YELLOW}WAV (.wav){Style.RESET_ALL}
  Completely uncompressed audio. Maximum quality, maximum size.
  Used in professional audio production and editing.

  {Fore.CYAN}Size:{Style.RESET_ALL} ~10 MB per minute (CD quality)
  {Fore.GREEN}Best for:{Style.RESET_ALL} Audio editing, professional production

{Fore.GREEN}═══ QUALITY COMPARISON ═══{Style.RESET_ALL}

  Format          Quality    File Size    Compatibility
  ──────────────────────────────────────────────────────
  WAV             ★★★★★      ★☆☆☆☆       ★★★★★
  FLAC            ★★★★★      ★★★☆☆       ★★★☆☆
  MP3 320k        ★★★★☆      ★★★★☆       ★★★★★
  AAC 256k        ★★★★☆      ★★★★☆       ★★★★☆
  Opus 128k       ★★★★☆      ★★★★★       ★★★☆☆
  MP3 128k        ★★★☆☆      ★★★★★       ★★★★★

{Fore.GREEN}═══ QUICK RECOMMENDATIONS ═══{Style.RESET_ALL}

  {Fore.CYAN}For music collection:{Style.RESET_ALL}   MP3 320kbps or FLAC
  {Fore.CYAN}For podcasts:{Style.RESET_ALL}           MP3 192kbps
  {Fore.CYAN}For archiving:{Style.RESET_ALL}          FLAC
  {Fore.CYAN}For editing:{Style.RESET_ALL}            WAV
  {Fore.CYAN}For Apple devices:{Style.RESET_ALL}      AAC
  {Fore.CYAN}For maximum compression:{Style.RESET_ALL} Opus
"""
    },
    "ffmpeg_tribute": {
        "title": "Dedication to FFmpeg",
        "content": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                    A TRIBUTE TO FFMPEG                            ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}
                    ███████╗███████╗███╗   ███╗██████╗ ███████╗ ██████╗
                    ██╔════╝██╔════╝████╗ ████║██╔══██╗██╔════╝██╔════╝
                    █████╗  █████╗  ██╔████╔██║██████╔╝█████╗  ██║  ███╗
                    ██╔══╝  ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██╔══╝  ██║   ██║
                    ██║     ██║     ██║ ╚═╝ ██║██║     ███████╗╚██████╔╝
                    ╚═╝     ╚═╝     ╚═╝     ╚═╝╚═╝     ╚══════╝ ╚═════╝
{Style.RESET_ALL}

{Fore.CYAN}The Unsung Hero of Digital Media{Style.RESET_ALL}

Every time you watch a YouTube video, stream on Netflix, make a video
call, or play a game - there's a good chance FFmpeg is involved somehow.

{Fore.GREEN}Started in 2000{Style.RESET_ALL} by Fabrice Bellard, FFmpeg has grown into the most
important open-source multimedia project in existence. It's the Swiss
Army knife that powers:

  {Fore.YELLOW}•{Style.RESET_ALL} YouTube, Vimeo, and almost every video platform
  {Fore.YELLOW}•{Style.RESET_ALL} VLC, Chrome, Firefox, and countless media players
  {Fore.YELLOW}•{Style.RESET_ALL} OBS, HandBrake, and professional editing tools
  {Fore.YELLOW}•{Style.RESET_ALL} Discord, WhatsApp, and communication apps
  {Fore.YELLOW}•{Style.RESET_ALL} Video games, streaming services, security cameras

{Fore.CYAN}The Numbers Are Staggering:{Style.RESET_ALL}

  {Fore.GREEN}•{Style.RESET_ALL} 20+ years of continuous development
  {Fore.GREEN}•{Style.RESET_ALL} 1,000+ contributors from around the world
  {Fore.GREEN}•{Style.RESET_ALL} Supports virtually every audio/video format ever created
  {Fore.GREEN}•{Style.RESET_ALL} Billions of devices run FFmpeg code
  {Fore.GREEN}•{Style.RESET_ALL} 100% free and open source (LGPL/GPL)

{Fore.CYAN}Why This Matters:{Style.RESET_ALL}

Without FFmpeg, the multimedia landscape would be fragmented, expensive,
and inaccessible. The FFmpeg team has given the world a gift - the ability
to work with any media format, on any platform, completely free.

{Fore.YELLOW}MONICA exists because FFmpeg exists.{Style.RESET_ALL}

We're just a friendly interface. The real magic happens in FFmpeg's
millions of lines of carefully optimized code, written by brilliant
engineers who believe in open source.

{Fore.CYAN}Thank You:{Style.RESET_ALL}

  To Fabrice Bellard, for creating FFmpeg
  To Michael Niedermayer, for years of leadership
  To the entire FFmpeg team, past and present
  To every contributor who fixed a bug or added a feature

{Fore.GREEN}Your work makes the digital world possible.{Style.RESET_ALL}

{Fore.CYAN}────────────────────────────────────────────────────────────────────{Style.RESET_ALL}
  Learn more: {Fore.YELLOW}https://ffmpeg.org{Style.RESET_ALL}
  Donate: {Fore.YELLOW}https://ffmpeg.org/donations.html{Style.RESET_ALL}
{Fore.CYAN}────────────────────────────────────────────────────────────────────{Style.RESET_ALL}
"""
    },
    "shortform": {
        "title": "Short-form Content",
        "content": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                    SHORT-FORM CONTENT                             ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}═══ VERTICAL VIDEO PRESETS ═══{Style.RESET_ALL}

{Fore.YELLOW}TikTok/Reels (1080x1920){Style.RESET_ALL}
  Full HD vertical format. Works for TikTok, Instagram Reels,
  and most social platforms. Max 10 minutes for TikTok.

{Fore.YELLOW}YouTube Shorts (720x1280){Style.RESET_ALL}
  Optimized for YouTube Shorts. 720p saves bandwidth while
  maintaining quality. Max 60 seconds.

{Fore.YELLOW}Instagram/Facebook Stories{Style.RESET_ALL}
  Optimized encoding for Stories format. Max 60 seconds.

{Fore.YELLOW}Vertical Compressed (Quick Draft){Style.RESET_ALL}
  Fast encoding for previews and drafts. Smaller file size.

{Fore.GREEN}═══ REPURPOSE HORIZONTAL TO VERTICAL ═══{Style.RESET_ALL}

{Fore.YELLOW}Center Crop (16:9 to 9:16){Style.RESET_ALL}
  Crops the center of your horizontal video to fill vertical
  frame. Best when the subject is centered in frame.

{Fore.YELLOW}Letterbox with Black Bars{Style.RESET_ALL}
  Fits your entire video with black bars top and bottom.
  Preserves full content but has empty space.

{Fore.YELLOW}Blur Background Fill{Style.RESET_ALL}
  The popular "blurred background" effect! Shows your video
  centered with a blurred, zoomed version behind it.

{Fore.YELLOW}Split Screen Vertical{Style.RESET_ALL}
  Splits your video into top/bottom halves stacked vertically.
  Great for comparisons or before/after content.

{Fore.GREEN}═══ PLATFORM LIMITS ═══{Style.RESET_ALL}

  Platform            Duration    File Size
  ─────────────────────────────────────────────
  TikTok              10 min      287 MB
  Instagram Reels     90 sec      4 GB
  YouTube Shorts      60 sec      -
  Snapchat Spotlight  60 sec      -
  Facebook Reels      90 sec      4 GB
"""
    },
    "tips": {
        "title": "Tips & Tricks",
        "content": f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                       TIPS & TRICKS                               ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}═══ SPEED TIPS ═══{Style.RESET_ALL}

{Fore.YELLOW}Use Remux When Possible{Style.RESET_ALL}
  If you just need MKV → MP4 (or vice versa) and the codecs are
  compatible, use Remux! It's instant and lossless.

{Fore.YELLOW}H.264 is Faster Than H.265{Style.RESET_ALL}
  H.265 gives smaller files but takes 2-3x longer to encode.
  For quick jobs, stick with H.264.

{Fore.YELLOW}Batch Process Overnight{Style.RESET_ALL}
  Select multiple files at once and let MONICA work while you sleep!

{Fore.GREEN}═══ QUALITY TIPS ═══{Style.RESET_ALL}

{Fore.YELLOW}Don't Upscale{Style.RESET_ALL}
  Converting 720p to 1080p doesn't add quality - it just makes
  the file bigger. Always scale down, never up.

{Fore.YELLOW}Avoid Multiple Conversions{Style.RESET_ALL}
  Each lossy conversion loses quality. Go from source → final
  in one step when possible.

{Fore.YELLOW}Keep Originals{Style.RESET_ALL}
  Always keep your source files until you've verified the
  conversion looks good.

{Fore.GREEN}═══ SPACE-SAVING TIPS ═══{Style.RESET_ALL}

{Fore.YELLOW}720p is Usually Enough{Style.RESET_ALL}
  For most content viewed on phones or laptops, 720p looks
  great and is half the size of 1080p.

{Fore.YELLOW}H.265 for Archives{Style.RESET_ALL}
  If you're archiving videos long-term, H.265 saves ~50% space
  with identical quality. Worth the extra encoding time.

{Fore.YELLOW}Audio Matters Less Than You Think{Style.RESET_ALL}
  128kbps AAC is fine for most video. Going to 320kbps doubles
  the audio size for minimal audible improvement.

{Fore.GREEN}═══ TROUBLESHOOTING ═══{Style.RESET_ALL}

{Fore.YELLOW}File Won't Play?{Style.RESET_ALL}
  Try remuxing to MP4 first. If that doesn't work, convert
  to MP4 H.264 - it plays on everything.

{Fore.YELLOW}Audio Out of Sync?{Style.RESET_ALL}
  This usually means the source file has issues. Try remuxing
  first, then converting if needed.

{Fore.YELLOW}Conversion Fails?{Style.RESET_ALL}
  Check the logs (Logs / Status menu). The error message
  usually tells you what went wrong.

{Fore.YELLOW}File Too Large?{Style.RESET_ALL}
  Use Resize/Compress with "Compress (Medium)" or lower the
  resolution to 720p.
"""
    },
}


def display_banner() -> None:
    """Display the MONICA banner."""
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════╗
║  {Fore.WHITE}MONICA{Fore.CYAN} - FFmpeg Interactive CLI Tool    ║
╚══════════════════════════════════════════╝{Style.RESET_ALL}
""")


def select_recipe(category: str) -> Recipe | None:
    """Display recipe selection menu for a category.

    Args:
        category: The recipe category

    Returns:
        Selected recipe or None if cancelled
    """
    recipes = get_recipes_by_category(category)

    if not recipes:
        print(f"\n{Fore.YELLOW}No recipes available for this category.{Style.RESET_ALL}")
        return None

    choices = []
    for recipe in recipes:
        title = f"{recipe.name}"
        if recipe.description:
            title += f" - {recipe.description}"
        choices.append(questionary.Choice(title=title, value=recipe))

    choices.append(questionary.Choice(title="<- Back to main menu", value=None))

    print()  # Add spacing
    selected = questionary.select(
        "Select a preset:",
        choices=choices,
        use_shortcuts=False,
        use_indicator=True
    ).ask()

    return selected


def handle_conversion(
    category: str,
    ffmpeg_path: str,
    import_dir: Path,
    export_dir: Path
) -> None:
    """Handle a conversion workflow.

    Args:
        category: The recipe category
        ffmpeg_path: Path to FFmpeg
        import_dir: Import directory
        export_dir: Export directory
    """
    # Select recipe
    recipe = select_recipe(category)
    if recipe is None:
        return

    # Get valid extensions for this category
    extensions = get_input_extensions_for_category(category)

    # Select files
    files = select_files(import_dir, extensions)
    if not files:
        return

    display_selected_files(files)

    # Confirm
    print()
    if not questionary.confirm("Start processing?", default=True).ask():
        print(f"{Fore.YELLOW}Cancelled.{Style.RESET_ALL}")
        return

    # Execute
    execute_jobs(ffmpeg_path, files, recipe, export_dir)

    # Pause before returning to menu
    print()
    questionary.press_any_key_to_continue("Press any key to continue...").ask()


def handle_status(base_dir: Path, logs_dir: Path) -> None:
    """Display status information and log viewer.

    Args:
        base_dir: Base project directory
        logs_dir: Logs directory
    """
    print(f"\n{Fore.CYAN}=== Status ==={Style.RESET_ALL}\n")

    # FFmpeg status
    print_ffmpeg_status(base_dir)

    # Log file info
    log_file = logs_dir / "monica.log"
    if log_file.exists():
        size = log_file.stat().st_size
        size_kb = size / 1024
        print(f"Log file: {Fore.GREEN}{size_kb:.1f} KB{Style.RESET_ALL}")

        # Offer to view logs
        print()
        view_choice = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("View recent logs (last 20 lines)", "view"),
                questionary.Choice("Clear log file", "clear"),
                questionary.Choice("<- Back to main menu", "back"),
            ]
        ).ask()

        if view_choice == "view":
            print(f"\n{Fore.CYAN}=== Recent Logs ==={Style.RESET_ALL}\n")
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"{Fore.RED}Error reading log: {e}{Style.RESET_ALL}")

            print()
            questionary.press_any_key_to_continue("Press any key to continue...").ask()

        elif view_choice == "clear":
            if questionary.confirm("Are you sure you want to clear the log file?", default=False).ask():
                try:
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write("")
                    print(f"{Fore.GREEN}Log file cleared.{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error clearing log: {e}{Style.RESET_ALL}")
    else:
        print(f"Log file: {Fore.YELLOW}Not created yet{Style.RESET_ALL}")

    print()


def handle_help() -> None:
    """Display help menu with submenus for different topics."""
    while True:
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════╗")
        print(f"║              {Fore.WHITE}HELP CENTER{Fore.CYAN}                  ║")
        print(f"╚══════════════════════════════════════════╝{Style.RESET_ALL}\n")

        choices = [
            questionary.Choice("About MONICA - What is this and how does it work?", "about"),
            questionary.Choice("Menu Guide - What does each option do?", "menu_guide"),
            questionary.Choice("Video Formats - Containers, codecs, and recommendations", "video_formats"),
            questionary.Choice("Audio Formats - MP3, FLAC, AAC and more explained", "audio_formats"),
            questionary.Choice("Short-form Content - TikTok, Reels, Shorts, and vertical video", "shortform"),
            questionary.Choice("Tips & Tricks - Get the most out of MONICA", "tips"),
            questionary.Choice("Dedication to FFmpeg - The heroes behind the magic", "ffmpeg_tribute"),
            questionary.Choice("<- Back to main menu", "back"),
        ]

        choice = questionary.select(
            "What would you like to learn about?",
            choices=choices,
            use_shortcuts=False,
            use_indicator=True
        ).ask()

        if choice is None or choice == "back":
            break

        topic = HELP_TOPICS.get(choice)
        if topic:
            print(topic["content"])
            print()
            questionary.press_any_key_to_continue("Press any key to continue...").ask()


def run_menu_loop(
    ffmpeg_path: str,
    base_dir: Path,
    import_dir: Path,
    export_dir: Path,
    logs_dir: Path
) -> None:
    """Run the main menu loop.

    Args:
        ffmpeg_path: Path to FFmpeg executable
        base_dir: Base project directory
        import_dir: Import directory
        export_dir: Export directory
        logs_dir: Logs directory
    """
    while True:
        display_banner()

        # Build menu choices
        choices = [
            questionary.Choice(title=name, value=action)
            for name, action in MAIN_MENU_OPTIONS
        ]

        action = questionary.select(
            "Main Menu:",
            choices=choices,
            use_shortcuts=False,
            use_indicator=True
        ).ask()

        if action is None or action == "exit":
            print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}\n")
            break

        elif action == "status":
            handle_status(base_dir, logs_dir)

        elif action == "help":
            handle_help()

        elif action in ("video", "audio", "extract", "resize", "remux", "youtube", "shortform"):
            handle_conversion(action, ffmpeg_path, import_dir, export_dir)

        else:
            print(f"{Fore.YELLOW}Unknown action.{Style.RESET_ALL}")
