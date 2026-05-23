#!/usr/bin/env bash
# ============================================================
#  YouTube Audio Downloader - direkter Start (ohne EXE-Build)
# ============================================================
set -e
cd "$(dirname "$0")"

# Python prüfen
if ! command -v python3 >/dev/null 2>&1; then
    echo "[FEHLER] python3 nicht gefunden. Bitte Python 3.10+ installieren."
    exit 1
fi

# venv anlegen falls nötig
if [ ! -f ".venv/bin/python" ]; then
    echo "[INFO] Lege virtuelle Umgebung an..."
    python3 -m venv .venv
fi

# Dependencies installieren
echo "[INFO] Installiere/Aktualisiere Abhängigkeiten..."
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt

# Programm starten
echo "[INFO] Starte YouTube Audio Downloader..."
.venv/bin/python youtube_audio_downloader.py
