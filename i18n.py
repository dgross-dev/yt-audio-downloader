# Übersetzungen für GUI und Log-Ausgaben.
# Sprache umschaltbar zur Laufzeit; Default kommt aus Config oder Build-Konstante.
from __future__ import annotations

import locale


TRANSLATIONS = {
    "de": {
        # App allgemein
        "app.subtitle": "Playlists oder einzelne Videos als FLAC (24 Bit) oder MP3 (320 kbps) speichern",
        "app.window_title": "YouTube Audio Downloader v{version}",

        # Buttons / Labels
        "ui.url_label": "YouTube-URL (Video oder Playlist)",
        "ui.url_placeholder": "https://www.youtube.com/playlist?list=… oder https://www.youtube.com/watch?v=…",
        "ui.format_label": "Audioformat",
        "ui.target_label": "Zielordner",
        "ui.log_label": "Protokoll",
        "ui.browse": "Durchsuchen…",
        "ui.start_download": "⬇   Download starten",
        "ui.downloading": "Lade herunter…",
        "ui.cancel": "Abbrechen",
        "ui.about": "Über",
        "ui.close": "Schließen",
        "ui.language": "Sprache",

        # Formate
        "format.flac": "FLAC – 24 Bit, verlustfrei (beste Qualität)",
        "format.mp3": "MP3 – 320 kbps (HQ)",

        # Status
        "status.ready": "Bereit",
        "status.done": "Fertig ✓",
        "status.ended": "Beendet",
        "status.cancelling": "Wird abgebrochen…",
        "status.converting": "Konvertiere …",
        "status.update_installed": "Update installiert — bitte neu starten",
        "status.downloading_fmt": "⬇  {prefix}{title}   {pct}%   {speed}   ETA {eta}",

        # Update
        "update.pill": "Update: {version}",
        "update.pill_generic": "Update verfügbar",
        "update.dialog_title": "yt-dlp aktualisieren",
        "update.dialog_header": "Aktualisiere yt-dlp auf {version}",
        "update.preparing": "Download wird vorbereitet…",
        "update.downloading": "Herunterladen… {pct} %",
        "update.success": "Update installiert. Bitte Programm neu starten.",
        "update.failed": "Update fehlgeschlagen. Bitte später erneut versuchen.",
        "update.available_title": "Update verfügbar",
        "update.available_msg": "Eine neuere yt-dlp Version ist verfügbar:\n\n  Aktuell:   {current}\n  Verfügbar: {available}\n\nJetzt herunterladen und installieren?",
        "update.install_confirm_title": "Update installieren",
        "update.install_confirm_msg": "yt-dlp {version} jetzt herunterladen?",
        "update.check_title": "Update-Prüfung",
        "update.check_failed": "Konnte die aktuelle Version nicht ermitteln. Bitte Internetverbindung prüfen.",
        "update.check_uptodate": "yt-dlp ist auf dem aktuellen Stand ({version}).",
        "update.section_title": "yt-dlp Updates",
        "update.auto_check_label": "Beim Start automatisch nach Updates suchen",
        "update.check_now": "Jetzt nach Updates suchen",
        "update.clear_override": "Override entfernen",
        "update.no_override": "Es ist kein Override aktiv.",
        "update.clear_confirm_title": "Override entfernen",
        "update.clear_confirm_msg": "Damit wird die mitgelieferte yt-dlp-Version wieder genutzt.\nBitte das Programm danach neu starten.\n\nFortfahren?",
        "update.clear_done": "Override entfernt. Bitte neu starten.",
        "update.clear_failed": "Override konnte nicht entfernt werden.",

        # About
        "about.info_block": "Autor:    {author}\nLizenz:   {license} ({year})\nBackend:  yt-dlp {ytdlp}",
        "about.disclaimer": "Nutzung auf eigene Verantwortung.\nBitte nur Inhalte herunterladen, an denen entsprechende\nRechte bestehen.",
        "about.ytdlp_bundled": " (gebundelt)",
        "about.ytdlp_updated": " (aktualisiert)",

        # Dialoge
        "dialog.hint": "Hinweis",
        "dialog.error": "Fehler",
        "dialog.done": "Erledigt",
        "dialog.missing_url": "Bitte eine YouTube-URL eingeben.",
        "dialog.invalid_url": "Die URL sieht nicht wie eine gültige Web-Adresse aus.",
        "dialog.missing_target": "Bitte einen Zielordner wählen.",
        "dialog.target_create_failed": "Zielordner kann nicht angelegt werden:\n{err}",
        "dialog.no_ffmpeg_title": "ffmpeg nicht gefunden",
        "dialog.no_ffmpeg_msg": "Es wurde keine ffmpeg-Installation gefunden.\n\nBitte ffmpeg installieren oder die ffmpeg(.exe) in den Programm-Ordner legen.\n\nOhne ffmpeg ist keine Audio-Konvertierung möglich.",
        "dialog.no_ffmpeg_short": "ffmpeg wurde nicht gefunden. Bitte installieren oder ffmpeg(.exe) in den Programm-Ordner legen.",

        # Log
        "log.start_download": "▶  Starte Download",
        "log.url_line": "    URL:      {url}",
        "log.format_line": "    Format:   {fmt}",
        "log.target_line": "    Ziel:     {target}",
        "log.ffmpeg_line": "    ffmpeg:   {path}",
        "log.ytdlp_line": "    yt-dlp:   {version}{override}",
        "log.override_marker": " (override)",
        "log.detected": "▶  Erkannt als: {kind}",
        "log.kind_playlist": "Playlist",
        "log.kind_single": "Einzelvideo",
        "log.downloaded": "✓  Heruntergeladen: {filename}",
        "log.all_done": "\n✓  Alle Downloads abgeschlossen.",
        "log.cancelled": "\n⏹  Download abgebrochen.",
        "log.cancelled_by_user": "\n⏹  Download durch Nutzer abgebrochen.",
        "log.error": "\n✗  Fehler: {err}",
        "log.cancel_requested": "⏹  Abbruch angefordert — aktuelle Datei wird noch fertiggestellt…",
        "log.playlist_probe_failed": "⚠  Playlist-Probe per API fehlgeschlagen, nutze URL-Heuristik. ({err})",
        "log.update_available": "⚙  Neue yt-dlp-Version verfügbar: {version}",
        "log.update_done": "✓  yt-dlp aktualisiert. Bitte das Programm neu starten, damit die neue Version geladen wird.",
        "log.cover_saved": "Cover gespeichert: {folder}/",
        "log.format_flac": "FLAC 24-Bit (verlustfrei)",
        "log.format_mp3": "MP3 320 kbps",
    },

    "en": {
        "app.subtitle": "Save playlists or single videos as FLAC (24-bit) or MP3 (320 kbps)",
        "app.window_title": "YouTube Audio Downloader v{version}",

        "ui.url_label": "YouTube URL (video or playlist)",
        "ui.url_placeholder": "https://www.youtube.com/playlist?list=… or https://www.youtube.com/watch?v=…",
        "ui.format_label": "Audio format",
        "ui.target_label": "Target folder",
        "ui.log_label": "Log",
        "ui.browse": "Browse…",
        "ui.start_download": "⬇   Start download",
        "ui.downloading": "Downloading…",
        "ui.cancel": "Cancel",
        "ui.about": "About",
        "ui.close": "Close",
        "ui.language": "Language",

        "format.flac": "FLAC – 24-bit, lossless (best quality)",
        "format.mp3": "MP3 – 320 kbps (HQ)",

        "status.ready": "Ready",
        "status.done": "Done ✓",
        "status.ended": "Finished",
        "status.cancelling": "Cancelling…",
        "status.converting": "Converting…",
        "status.update_installed": "Update installed — please restart",
        "status.downloading_fmt": "⬇  {prefix}{title}   {pct}%   {speed}   ETA {eta}",

        "update.pill": "Update: {version}",
        "update.pill_generic": "Update available",
        "update.dialog_title": "Update yt-dlp",
        "update.dialog_header": "Updating yt-dlp to {version}",
        "update.preparing": "Preparing download…",
        "update.downloading": "Downloading… {pct} %",
        "update.success": "Update installed. Please restart the application.",
        "update.failed": "Update failed. Please try again later.",
        "update.available_title": "Update available",
        "update.available_msg": "A newer version of yt-dlp is available:\n\n  Current:    {current}\n  Available:  {available}\n\nDownload and install now?",
        "update.install_confirm_title": "Install update",
        "update.install_confirm_msg": "Download yt-dlp {version} now?",
        "update.check_title": "Update check",
        "update.check_failed": "Could not determine the latest version. Please check your internet connection.",
        "update.check_uptodate": "yt-dlp is up to date ({version}).",
        "update.section_title": "yt-dlp updates",
        "update.auto_check_label": "Check for updates automatically on start",
        "update.check_now": "Check for updates now",
        "update.clear_override": "Remove override",
        "update.no_override": "No override is active.",
        "update.clear_confirm_title": "Remove override",
        "update.clear_confirm_msg": "This will revert to the bundled yt-dlp version.\nPlease restart the application afterwards.\n\nContinue?",
        "update.clear_done": "Override removed. Please restart.",
        "update.clear_failed": "Could not remove the override.",

        "about.info_block": "Author:   {author}\nLicense:  {license} ({year})\nBackend:  yt-dlp {ytdlp}",
        "about.disclaimer": "Use at your own risk.\nOnly download content you have the right\nto download.",
        "about.ytdlp_bundled": " (bundled)",
        "about.ytdlp_updated": " (updated)",

        "dialog.hint": "Notice",
        "dialog.error": "Error",
        "dialog.done": "Done",
        "dialog.missing_url": "Please enter a YouTube URL.",
        "dialog.invalid_url": "The URL does not look like a valid web address.",
        "dialog.missing_target": "Please choose a target folder.",
        "dialog.target_create_failed": "Could not create target folder:\n{err}",
        "dialog.no_ffmpeg_title": "ffmpeg not found",
        "dialog.no_ffmpeg_msg": "No ffmpeg installation was found.\n\nPlease install ffmpeg or place ffmpeg(.exe) into the program folder.\n\nWithout ffmpeg, audio conversion is not possible.",
        "dialog.no_ffmpeg_short": "ffmpeg was not found. Please install it or place ffmpeg(.exe) into the program folder.",

        "log.start_download": "▶  Starting download",
        "log.url_line": "    URL:      {url}",
        "log.format_line": "    Format:   {fmt}",
        "log.target_line": "    Target:   {target}",
        "log.ffmpeg_line": "    ffmpeg:   {path}",
        "log.ytdlp_line": "    yt-dlp:   {version}{override}",
        "log.override_marker": " (override)",
        "log.detected": "▶  Detected as: {kind}",
        "log.kind_playlist": "Playlist",
        "log.kind_single": "Single video",
        "log.downloaded": "✓  Downloaded: {filename}",
        "log.all_done": "\n✓  All downloads completed.",
        "log.cancelled": "\n⏹  Download cancelled.",
        "log.cancelled_by_user": "\n⏹  Download cancelled by user.",
        "log.error": "\n✗  Error: {err}",
        "log.cancel_requested": "⏹  Cancel requested — current file will finish first…",
        "log.playlist_probe_failed": "⚠  Playlist probe via API failed, using URL heuristic. ({err})",
        "log.update_available": "⚙  New yt-dlp version available: {version}",
        "log.update_done": "✓  yt-dlp updated. Please restart the application to load the new version.",
        "log.cover_saved": "Cover saved: {folder}/",
        "log.format_flac": "FLAC 24-bit (lossless)",
        "log.format_mp3": "MP3 320 kbps",
    },
}

SUPPORTED_LANGS = ("de", "en")


def detect_system_lang() -> str:
    """System-Locale lesen — falls Deutsch, 'de', sonst Default 'en'."""
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.lower().startswith("de"):
            return "de"
    except Exception:
        pass
    return "en"


class Translator:
    def __init__(self, lang: str = "en"):
        self.lang = lang if lang in SUPPORTED_LANGS else "en"

    def set_lang(self, lang: str):
        if lang in SUPPORTED_LANGS:
            self.lang = lang

    def t(self, key: str, **kwargs) -> str:
        value = TRANSLATIONS.get(self.lang, {}).get(key)
        if value is None:
            # Fallback auf Englisch, dann auf den Key selbst
            value = TRANSLATIONS["en"].get(key, key)
        if kwargs:
            try:
                value = value.format(**kwargs)
            except (KeyError, IndexError):
                pass  # bei kaputtem Template lieber den Rohtext zeigen
        return value
