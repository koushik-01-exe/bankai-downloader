#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BANKAI DOWNLOADER — YouTube Video Downloader CLI Tool
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Author  : Kouxik
  Version : 1.0.0
  Backend : yt-dlp

  INSTALL (Termux):
    pkg install python ffmpeg
    pip install -r requirements.txt
    python bankai_downloader.py

  INSTALL (Linux/Mac):
    pip install -r requirements.txt
    python bankai_downloader.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import re
import sys
import time
import subprocess
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    TaskProgressColumn,
)
from rich.live import Live
from rich.align import Align
from rich.rule import Rule
import pyfiglet

console = Console()

# ─── Color constants ───────────────────────────────────────
CYAN = "bold cyan"
MAGENTA = "bold magenta"
GREEN = "bold green"
RED = "bold red"
YELLOW = "bold yellow"
DIM = "dim"

_ANDROID_DIR = "/storage/emulated/0/Download/BankaiDownloader"
_DEFAULT_FALLBACK = os.path.expanduser("~/Downloads/BankaiDownloader")

def _resolve_download_dir():
    """Use Android storage if writable, otherwise fall back to home dir."""
    try:
        os.makedirs(_ANDROID_DIR, exist_ok=True)
        return _ANDROID_DIR
    except PermissionError:
        return _DEFAULT_FALLBACK
    except OSError:
        return _DEFAULT_FALLBACK

DEFAULT_DOWNLOAD_DIR = _resolve_download_dir()
VERSION = "1.0.0"
AUTHOR = "Kouxik"


def has_ffmpeg():
    """Check if ffmpeg is available on the system."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        return False


def prompt(text, default=""):
    """Styled input prompt that renders Rich markup. Handles EOF gracefully."""
    try:
        return console.input(text).strip()
    except EOFError:
        console.print()
        return default


def safe_exit():
    """Graceful exit on EOF or interrupt."""
    console.print(f"\n\n  [{GREEN}]✓ Goodbye![/{GREEN}]\n")
    sys.exit(0)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ANIMATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def typewriter(text, delay=0.03, style=None):
    """Print text one character at a time."""
    for char in text:
        if style:
            console.print(char, end="", style=style, highlight=False)
        else:
            console.print(char, end="", highlight=False)
        sys.stdout.flush()
        time.sleep(delay)
    console.print()


def show_opening_animation():
    """Animated opening sequence with ASCII art banner."""
    os.system("clear" if os.name != "nt" else "cls")

    # Generate banner with pyfiglet
    banner = pyfiglet.figlet_format("BANKAI", font="slant")
    banner_lines = banner.rstrip("\n").split("\n")
    subtitle = "D O W N L O A D E R"

    console.print()
    for line in banner_lines:
        for char in line:
            console.print(char, end="", style=CYAN, highlight=False)
            sys.stdout.flush()
            time.sleep(0.004)
        console.print()
        time.sleep(0.05)

    # Subtitle typewriter
    console.print()
    padding = " " * ((40 - len(subtitle)) // 2)
    console.print(padding, end="")
    typewriter(subtitle, delay=0.06, style=MAGENTA)
    console.print()

    # Info panel
    info_text = Text()
    info_text.append("  Version  ", style=DIM)
    info_text.append(f"v{VERSION}\n", style=CYAN)
    info_text.append("  Author   ", style=DIM)
    info_text.append(f"{AUTHOR}\n", style=MAGENTA)
    info_text.append("  Join     ", style=DIM)
    info_text.append("https://t.me/BankaiMods\n", style=CYAN)
    info_text.append("  Engine   ", style=DIM)
    info_text.append("Ready", style=GREEN)

    panel = Panel(
        info_text,
        title=f"[{CYAN}]⚡ BANKAI DOWNLOADER ⚡[/{CYAN}]",
        border_style=CYAN,
        box=__import__("rich.box", fromlist=["DOUBLE"]).DOUBLE,
        padding=(0, 2),
    )
    console.print(Align.center(panel))
    console.print()

    # Loading spinner
    with console.status(f"[{CYAN}]Initializing engine...[/{CYAN}]", spinner="dots"):
        time.sleep(1.5)

    if has_ffmpeg():
        console.print(f"  [{GREEN}]✓ Engine ready![/{GREEN}]")
    else:
        console.print(f"  [{YELLOW}]⚠ ffmpeg not found — downloads will use single-stream formats[/{YELLOW}]")
        console.print(f"  [{DIM}]  Install with: pkg install ffmpeg (Termux) or apt install ffmpeg (Linux)[/{DIM}]")
    console.print()
    console.print(Rule(style=CYAN))
    console.print()


def show_closing_animation(stats):
    """Animated closing sequence with download summary."""
    console.print()
    console.print(Rule(style=CYAN))

    with console.status(f"[{GREEN}]Finalizing...[/{GREEN}]", spinner="dots"):
        time.sleep(0.8)

    console.print(f"\n  [{GREEN}]✓  Download Complete![/{GREEN}]\n")

    # Summary box
    filename = stats.get("filename", "Unknown")
    size = stats.get("size", "Unknown")
    quality = stats.get("quality", "Unknown")
    elapsed = stats.get("elapsed", "0s")
    mode = stats.get("mode", "Video")

    summary = Text()
    summary.append("  📁 Filename  ", style=DIM)
    summary.append(f"{filename}\n", style=CYAN)
    summary.append("  📊 Size      ", style=DIM)
    summary.append(f"{size}\n", style=CYAN)
    summary.append("  🎬 Quality   ", style=DIM)
    summary.append(f"{quality}\n", style=MAGENTA)
    summary.append("  📦 Mode      ", style=DIM)
    summary.append(f"{mode}\n", style=MAGENTA)
    summary.append("  ⏱  Time      ", style=DIM)
    summary.append(f"{elapsed}\n", style=GREEN)

    panel = Panel(
        summary,
        title=f"[{GREEN}]Download Summary[/{GREEN}]",
        border_style=GREEN,
        box=__import__("rich.box", fromlist=["DOUBLE"]).DOUBLE,
        padding=(0, 2),
    )
    console.print(Align.center(panel))
    console.print()

    # Typewriter farewell
    farewell = "Thanks for using Bankai Downloader. Stay Legendary."
    console.print("  ", end="")
    typewriter(farewell, delay=0.04, style=MAGENTA)
    console.print()

    # Instant progress bar fill
    with Progress(
        TextColumn("  "),
        BarColumn(bar_width=40, style="dim", complete_style=GREEN, finished_style=GREEN),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("exit", total=100)
        for i in range(100):
            progress.update(task, advance=1)
            time.sleep(0.008)

    console.print(f"\n  [{GREEN}]✓ All done. Goodbye![/{GREEN}]\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORE FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def sanitize_filename(name):
    """Remove or replace characters unsafe for filenames."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"\s+", " ", name).strip()
    if len(name) > 200:
        name = name[:200]
    return name


def format_size(size_bytes):
    """Convert bytes to human-readable size string."""
    if size_bytes is None or size_bytes == 0:
        return "N/A"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_elapsed(seconds):
    """Convert seconds to human-readable elapsed time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def get_video_info(url):
    """Fetch video metadata using yt-dlp."""
    import yt_dlp

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return info
    except Exception as e:
        return None


def get_video_formats(url):
    """Fetch and parse available formats for a video."""
    import yt_dlp

    console.print(f"\n  [{CYAN}]Fetching available formats...[/{CYAN}]")
    with console.status(f"[{CYAN}]Contacting YouTube...[/{CYAN}]", spinner="dots"):
        info = get_video_info(url)

    if info is None:
        return None, None

    formats = []
    seen = set()

    for f in info.get("formats", []):
        height = f.get("height")
        fps = f.get("fps", 30)
        ext = f.get("ext", "unknown")
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        filesize = f.get("filesize") or f.get("filesize_approx")
        format_id = f.get("format_id", "")
        format_note = f.get("format_note", "")

        # Only video formats with resolution
        if height and vcodec != "none":
            key = f"{height}p-{ext}"
            if key not in seen:
                seen.add(key)
                has_audio = acodec != "none"
                formats.append({
                    "format_id": format_id,
                    "height": height,
                    "label": f"{height}p",
                    "fps": fps,
                    "ext": ext,
                    "filesize": filesize,
                    "filesize_str": format_size(filesize),
                    "has_audio": has_audio,
                    "format_note": format_note,
                })

    # Sort by resolution descending
    formats.sort(key=lambda x: x["height"], reverse=True)

    # Deduplicate keeping best per resolution+ext combo
    best = {}
    for f in formats:
        key = f"{f['height']}p-{f['ext']}"
        if key not in best or (f["filesize"] or 0) > (best[key]["filesize"] or 0):
            best[key] = f
    formats = sorted(best.values(), key=lambda x: x["height"], reverse=True)

    return info, formats


def show_quality_menu(info, formats):
    """Display interactive quality selection table."""
    title = info.get("title", "Unknown Video")
    duration = info.get("duration", 0)
    dur_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"

    console.print()
    console.print(Panel(
        f"  [{CYAN}]🎬 {title}[/{CYAN}]\n"
        f"  [{DIM}]Duration: {dur_str}[/{DIM}]",
        title=f"[{MAGENTA}]Video Info[/{MAGENTA}]",
        border_style=MAGENTA,
        padding=(0, 2),
    ))

    table = Table(
        title="Available Qualities",
        title_style=CYAN,
        border_style=CYAN,
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#", style=YELLOW, justify="center", width=4)
    table.add_column("Resolution", style=CYAN, justify="center")
    table.add_column("FPS", style=MAGENTA, justify="center")
    table.add_column("Format", style=CYAN, justify="center")
    table.add_column("Est. Size", style=GREEN, justify="center")
    table.add_column("Audio", style=YELLOW, justify="center")

    # Option 0: Best quality auto
    table.add_row(
        "0",
        "[bold green]Best Quality (Auto)[/bold green]",
        "—",
        "—",
        "—",
        "✓",
    )

    for i, f in enumerate(formats, 1):
        audio_str = "✓" if f["has_audio"] else "✗ (needs merge)"
        table.add_row(
            str(i),
            f["label"],
            str(f["fps"]),
            f["ext"],
            f["filesize_str"],
            audio_str,
        )

    console.print()
    console.print(table)
    console.print()

    while True:
        choice = prompt(f"  [{YELLOW}]Select quality [0-{len(formats)}] (0=Best): [/{YELLOW}]")
        if choice == "":
            choice = "0"
        try:
            idx = int(choice)
            if idx == 0:
                return "best"
            if 1 <= idx <= len(formats):
                return formats[idx - 1]
            console.print(f"  [{RED}]Invalid choice. Enter 0-{len(formats)}.[/{RED}]")
        except ValueError:
            console.print(f"  [{RED}]Enter a number.[/{RED}]")


def ensure_output_dir(path):
    """Create output directory if it doesn't exist."""
    try:
        os.makedirs(path, exist_ok=True)
    except PermissionError:
        fallback = os.path.expanduser("~/Downloads/BankaiDownloader")
        console.print(f"\n  [{YELLOW}]⚠ Storage permission not granted.[/{YELLOW}]")
        console.print(f"  [{DIM}]Run 'termux-setup-storage' to grant access.[/{DIM}]")
        console.print(f"  [{CYAN}]Using fallback: {fallback}[/{CYAN}]\n")
        os.makedirs(fallback, exist_ok=True)
        return fallback
    return path


def make_progress_hook():
    """Create a yt-dlp progress hook using Rich live display."""
    progress = Progress(
        TextColumn("  "),
        SpinnerColumn(style=CYAN),
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=30, style="dim", complete_style=CYAN, finished_style=GREEN),
        TaskProgressColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    )
    task_id = None
    result = {"filepath": None}

    def hook(d):
        nonlocal task_id
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            filename = os.path.basename(d.get("filename", "file"))
            result["filepath"] = d.get("filename")

            if len(filename) > 40:
                filename = filename[:37] + "..."

            if task_id is None:
                task_id = progress.add_task(filename, total=total or None)
            else:
                progress.update(task_id, completed=downloaded, total=total or None)

        elif d["status"] == "finished":
            result["filepath"] = d.get("filename")
            if task_id is not None:
                progress.update(task_id, description=f"[{GREEN}]✓ Done[/{GREEN}]")

    return progress, hook, result


class SilentLogger:
    """Suppress all yt-dlp output so only Rich progress bar shows."""
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        pass


def download_with_progress(ydl_opts, url):
    """Execute yt-dlp download with Rich progress display."""
    import yt_dlp

    progress, hook, result = make_progress_hook()

    ydl_opts["progress_hooks"] = [hook]
    ydl_opts["logger"] = SilentLogger()
    ydl_opts["noprogress"] = True

    with Live(progress, console=console, refresh_per_second=10):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    return result.get("filepath")


def download_video(url, format_choice, output_dir):
    """Download a video with selected quality."""
    import yt_dlp

    ensure_output_dir(output_dir)

    if format_choice == "best":
        if has_ffmpeg():
            format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        else:
            format_str = "best[ext=mp4]/best"
    else:
        fid = format_choice["format_id"]
        if format_choice["has_audio"]:
            format_str = fid
        elif has_ffmpeg():
            format_str = f"{fid}+bestaudio/best"
        else:
            format_str = f"best[ext=mp4]/best"

    ydl_opts = {
        "format": format_str,
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }

    console.print(f"\n  [{CYAN}]Starting download...[/{CYAN}]\n")

    start_time = time.time()
    downloaded_path = None

    # Retry logic
    for attempt in range(3):
        try:
            downloaded_path = download_with_progress(ydl_opts, url)
            break
        except Exception as e:
            if attempt < 2:
                wait = (attempt + 1) * 5
                console.print(f"\n  [{RED}]Error: {e}[/{RED}]")
                console.print(f"  [{YELLOW}]Retrying in {wait}s... (attempt {attempt + 2}/3)[/{YELLOW}]")
                time.sleep(wait)
            else:
                console.print(f"\n  [{RED}]✗ Download failed after 3 attempts: {e}[/{RED}]")
                return None

    elapsed = time.time() - start_time

    # Use actual filepath from hook, fallback to scanning dir
    filename = None
    filesize = 0
    if downloaded_path and os.path.exists(downloaded_path):
        filename = os.path.basename(downloaded_path)
        filesize = os.path.getsize(downloaded_path)
    else:
        # Fallback: find newest file in output_dir
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
        files = [f for f in files if os.path.isfile(f)]
        if files:
            newest = max(files, key=os.path.getmtime)
            filename = os.path.basename(newest)
            filesize = os.path.getsize(newest)

    quality_label = "Best (Auto)" if format_choice == "best" else format_choice.get("label", "Unknown")

    return {
        "filename": filename or "video",
        "size": format_size(filesize),
        "quality": quality_label,
        "elapsed": format_elapsed(elapsed),
        "mode": "Video",
    }


def download_audio(url, output_dir):
    """Download audio only as MP3."""
    import yt_dlp

    if not has_ffmpeg():
        console.print(f"\n  [{RED}]✗ ffmpeg is required for MP3 conversion.[/{RED}]")
        console.print(f"  [{DIM}]Install with: pkg install ffmpeg (Termux) or apt install ffmpeg (Linux)[/{DIM}]")
        return None

    ensure_output_dir(output_dir)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    console.print(f"\n  [{CYAN}]Starting audio download (MP3 320kbps)...[/{CYAN}]\n")

    start_time = time.time()

    for attempt in range(3):
        try:
            download_with_progress(ydl_opts, url)
            break
        except Exception as e:
            if attempt < 2:
                wait = (attempt + 1) * 5
                console.print(f"\n  [{RED}]Error: {e}[/{RED}]")
                console.print(f"  [{YELLOW}]Retrying in {wait}s... (attempt {attempt + 2}/3)[/{YELLOW}]")
                time.sleep(wait)
            else:
                console.print(f"\n  [{RED}]✗ Download failed after 3 attempts: {e}[/{RED}]")
                return None

    elapsed = time.time() - start_time

    # Find the downloaded mp3 (yt-dlp converts after download, so scan for newest mp3)
    filename = None
    filesize = 0
    mp3_files = [f for f in os.listdir(output_dir) if f.endswith(".mp3")]
    if mp3_files:
        newest = max(mp3_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
        filename = newest
        filesize = os.path.getsize(os.path.join(output_dir, newest))

    return {
        "filename": filename or "audio.mp3",
        "size": format_size(filesize),
        "quality": "MP3 320kbps",
        "elapsed": format_elapsed(elapsed),
        "mode": "Audio (MP3)",
    }


def download_playlist(url, output_dir):
    """Download all videos in a playlist."""
    import yt_dlp

    playlist_dir = os.path.join(output_dir, "Playlists")
    ensure_output_dir(playlist_dir)

    if has_ffmpeg():
        fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
    else:
        fmt = "best[ext=mp4]/best"

    ydl_opts = {
        "format": fmt,
        "outtmpl": os.path.join(playlist_dir, "%(playlist_title)s", "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }

    console.print(f"\n  [{CYAN}]Fetching playlist info...[/{CYAN}]")
    info = get_video_info(url)

    if info is None:
        console.print(f"  [{RED}]✗ Could not fetch playlist info.[/{RED}]")
        return None

    playlist_title = info.get("title", "Playlist")
    entries = list(info.get("entries", []))
    count = len(entries)

    console.print(f"\n  [{MAGENTA}]📋 Playlist: {playlist_title}[/{MAGENTA}]")
    console.print(f"  [{CYAN}]   Videos: {count}[/{CYAN}]\n")

    start_time = time.time()

    for attempt in range(3):
        try:
            download_with_progress(ydl_opts, url)
            break
        except Exception as e:
            if attempt < 2:
                wait = (attempt + 1) * 5
                console.print(f"\n  [{RED}]Error: {e}[/{RED}]")
                console.print(f"  [{YELLOW}]Retrying in {wait}s... (attempt {attempt + 2}/3)[/{YELLOW}]")
                time.sleep(wait)
            else:
                console.print(f"\n  [{RED}]✗ Playlist download failed: {e}[/{RED}]")
                return None

    elapsed = time.time() - start_time

    return {
        "filename": f"{playlist_title} ({count} videos)",
        "size": "—",
        "quality": "Best (Auto)",
        "elapsed": format_elapsed(elapsed),
        "mode": "Playlist",
    }


def download_thumbnail(url, output_dir):
    """Download video thumbnail image."""
    import yt_dlp

    thumb_dir = os.path.join(output_dir, "Thumbnails")
    ensure_output_dir(thumb_dir)

    ydl_opts = {
        "skip_download": True,
        "writethumbnail": True,
        "outtmpl": os.path.join(thumb_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    console.print(f"\n  [{CYAN}]Downloading thumbnail...[/{CYAN}]")

    start_time = time.time()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        console.print(f"  [{RED}]✗ Failed: {e}[/{RED}]")
        return None

    elapsed = time.time() - start_time

    # Find newest image in thumb_dir
    img_exts = (".jpg", ".jpeg", ".png", ".webp")
    filename = None
    filesize = 0
    images = [f for f in os.listdir(thumb_dir) if f.lower().endswith(img_exts)]
    if images:
        newest = max(images, key=lambda f: os.path.getmtime(os.path.join(thumb_dir, f)))
        filename = newest
        filesize = os.path.getsize(os.path.join(thumb_dir, newest))

    return {
        "filename": filename or "thumbnail.jpg",
        "size": format_size(filesize),
        "quality": "Original",
        "elapsed": format_elapsed(elapsed),
        "mode": "Thumbnail",
    }


def download_subtitles(url, output_dir):
    """Download video subtitles as .srt."""
    import yt_dlp

    sub_dir = os.path.join(output_dir, "Subtitles")
    ensure_output_dir(sub_dir)

    lang = prompt(f"  [{CYAN}]Subtitle language code (e.g. en, es, fr) [en]: [/{CYAN}]", "en")
    if not lang:
        lang = "en"

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [lang],
        "subtitlesformat": "srt",
        "outtmpl": os.path.join(sub_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    console.print(f"\n  [{CYAN}]Downloading subtitles ({lang})...[/{CYAN}]")

    start_time = time.time()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        console.print(f"  [{RED}]✗ Failed: {e}[/{RED}]")
        return None

    elapsed = time.time() - start_time

    # Find newest .srt in sub_dir
    filename = None
    filesize = 0
    srt_files = [f for f in os.listdir(sub_dir) if f.endswith(".srt")]
    if srt_files:
        newest = max(srt_files, key=lambda f: os.path.getmtime(os.path.join(sub_dir, f)))
        filename = newest
        filesize = os.path.getsize(os.path.join(sub_dir, newest))

    if filename is None:
        console.print(f"  [{YELLOW}]⚠ No subtitles found for this video.[/{YELLOW}]")
        return None

    return {
        "filename": filename,
        "size": format_size(filesize),
        "quality": f"{lang.upper()} (SRT)",
        "elapsed": format_elapsed(elapsed),
        "mode": "Subtitles",
    }


def batch_download(urls, output_dir):
    """Download multiple videos from a list of URLs."""
    ensure_output_dir(output_dir)

    total = len(urls)
    console.print(f"\n  [{MAGENTA}]📋 Batch Download: {total} videos[/{MAGENTA}]\n")

    start_time = time.time()
    success = 0
    failed = 0

    for i, url in enumerate(urls, 1):
        url = url.strip()
        if not url:
            continue

        console.print(f"\n  [{CYAN}]━━━ [{i}/{total}] ━━━[/{CYAN}]")
        console.print(f"  [{DIM}]{url}[/{DIM}]")

        info, formats = get_video_formats(url)
        if info is None:
            console.print(f"  [{RED}]✗ Skipping — could not fetch info[/{RED}]")
            failed += 1
            continue

        result = download_video(url, "best", output_dir)
        if result:
            success += 1
        else:
            failed += 1

    elapsed = time.time() - start_time

    return {
        "filename": f"Batch: {success}/{total} succeeded",
        "size": f"{success} downloaded, {failed} failed",
        "quality": "Best (Auto)",
        "elapsed": format_elapsed(elapsed),
        "mode": "Batch Download",
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MENUS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def show_main_menu():
    """Display the main mode selection menu."""
    console.print(Rule("Main Menu", style=CYAN))
    console.print()

    menu_text = Text()
    menu_text.append("  [1]  ", style=YELLOW)
    menu_text.append("Single Video Download\n", style=CYAN)
    menu_text.append("  [2]  ", style=YELLOW)
    menu_text.append("Playlist Download\n", style=CYAN)
    menu_text.append("  [3]  ", style=YELLOW)
    menu_text.append("Audio Only (MP3 320kbps)\n", style=MAGENTA)
    menu_text.append("  [4]  ", style=YELLOW)
    menu_text.append("Thumbnail Download\n", style=CYAN)
    menu_text.append("  [5]  ", style=YELLOW)
    menu_text.append("Subtitles Download (.srt)\n", style=CYAN)
    menu_text.append("  [6]  ", style=YELLOW)
    menu_text.append("Batch Download (multiple URLs)\n", style=MAGENTA)
    menu_text.append("  [0]  ", style=YELLOW)
    menu_text.append("Exit\n", style=RED)

    panel = Panel(
        menu_text,
        title=f"[{MAGENTA}]⚡ Select Mode[/{MAGENTA}]",
        border_style=MAGENTA,
        box=__import__("rich.box", fromlist=["DOUBLE"]).DOUBLE,
        padding=(1, 2),
    )
    console.print(Align.center(panel))
    console.print()

    while True:
        choice = prompt(f"  [{YELLOW}]Enter choice [0-6]: [/{YELLOW}]")
        if choice in ("0", "1", "2", "3", "4", "5", "6"):
            return choice
        console.print(f"  [{RED}]Invalid choice. Enter 0-6.[/{RED}]")


YT_URL_PATTERN = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/playlist\?list=)[\w\-]+'
)

def get_url(prompt_text="Enter video URL"):
    """Prompt user for a URL with validation."""
    while True:
        url = prompt(f"\n  [{CYAN}]{prompt_text}: [/{CYAN}]")
        if url:
            if YT_URL_PATTERN.match(url):
                return url
            console.print(f"  [{RED}]✗ Invalid YouTube URL.[/{RED}]")
            console.print(f"  [{DIM}]Tip: Use https://www.youtube.com/watch?v=... or https://youtu.be/...[/{DIM}]")
        else:
            console.print(f"  [{RED}]URL cannot be empty.[/{RED}]")


def get_output_dir():
    """Return the fixed download directory."""
    return ensure_output_dir(DEFAULT_DOWNLOAD_DIR)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Main entry point."""
    try:
        show_opening_animation()

        while True:
            choice = show_main_menu()

            if choice == "0":
                console.print(f"\n  [{MAGENTA}]Shutting down...[/{MAGENTA}]\n")
                break

            output_dir = get_output_dir()

            # ── Mode 1: Single Video ──
            if choice == "1":
                url = get_url("Enter YouTube URL")
                info, formats = get_video_formats(url)
                if info is None:
                    console.print(Panel(
                        f"  [{RED}]✗ Could not fetch video info.[/{RED}]\n"
                        f"  [{DIM}]Check the URL and your internet connection.[/{DIM}]",
                        title=f"[{RED}]Error[/{RED}]",
                        border_style=RED,
                    ))
                    continue

                format_choice = show_quality_menu(info, formats)
                stats = download_video(url, format_choice, output_dir)
                if stats:
                    show_closing_animation(stats)

            # ── Mode 2: Playlist ──
            elif choice == "2":
                url = get_url("Enter Playlist URL")
                stats = download_playlist(url, output_dir)
                if stats:
                    show_closing_animation(stats)

            # ── Mode 3: Audio Only ──
            elif choice == "3":
                url = get_url("Enter YouTube URL for audio")
                stats = download_audio(url, output_dir)
                if stats:
                    show_closing_animation(stats)

            # ── Mode 4: Thumbnail ──
            elif choice == "4":
                url = get_url("Enter YouTube URL for thumbnail")
                stats = download_thumbnail(url, output_dir)
                if stats:
                    show_closing_animation(stats)

            # ── Mode 5: Subtitles ──
            elif choice == "5":
                url = get_url("Enter YouTube URL for subtitles")
                stats = download_subtitles(url, output_dir)
                if stats:
                    show_closing_animation(stats)

            # ── Mode 6: Batch Download ──
            elif choice == "6":
                console.print(f"\n  [{CYAN}]Enter URLs (one per line). Type 'done' when finished:[/{CYAN}]")
                urls = []
                while True:
                    line = prompt(f"  [{DIM}]URL [{len(urls) + 1}]: [/{DIM}]")
                    if line.lower() == "done":
                        break
                    if line:
                        urls.append(line)

                if not urls:
                    console.print(f"  [{RED}]No URLs entered.[/{RED}]")
                    continue

                stats = batch_download(urls, output_dir)
                if stats:
                    show_closing_animation(stats)

            # Ask to continue
            console.print()
            again = prompt(f"  [{YELLOW}]Download another? (y/N): [/{YELLOW}]", "n").lower()
            if again != "y":
                console.print(f"\n  [{MAGENTA}]Shutting down...[/{MAGENTA}]\n")
                break

        console.print(f"  [{GREEN}]✓ Bankai Downloader exited. See you next time![/{GREEN}]\n")

    except KeyboardInterrupt:
        console.print(f"\n\n  [{GREEN}]✓ Interrupted. Goodbye![/{GREEN}]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
