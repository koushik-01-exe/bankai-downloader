# Bankai Downloader

A feature-rich YouTube video downloader CLI tool for Termux and Linux, built with Python.

## Features

- **6 Download Modes** — Single video, Playlist, Audio (MP3 320kbps), Thumbnail, Subtitles (.srt), Batch download
- **Quality Selection** — Interactive menu showing all available resolutions, FPS, format, and estimated size
- **Rich Terminal UI** — Animated ASCII banner, progress bars, styled panels, spinners
- **Smart Retry** — Auto-retries up to 3 times on network failure with countdown
- **Organized Output** — Saves to `/storage/emulated/0/Download/BankaiDownloader/`

## Install (One Command)

**Termux:**
```bash
pkg install git -y && git clone https://github.com/koushik-01-exe/bankai-downloader.git && cd bankai-downloader && bash install.sh
```

**Linux / Mac:**
```bash
git clone https://github.com/koushik-01-exe/bankai-downloader.git && cd bankai-downloader && bash install.sh
```

After install, run from anywhere:
```bash
bankai
```

## Usage

```
bankai
```

Select a mode from the menu:

```
  [1]  Single Video Download
  [2]  Playlist Download
  [3]  Audio Only (MP3 320kbps)
  [4]  Thumbnail Download
  [5]  Subtitles Download (.srt)
  [6]  Batch Download (multiple URLs)
  [0]  Exit
```

Paste a YouTube URL when prompted, pick your quality, and the download starts.

## Requirements

- Python 3.8+
- ffmpeg (required for merging video+audio streams)

The install script handles all dependencies automatically.

## Dependencies

| Package    | Purpose                        |
|------------|--------------------------------|
| `yt-dlp`   | YouTube download backend       |
| `rich`     | Terminal UI (panels, progress) |
| `pyfiglet` | ASCII art banner               |

## File Structure

```
bankai-downloader/
├── bankai_downloader.py   # Main tool
├── requirements.txt       # Python dependencies
├── install.sh             # One-line installer
├── .gitignore
└── README.md
```

## License

MIT

## Author

**Kouxik** — [Telegram](https://t.me/BankaiMods)
