# Lädt einen LGPL-ffmpeg-Build (Windows) bzw. ein statisches Linux-Binary
# herunter und legt die ffmpeg-Datei im lokalen 'ffmpeg-bundled/'-Verzeichnis ab.
#
# Wird vom Build-Skript vor dem PyInstaller-Lauf ausgeführt. Das Build-Skript
# bindet die heruntergeladene Binary dann via --add-binary ins EXE-Bundle ein.
#
# Quellen:
#   Windows: BtbN FFmpeg LGPL-Build (https://github.com/BtbN/FFmpeg-Builds)
#   Linux:   John van Sickle's static build (https://johnvansickle.com/ffmpeg/)
from __future__ import annotations

import argparse
import io
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path


WIN_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/"
    "ffmpeg-master-latest-win64-lgpl.zip"
)
LINUX_URL = (
    "https://johnvansickle.com/ffmpeg/releases/"
    "ffmpeg-release-amd64-static.tar.xz"
)

BUNDLE_DIR = Path(__file__).parent / "ffmpeg-bundled"
USER_AGENT = "YouTubeAudioDownloader-FFmpegBundler/1.0"


def _http_get(url: str, timeout: float = 120.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _extract_windows(archive_bytes: bytes, target: Path) -> bool:
    """Sucht im LGPL-Build-ZIP die ffmpeg.exe und kopiert sie nach target."""
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
        for name in zf.namelist():
            if name.endswith("/bin/ffmpeg.exe"):
                with zf.open(name) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                return True
    return False


def _extract_linux(archive_bytes: bytes, target: Path) -> bool:
    """Sucht im tar.xz das ffmpeg-Binary und kopiert es nach target."""
    with tempfile.NamedTemporaryFile(suffix=".tar.xz", delete=False) as tmp:
        tmp.write(archive_bytes)
        tmp_path = tmp.name
    try:
        with tarfile.open(tmp_path, mode="r:xz") as tf:
            for member in tf.getmembers():
                if member.isfile() and member.name.endswith("/ffmpeg"):
                    fileobj = tf.extractfile(member)
                    if fileobj is None:
                        continue
                    with open(target, "wb") as dst:
                        shutil.copyfileobj(fileobj, dst)
                    target.chmod(0o755)
                    return True
    finally:
        os.unlink(tmp_path)
    return False


def fetch(force: bool = False) -> Path | None:
    """Holt ffmpeg, falls noch nicht vorhanden (oder force=True).
    Gibt den Pfad zur Binary zurück, oder None bei Fehler."""
    BUNDLE_DIR.mkdir(exist_ok=True)

    is_windows = sys.platform == "win32"
    binary_name = "ffmpeg.exe" if is_windows else "ffmpeg"
    target = BUNDLE_DIR / binary_name

    if target.exists() and target.stat().st_size > 0 and not force:
        size_mb = target.stat().st_size / 1024 / 1024
        print(f"  ffmpeg bereits im Cache ({size_mb:.1f} MB): {target}")
        return target

    url = WIN_URL if is_windows else LINUX_URL
    print(f"  Lade ffmpeg von {url} …")
    try:
        data = _http_get(url)
    except Exception as e:
        print(f"  [FEHLER] Download fehlgeschlagen: {e}")
        return None

    print(f"  Heruntergeladen: {len(data)/1024/1024:.1f} MB. Entpacke …")
    try:
        ok = _extract_windows(data, target) if is_windows else _extract_linux(data, target)
    except Exception as e:
        print(f"  [FEHLER] Entpacken fehlgeschlagen: {e}")
        return None

    if not ok or not target.exists():
        print("  [FEHLER] ffmpeg-Binary nicht im Archiv gefunden.")
        return None

    size_mb = target.stat().st_size / 1024 / 1024
    print(f"  ffmpeg bereit ({size_mb:.1f} MB): {target}")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ffmpeg für das EXE-Bundle herunterladen.")
    parser.add_argument("--force", action="store_true",
                        help="erneut herunterladen, auch wenn schon im Cache")
    args = parser.parse_args()
    result = fetch(force=args.force)
    sys.exit(0 if result else 1)
