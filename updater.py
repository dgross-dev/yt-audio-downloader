# Update-Mechanismus für yt-dlp.
# Hintergrund: yt-dlp muss regelmäßig aktualisiert werden, da YouTube
# laufend seine API ändert. In der PyInstaller-EXE können wir aber kein
# `pip install --upgrade` aufrufen — yt-dlp liegt dort statisch im Bundle.
#
# Lösung: Updates werden in ein User-Verzeichnis entpackt und beim
# Programmstart vor das gebundelte yt-dlp in sys.path eingehängt. Funktioniert
# in beiden Distributionen (Python-venv und PyInstaller-EXE) und kommt ohne
# Admin-Rechte aus.
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


PYPI_URL = "https://pypi.org/pypi/yt-dlp/json"
USER_AGENT = "YouTubeAudioDownloader/1.2 (Updater)"
HTTP_TIMEOUT = 8.0          # für API-Calls
DOWNLOAD_TIMEOUT = 60.0     # für Wheel-Download


def _appdata_dir() -> Path:
    """Plattformübliches User-Data-Verzeichnis."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "YouTubeAudioDownloader"


APP_DATA_DIR = _appdata_dir()
OVERRIDE_DIR = APP_DATA_DIR / "yt-dlp-override"
CONFIG_FILE = APP_DATA_DIR / "config.json"


# ---- Override-Setup -------------------------------------------------------
# Muss VOR `import yt_dlp` laufen, sonst greift die Override-Version nicht.

def setup_override() -> str | None:
    """Falls ein lokales yt-dlp-Update vorliegt, dieses vorne in sys.path
    eintragen. Gibt den Pfad zurück, wenn aktiviert."""
    override_pkg = OVERRIDE_DIR / "yt_dlp"
    if override_pkg.is_dir():
        path_str = str(OVERRIDE_DIR)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
        return path_str
    return None


def is_override_active() -> bool:
    return (OVERRIDE_DIR / "yt_dlp").is_dir()


def clear_override() -> bool:
    """Entfernt einen evtl. vorhandenen Override (z.B. bei kaputter Version)."""
    pkg = OVERRIDE_DIR / "yt_dlp"
    if not pkg.exists():
        return False
    try:
        shutil.rmtree(pkg)
        return True
    except OSError:
        return False


# ---- Versionsvergleich ----------------------------------------------------

def _parse_version(v: str) -> tuple:
    """yt-dlp nutzt Datumsversionen wie '2024.10.07' oder '2024.11.04.232045'.
    Wir parsen Komponenten als Ints — alles Nicht-Numerische wird 0."""
    parts = []
    for p in str(v).split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def is_newer(remote: str, local: str) -> bool:
    return _parse_version(remote) > _parse_version(local)


# ---- PyPI-Abfrage ---------------------------------------------------------

def _request(url: str, timeout: float):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout)


def fetch_latest_info() -> dict | None:
    """JSON-Metadaten von PyPI laden. None bei Netzwerkproblemen."""
    try:
        with _request(PYPI_URL, HTTP_TIMEOUT) as r:
            return json.load(r)
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return None


def latest_version(info: dict | None = None) -> str | None:
    if info is None:
        info = fetch_latest_info()
    if not info:
        return None
    return info.get("info", {}).get("version")


def _wheel_url(info: dict, version: str) -> str | None:
    """Wheel-URL für genannte Version aus dem PyPI-Response holen.
    Wir bevorzugen das py3-none-any wheel (pure Python)."""
    releases = info.get("releases", {}).get(version, [])
    candidates = [r for r in releases if r.get("packagetype") == "bdist_wheel"]
    if not candidates:
        return None
    # py3-none-any zuerst — yt-dlp ist pure Python
    candidates.sort(key=lambda r: 0 if "py3-none-any" in r.get("filename", "") else 1)
    return candidates[0].get("url")


# ---- Update-Installation --------------------------------------------------

def install_update(version: str, progress_cb=None) -> bool:
    """Wheel der angegebenen Version laden und yt_dlp/ in OVERRIDE_DIR
    entpacken. Beim nächsten Programmstart wird die neue Version geladen.

    progress_cb(fraction: float) wird beim Download aufgerufen, falls gesetzt.
    """
    info = fetch_latest_info()
    if not info:
        return False
    url = _wheel_url(info, version)
    if not url:
        return False

    OVERRIDE_DIR.mkdir(parents=True, exist_ok=True)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".whl", delete=False) as tmp:
            tmp_path = tmp.name

        with _request(url, DOWNLOAD_TIMEOUT) as resp:
            total = int(resp.headers.get("Content-Length") or 0)
            done = 0
            with open(tmp_path, "wb") as fh:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    fh.write(chunk)
                    done += len(chunk)
                    if progress_cb and total:
                        progress_cb(done / total)

        # in einen temp-Ordner entpacken, dann atomar verschieben.
        # Falls beim Entpacken was schiefgeht, bleibt die bisherige Version intakt.
        with tempfile.TemporaryDirectory(prefix="ytdlp_unpack_") as unpack_dir:
            with zipfile.ZipFile(tmp_path) as zf:
                for name in zf.namelist():
                    if name.startswith("yt_dlp/") and not name.endswith("/"):
                        zf.extract(name, unpack_dir)

            new_pkg = Path(unpack_dir) / "yt_dlp"
            if not new_pkg.is_dir():
                return False

            old_pkg = OVERRIDE_DIR / "yt_dlp"
            backup_pkg = OVERRIDE_DIR / "yt_dlp.old"

            if old_pkg.exists():
                # alten in .old umbenennen (rollback-Möglichkeit)
                if backup_pkg.exists():
                    shutil.rmtree(backup_pkg, ignore_errors=True)
                old_pkg.rename(backup_pkg)

            shutil.move(str(new_pkg), str(old_pkg))

            # backup nach erfolgreichem move entsorgen
            if backup_pkg.exists():
                shutil.rmtree(backup_pkg, ignore_errors=True)

        return True

    except (OSError, zipfile.BadZipFile, urllib.error.URLError, TimeoutError):
        return False
    finally:
        if tmp_path and os.path.isfile(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


# ---- Config (Auto-Check Toggle) -------------------------------------------

DEFAULT_CONFIG = {
    "auto_check_updates": True,
    "last_known_version": None,
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # ergänze fehlende keys mit defaults
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    try:
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except OSError:
        pass  # silent fail — Update funktioniert auch ohne persistenten config


# ---- Convenience ----------------------------------------------------------

def get_current_yt_dlp_version() -> str:
    """Aktuelle yt-dlp Version aus dem aktuell geladenen Modul."""
    try:
        import yt_dlp.version
        return yt_dlp.version.__version__
    except Exception:
        return "unknown"
