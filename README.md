# YouTube Audio Downloader

GUI for downloading YouTube videos and playlists as
**FLAC (24-bit)** or **MP3 (320 kbps)**. Windows + Linux, German + English UI.

**Author:** David Christopher Groß · **License:** MIT (see `LICENSE`)

---

## ⚠ Important note on audio quality

YouTube delivers audio in a **lossy** format by default — typically
Opus at around **160 kbps** (premium) or AAC at around **128 kbps**.
A true Hi-Res source does **not** exist on YouTube.

What this program does: it grabs the best available stream and packs
it losslessly into a 24-bit FLAC container. From the download onward,
nothing else is lost — but the original YouTube quality remains the
upper limit. It is not the same as a 24-bit studio master.

| Format | Lossless from download? | True studio quality? |
|---|---|---|
| FLAC (24-bit) | Yes | No — source is lossy |
| MP3 (320 kbps) | No, re-encoded | No |

If you want real Hi-Res quality: **Qobuz, Tidal Max, Bandcamp** or similar.
For YouTube content (bootlegs, your own uploads, demos, mixes), FLAC 24-bit
is the best quality this tool can offer.

---

## Features

- Single YouTube videos and complete playlists
- Lossless FLAC (24-bit container) or MP3 320 kbps CBR
- Cover is embedded into the audio file and additionally stored as `cover.jpg` + `folder.jpg` in the target folder
- No leftover WebP/PNG files — thumbnails are converted to JPG and cleaned up after embedding
- Metadata (title, artist, …) is set automatically
- Default target folder: `<Downloads>/YT-Music`
- **ffmpeg is bundled into the EXE** — no external installation needed
- Automatic yt-dlp update check on startup
- German and English UI, switchable inside the app
- Playlist tracks land in a subfolder named after the playlist, numbered sequentially
- Live progress display, can be cancelled at any time

---

## Self-contained EXE — what's actually included

When built with `build.bat`, the resulting EXEs contain **everything**
needed to run the program:

- ✔ Python runtime
- ✔ All Python libraries (yt-dlp, customtkinter, Pillow, urllib, …)
- ✔ **ffmpeg** (LGPL build by BtbN, around 80 MB)
- ✔ App icon, translations, logo (generated programmatically)

**EXE size:** approximately **100–130 MB** (with bundled ffmpeg).
Without the ffmpeg bundle it would be around 35 MB.

On the target machine, **nothing else** is required except:
- Internet access (for yt-dlp downloads and the update check)
- Write permissions on `%LOCALAPPDATA%` (standard on any Windows user profile)

On first launch, Windows Defender SmartScreen may show a warning
("Unknown publisher") — this is normal for self-built EXEs without code signing.

---

## Default download path

| Platform | Path |
|---|---|
| Windows | `%USERPROFILE%\Downloads\YT-Music` (also handles redirected Downloads folders correctly) |
| Linux | `~/Downloads/YT-Music` (or `$XDG_DOWNLOAD_DIR/YT-Music`) |
| macOS | `~/Downloads/YT-Music` |

The path can be changed in the app on a per-download basis.

---

## Multilingual UI

Two pre-configured builds:

| EXE | Default language |
|---|---|
| `YouTubeAudioDownloader-DE.exe` | German |
| `YouTubeAudioDownloader-EN.exe` | English |

The language can be switched at any time inside the app via
**"About" → "Language"**. The selection is stored per user in
`%LOCALAPPDATA%\YouTubeAudioDownloader\config.json`.

---

## yt-dlp auto-update

YouTube regularly changes its internal API — yt-dlp therefore needs
to be updated regularly, otherwise downloads will start to fail.

- **Detection:** on startup, the app compares the loaded yt-dlp version against the latest on PyPI
- **Installation:** on confirmation, the updated yt-dlp is extracted into the user directory; it is loaded automatically on the next launch
- **Works in both distributions** (Python mode and EXE)
- **No admin rights required**
- **Toggle in the About dialog**
- **Rollback** via "Remove override"

---

## Building the EXE

### Windows
```bat
build.bat
```

What happens:
1. A `.venv` is created (if not already present)
2. **ffmpeg is downloaded automatically** (LGPL build by BtbN, ~50 MB download).
   It is cached in the `ffmpeg-bundled/` folder; subsequent builds skip the download.
3. PyInstaller builds two EXEs (DE + EN) including all components and ffmpeg
4. Result:
   - `dist\YouTubeAudioDownloader-DE.exe`
   - `dist\YouTubeAudioDownloader-EN.exe`

If the ffmpeg download fails (e.g. no internet), the build still completes —
but the resulting EXE then needs an external ffmpeg in the same folder.

### Linux
```bash
./build.sh
```
Downloads a static ffmpeg build from johnvansickle.com and bundles it the same way.

---

## Quick start (without building)

Requirements: **Python ≥ 3.10** and **ffmpeg**.

### Windows
```bat
run.bat
```

### Linux
```bash
chmod +x run.sh
./run.sh
```

On first launch, a `.venv` is created automatically and all dependencies
are installed. In Python mode, ffmpeg must be available in PATH or
next to the script (see below).

---

## Installing ffmpeg manually (only for Python mode or builds without bundling)

### Windows (portable, no admin required)
1. Download a static build from <https://www.gyan.dev/ffmpeg/builds/> or
   <https://github.com/BtbN/FFmpeg-Builds>.
2. Place `ffmpeg.exe` directly next to the script or EXE.

### Linux
```bash
sudo apt install ffmpeg          # Debian/Ubuntu
sudo dnf install ffmpeg          # Fedora
```

---

## License and third-party software

The code in this repository is released under the MIT license (see `LICENSE`).

The bundled third-party components — in particular ffmpeg (LGPL-2.1) and
yt-dlp (Unlicense) — retain their respective licenses. Details and source
references: see `THIRD_PARTY_LICENSES.txt`.

**Brief note on the ffmpeg LGPL:** an unmodified LGPL build is bundled and
ffmpeg is invoked as an external process — i.e. ffmpeg is not linked into
the application code, but called via process invocation. The ffmpeg source
code is freely available from the upstream project.

---

## Android?

No dedicated port. Recommended (Open Source, via F-Droid):

- **Seal** — [github.com/JunkFood02/Seal](https://github.com/JunkFood02/Seal)
- **YTDLnis** — [github.com/deniscerri/ytdlnis](https://github.com/deniscerri/ytdlnis)
- **NewPipe** — [newpipe.net](https://newpipe.net/)

---

## Legal (content)

Use at your **own responsibility**. Recommended for:

- Your own uploads
- Content under free licenses (CC, Public Domain)
- Content you hold the rights to

---

## Project structure

```
yt-audio-downloader/
├── youtube_audio_downloader.py   # Main program
├── app_logo.py                   # Logo generator
├── updater.py                    # yt-dlp auto-update
├── i18n.py                       # DE/EN translations
├── paths.py                      # Platform-specific paths
├── build_config.py               # Build-time default language
├── bundle_ffmpeg.py              # ffmpeg downloader for build
├── requirements.txt
├── run.bat / run.sh              # Direct start
├── build.bat / build.sh          # EXE build (with ffmpeg bundling)
├── LICENSE                       # MIT (own code)
├── THIRD_PARTY_LICENSES.txt      # Third-party software (ffmpeg, yt-dlp, …)
└── README.md
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| HTTP 403 / format errors | "Check for updates" in the About dialog → update yt-dlp |
| Update check fails (corporate proxy) | Set the `HTTPS_PROXY` env variable, or disable the auto-check |
| Override causes issues | About dialog → "Remove override" → restart |
| Windows SmartScreen warning | "More info" → "Run anyway" (normal for self-built EXEs) |
| ffmpeg download failed during build | Check internet; alternatively place `ffmpeg.exe` manually in `ffmpeg-bundled/` |
| GUI does not start (Linux) | `sudo apt install python3-tk` |
