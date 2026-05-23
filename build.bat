@echo off
REM YouTube Audio Downloader - EXE-Build (DE + EN, mit gebuendeltem ffmpeg)
setlocal enabledelayedexpansion

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
)

echo [INFO] Installiere Build-Abhaengigkeiten...
".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
".venv\Scripts\python.exe" -m pip install --quiet pyinstaller

REM ---- ffmpeg bundeln (laedt LGPL-Build von BtbN beim ersten Mal) ----
echo.
echo [INFO] Bereite ffmpeg fuer das Bundle vor...
".venv\Scripts\python.exe" bundle_ffmpeg.py
if errorlevel 1 (
    echo [WARNUNG] ffmpeg-Download fehlgeschlagen. Der Build laeuft trotzdem,
    echo            aber die EXE braucht dann eine externe ffmpeg.exe.
    set "FFMPEG_BINDING="
) else (
    set "FFMPEG_BINDING=--add-binary ffmpeg-bundled\ffmpeg.exe;."
)

echo.
echo [INFO] Erzeuge App-Icon...
".venv\Scripts\python.exe" -c "from app_logo import make_logo; logo=make_logo(256); logo.save('app_icon.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"

REM Build-Konfig sichern
copy /Y build_config.py build_config.py.bak >nul

REM ------- Deutsche Variante -------
echo.
echo [INFO] Baue deutsche Version...
".venv\Scripts\python.exe" -c "open('build_config.py','w').write('BUILD_DEFAULT_LANG = \"de\"\n')"
".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "YouTubeAudioDownloader-DE" ^
    --icon "app_icon.ico" ^
    --collect-all customtkinter ^
    --collect-all yt_dlp ^
    --hidden-import updater ^
    --hidden-import app_logo ^
    --hidden-import i18n ^
    --hidden-import paths ^
    --hidden-import build_config ^
    %FFMPEG_BINDING% ^
    youtube_audio_downloader.py

if errorlevel 1 (
    echo [FEHLER] DE-Build fehlgeschlagen.
    copy /Y build_config.py.bak build_config.py >nul
    del build_config.py.bak
    pause
    exit /b 1
)

REM ------- Englische Variante -------
echo.
echo [INFO] Baue englische Version...
".venv\Scripts\python.exe" -c "open('build_config.py','w').write('BUILD_DEFAULT_LANG = \"en\"\n')"
".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "YouTubeAudioDownloader-EN" ^
    --icon "app_icon.ico" ^
    --collect-all customtkinter ^
    --collect-all yt_dlp ^
    --hidden-import updater ^
    --hidden-import app_logo ^
    --hidden-import i18n ^
    --hidden-import paths ^
    --hidden-import build_config ^
    %FFMPEG_BINDING% ^
    youtube_audio_downloader.py

if errorlevel 1 (
    echo [FEHLER] EN-Build fehlgeschlagen.
    copy /Y build_config.py.bak build_config.py >nul
    del build_config.py.bak
    pause
    exit /b 1
)

REM Build-Konfig wiederherstellen
copy /Y build_config.py.bak build_config.py >nul
del build_config.py.bak

echo.
echo ============================================================
echo  Build erfolgreich!
echo.
echo  Deutsche Version:    dist\YouTubeAudioDownloader-DE.exe
echo  Englische Version:   dist\YouTubeAudioDownloader-EN.exe
echo.
if defined FFMPEG_BINDING (
    echo  ffmpeg ist im Bundle enthalten. Die EXEs sind 100%% self-contained
    echo  und brauchen auf dem Zielsystem nichts ausser einer
    echo  Internetverbindung fuer den Update-Check.
) else (
    echo  Hinweis: ffmpeg konnte nicht heruntergeladen werden und ist
    echo  NICHT im Bundle. Bitte ffmpeg.exe manuell neben die EXE legen.
)
echo ============================================================
pause

endlocal
