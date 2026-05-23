@echo off
REM ============================================================
REM  YouTube Audio Downloader - direkter Start (ohne EXE-Build)
REM ============================================================
setlocal

cd /d "%~dp0"

REM Pruefe ob Python vorhanden ist
where python >nul 2>nul
if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden.
    echo Bitte Python 3.10 oder neuer installieren: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Virtuelle Umgebung anlegen falls nicht vorhanden
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Lege virtuelle Umgebung an...
    python -m venv .venv
    if errorlevel 1 (
        echo [FEHLER] venv-Erstellung fehlgeschlagen.
        pause
        exit /b 1
    )
)

REM Dependencies installieren (nur beim ersten Mal langsam)
echo [INFO] Installiere/Aktualisiere Abhaengigkeiten...
".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt

REM Programm starten
echo [INFO] Starte YouTube Audio Downloader...
".venv\Scripts\python.exe" youtube_audio_downloader.py

endlocal
