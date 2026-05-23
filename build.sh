#!/usr/bin/env bash
# YouTube Audio Downloader - Binary-Build (DE + EN, mit gebündeltem ffmpeg)
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[FEHLER] python3 nicht gefunden."
    exit 1
fi

if [ ! -f ".venv/bin/python" ]; then
    python3 -m venv .venv
fi

echo "[INFO] Installiere Build-Abhängigkeiten..."
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt
.venv/bin/python -m pip install --quiet pyinstaller

# ffmpeg bundeln
echo
echo "[INFO] Bereite ffmpeg für das Bundle vor..."
FFMPEG_ARGS=""
if .venv/bin/python bundle_ffmpeg.py; then
    FFMPEG_ARGS="--add-binary ffmpeg-bundled/ffmpeg:."
else
    echo "[WARNUNG] ffmpeg-Download fehlgeschlagen. Der Build läuft trotzdem,"
    echo "          aber die Binary braucht dann externes ffmpeg im PATH."
fi

echo "[INFO] Erzeuge App-Icon..."
.venv/bin/python -c "from app_logo import make_logo; logo=make_logo(256); logo.save('app_icon.png')"

cp build_config.py build_config.py.bak

build_variant() {
    local lang="$1"
    local upper
    upper=$(echo "$lang" | tr '[:lower:]' '[:upper:]')

    echo
    echo "[INFO] Baue Variante: $upper"
    .venv/bin/python -c "open('build_config.py','w').write('BUILD_DEFAULT_LANG = \"$lang\"\n')"
    .venv/bin/python -m PyInstaller \
        --noconfirm \
        --onefile \
        --windowed \
        --name "YouTubeAudioDownloader-$upper" \
        --collect-all customtkinter \
        --collect-all yt_dlp \
        --hidden-import updater \
        --hidden-import app_logo \
        --hidden-import i18n \
        --hidden-import paths \
        --hidden-import build_config \
        $FFMPEG_ARGS \
        youtube_audio_downloader.py
}

build_variant de
build_variant en

mv build_config.py.bak build_config.py

echo
echo "============================================================"
echo "  Build erfolgreich!"
echo "  Deutsche Version:   dist/YouTubeAudioDownloader-DE"
echo "  Englische Version:  dist/YouTubeAudioDownloader-EN"
if [ -n "$FFMPEG_ARGS" ]; then
    echo
    echo "  ffmpeg ist im Bundle enthalten — Binaries sind self-contained."
fi
echo "============================================================"
