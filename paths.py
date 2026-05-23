# Plattformübliche Pfade ermitteln (Default-Downloadordner etc.).
from __future__ import annotations

import os
import sys
from pathlib import Path


def system_downloads_dir() -> Path:
    """System-Downloads-Ordner finden — plattformübergreifend.

    Windows: bevorzugt der echte 'Downloads'-Known-Folder (auch wenn umgeleitet),
             sonst Fallback auf %USERPROFILE%\\Downloads.
    Linux:   $XDG_DOWNLOAD_DIR aus xdg-user-dirs, sonst ~/Downloads.
    macOS:   ~/Downloads.
    """
    home = Path.home()

    if sys.platform == "win32":
        # Known Folders API — funktioniert auch bei umgeleiteten Profilen
        # (z.B. Downloads auf D:\). Wenn das schiefgeht, Fallback auf ~/Downloads.
        try:
            import ctypes
            from ctypes import wintypes

            # FOLDERID_Downloads
            FOLDERID_DOWNLOADS = ctypes.c_char_p(
                b"\x74\xfa\x40\x37\xc7\xfa\x1b\x4f\xa6\xc5\xea\x3a\xd6\xa4\x1f\x4d"
            )
            # SHGetKnownFolderPath ist die korrekte API; sie liefert einen PWSTR.
            class GUID(ctypes.Structure):
                _fields_ = [
                    ("Data1", wintypes.DWORD),
                    ("Data2", wintypes.WORD),
                    ("Data3", wintypes.WORD),
                    ("Data4", wintypes.BYTE * 8),
                ]

            # GUID für Downloads-Ordner: {374DE290-123F-4565-9164-39C4925E467B}
            downloads_guid = GUID(
                0x374DE290, 0x123F, 0x4565,
                (wintypes.BYTE * 8)(0x91, 0x64, 0x39, 0xC4, 0x92, 0x5E, 0x46, 0x7B),
            )

            shell32 = ctypes.windll.shell32
            shell32.SHGetKnownFolderPath.argtypes = [
                ctypes.POINTER(GUID), wintypes.DWORD, wintypes.HANDLE,
                ctypes.POINTER(ctypes.c_wchar_p),
            ]
            shell32.SHGetKnownFolderPath.restype = ctypes.HRESULT

            path_ptr = ctypes.c_wchar_p()
            hr = shell32.SHGetKnownFolderPath(
                ctypes.byref(downloads_guid), 0, 0, ctypes.byref(path_ptr)
            )
            if hr == 0 and path_ptr.value:
                result = Path(path_ptr.value)
                # speicher freigeben
                ctypes.windll.ole32.CoTaskMemFree(path_ptr)
                return result
        except Exception:
            pass
        return home / "Downloads"

    if sys.platform == "darwin":
        return home / "Downloads"

    # Linux / BSD: XDG-Standard
    xdg_dir = _read_xdg_user_dir("DOWNLOAD")
    if xdg_dir:
        return xdg_dir
    return home / "Downloads"


def _read_xdg_user_dir(name: str) -> Path | None:
    """Liest ~/.config/user-dirs.dirs und gibt den entsprechenden Pfad zurück."""
    cfg = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "user-dirs.dirs"
    if not cfg.is_file():
        return None
    try:
        for line in cfg.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith(f"XDG_{name}_DIR"):
                _, _, val = line.partition("=")
                val = val.strip().strip('"')
                val = val.replace("$HOME", str(Path.home()))
                return Path(val)
    except OSError:
        pass
    return None


def default_target_dir() -> Path:
    """Standard-Zielordner für Downloads: <Downloads>/YT-Music."""
    return system_downloads_dir() / "YT-Music"
