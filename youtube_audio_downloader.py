# YouTube Audio Downloader
# David Christopher Groß, 2026 — MIT
#
# Lädt YouTube-Videos und -Playlists als FLAC (24-Bit) oder MP3 (320 CBR)
# herunter. Cover wird ins Audio eingebettet und zusätzlich als
# cover.jpg / folder.jpg im Zielordner abgelegt. Temporäre Thumbnail-
# Dateien werden aufgeräumt.
from __future__ import annotations

# Reihenfolge der ersten Imports nicht ändern.
# updater.setup_override() MUSS vor `import yt_dlp` laufen, damit eine
# evtl. installierte neuere yt-dlp-Version aus dem User-Verzeichnis statt
# der gebundelten geladen wird.
import updater
updater.setup_override()

import os
import re
import sys
import shutil
import queue
import threading
import traceback
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk
import yt_dlp
from yt_dlp.postprocessor import PostProcessor

from app_logo import make_logo
from i18n import Translator, detect_system_lang, SUPPORTED_LANGS
from paths import default_target_dir
from build_config import BUILD_DEFAULT_LANG


VERSION = "1.4.0"
AUTHOR = "David Christopher Groß"
YEAR = "2026"
LICENSE = "MIT"
REPO_URL = ""


# ---- Helfer ---------------------------------------------------------------

def locate_ffmpeg():
    """ffmpeg finden — bevorzugt im Programmordner, sonst PATH."""
    here = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    for name in ("ffmpeg.exe", "ffmpeg"):
        p = here / name
        if p.exists():
            return str(p)
    return shutil.which("ffmpeg")


def sanitize_url(url: str) -> str:
    return (url or "").strip()


def resolve_initial_lang(config: dict) -> str:
    """Entscheidet die zu verwendende Sprache beim Start:
       1) im Config gespeicherte User-Präferenz, sonst
       2) Build-Default (durch Build-Skript gesetzt), sonst
       3) System-Locale."""
    if config.get("language") in SUPPORTED_LANGS:
        return config["language"]
    if BUILD_DEFAULT_LANG in SUPPORTED_LANGS:
        return BUILD_DEFAULT_LANG
    return detect_system_lang()


# ---- Cover-Postprocessor --------------------------------------------------

class CoverArtSaver(PostProcessor):
    """Legt das eingebettete Cover als cover.jpg + folder.jpg im
    Audio-Verzeichnis ab und entsorgt anschließend die einzelne
    Thumbnail-Datei, die yt-dlp angelegt hat."""

    def __init__(self, translator: Translator = None):
        super().__init__()
        self._t = translator or Translator("en")

    def run(self, info):
        audio = info.get("filepath")
        if not audio or not os.path.isfile(audio):
            return [], info

        candidates = []
        for t in (info.get("thumbnails") or []):
            fp = t.get("filepath")
            if fp and os.path.isfile(fp):
                candidates.append(fp)

        candidates.sort(key=lambda p: (0 if p.lower().endswith((".jpg", ".jpeg")) else 1))

        target_dir = os.path.dirname(audio)
        cover_jpg = os.path.join(target_dir, "cover.jpg")
        folder_jpg = os.path.join(target_dir, "folder.jpg")

        if candidates:
            src = candidates[0]
            try:
                shutil.copyfile(src, cover_jpg)
                shutil.copyfile(src, folder_jpg)
                self.to_screen(self._t.t("log.cover_saved", folder=os.path.basename(target_dir)))
            except OSError as e:
                self.report_warning(f"Could not save cover: {e}")

        for fp in candidates:
            base = os.path.basename(fp).lower()
            if base in ("cover.jpg", "folder.jpg"):
                continue
            try:
                os.remove(fp)
            except OSError:
                pass

        stem = os.path.splitext(audio)[0]
        for ext in (".webp", ".png", ".jpg", ".jpeg"):
            stray = stem + ext
            if os.path.isfile(stray) and os.path.basename(stray).lower() not in ("cover.jpg", "folder.jpg"):
                try:
                    os.remove(stray)
                except OSError:
                    pass

        return [], info


# ---- Update-Dialog --------------------------------------------------------

class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, target_version: str, translator: Translator, on_done):
        super().__init__(parent)
        self._t = translator
        self.title(self._t.t("update.dialog_title"))
        self.geometry("440x220")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._on_done = on_done
        self._success = False
        self._target = target_version

        ctk.CTkLabel(self, text=self._t.t("update.dialog_header", version=target_version),
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(22, 6))
        self._status = ctk.CTkLabel(self, text=self._t.t("update.preparing"),
                                    text_color="gray70")
        self._status.pack(pady=(0, 12))

        self._progress = ctk.CTkProgressBar(self, height=14)
        self._progress.pack(fill="x", padx=30, pady=(0, 16))
        self._progress.set(0)

        self._close_btn = ctk.CTkButton(self, text=self._t.t("ui.close"), width=120,
                                        state="disabled", command=self._close)
        self._close_btn.pack(pady=(4, 16))

        threading.Thread(target=self._run_install, daemon=True).start()

    def _run_install(self):
        def progress(f):
            self.after(0, self._progress.set, f)
            self.after(0, self._status.configure,
                       {"text": self._t.t("update.downloading", pct=int(f * 100))})

        ok = updater.install_update(self._target, progress_cb=progress)
        self.after(0, self._finish, ok)

    def _finish(self, ok: bool):
        self._success = ok
        if ok:
            self._status.configure(text=self._t.t("update.success"),
                                   text_color=("#0a7c00", "#7ed957"))
            self._progress.set(1.0)
        else:
            self._status.configure(text=self._t.t("update.failed"),
                                   text_color=("#a50000", "#ff6464"))
        self._close_btn.configure(state="normal")

    def _close(self):
        if self._on_done:
            self._on_done(self._success)
        self.destroy()


# ---- About-Fenster --------------------------------------------------------

class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent, logo, app_ref):
        super().__init__(parent)
        self._app = app_ref
        self._t = app_ref.t
        self.title(self._t.t("ui.about"))
        self.geometry("480x540")
        self.resizable(False, False)

        ctk.CTkLabel(self, image=logo, text="").pack(pady=(18, 5))
        ctk.CTkLabel(self, text="YouTube Audio Downloader",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(5, 0))
        ctk.CTkLabel(self, text=f"Version {VERSION}",
                     font=ctk.CTkFont(size=12), text_color="gray70").pack(pady=(0, 12))

        ydl_ver = updater.get_current_yt_dlp_version()
        suffix = self._t.t("about.ytdlp_updated") if updater.is_override_active() \
                 else self._t.t("about.ytdlp_bundled")
        info = self._t.t("about.info_block",
                         author=AUTHOR, license=LICENSE, year=YEAR,
                         ytdlp=ydl_ver + suffix)
        ctk.CTkLabel(self, text=info, font=ctk.CTkFont(family="Consolas", size=11),
                     justify="left").pack(pady=(0, 8), padx=20)

        # Language switcher
        lang_card = ctk.CTkFrame(self)
        lang_card.pack(fill="x", padx=20, pady=(4, 6))
        ctk.CTkLabel(lang_card, text=self._t.t("ui.language"),
                     font=ctk.CTkFont(size=12, weight="bold")
                     ).pack(anchor="w", padx=12, pady=(10, 4))
        lang_row = ctk.CTkFrame(lang_card, fg_color="transparent")
        lang_row.pack(fill="x", padx=12, pady=(0, 10))
        self._lang_var = ctk.StringVar(value=self._app.lang)
        ctk.CTkRadioButton(lang_row, text="Deutsch", variable=self._lang_var,
                           value="de", command=self._change_lang
                           ).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(lang_row, text="English", variable=self._lang_var,
                           value="en", command=self._change_lang
                           ).pack(side="left")

        # Update-Sektion
        upd_card = ctk.CTkFrame(self)
        upd_card.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(upd_card, text=self._t.t("update.section_title"),
                     font=ctk.CTkFont(size=12, weight="bold")
                     ).pack(anchor="w", padx=12, pady=(10, 4))

        self._auto_var = ctk.BooleanVar(value=self._app.config.get("auto_check_updates", True))
        ctk.CTkCheckBox(upd_card, text=self._t.t("update.auto_check_label"),
                        variable=self._auto_var, command=self._toggle_auto
                        ).pack(anchor="w", padx=12, pady=(0, 8))

        btn_row = ctk.CTkFrame(upd_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(btn_row, text=self._t.t("update.check_now"), width=210,
                      command=self._check_now).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text=self._t.t("update.clear_override"), width=160,
                      fg_color="transparent", border_width=1,
                      text_color=("gray10", "gray90"),
                      command=self._clear_override).pack(side="left")

        ctk.CTkLabel(self, text=self._t.t("about.disclaimer"),
                     font=ctk.CTkFont(size=10),
                     text_color="gray60", justify="center"
                     ).pack(pady=(4, 10), padx=20)

        ctk.CTkButton(self, text=self._t.t("ui.close"), width=120,
                      command=self.destroy).pack(pady=(0, 16))

        self.transient(parent)
        self.grab_set()

    def _change_lang(self):
        new_lang = self._lang_var.get()
        self._app.set_language(new_lang)
        # About-Fenster zumachen — wird neu geöffnet wenn nötig
        self.destroy()

    def _toggle_auto(self):
        self._app.config["auto_check_updates"] = self._auto_var.get()
        updater.save_config(self._app.config)

    def _check_now(self):
        self._app.check_for_updates(silent=False, parent=self)

    def _clear_override(self):
        if not updater.is_override_active():
            messagebox.showinfo(self._t.t("dialog.hint"),
                                self._t.t("update.no_override"),
                                parent=self)
            return
        confirmed = messagebox.askyesno(
            self._t.t("update.clear_confirm_title"),
            self._t.t("update.clear_confirm_msg"),
            parent=self)
        if confirmed:
            if updater.clear_override():
                messagebox.showinfo(self._t.t("dialog.done"),
                                    self._t.t("update.clear_done"),
                                    parent=self)
            else:
                messagebox.showerror(self._t.t("dialog.error"),
                                     self._t.t("update.clear_failed"),
                                     parent=self)


# ---- Hauptfenster ---------------------------------------------------------

class App:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.config = updater.load_config()
        self.lang = resolve_initial_lang(self.config)
        self.t = Translator(self.lang)

        target = default_target_dir()
        target.mkdir(parents=True, exist_ok=True)

        self.root = ctk.CTk()
        self.root.title(self.t.t("app.window_title", version=VERSION))
        self.root.geometry("780x720")
        self.root.minsize(660, 580)

        self._setup_logo()

        # State
        self.target_dir = ctk.StringVar(value=str(target))
        self.fmt = ctk.StringVar(value="flac24")
        self.busy = False
        self.cancel = threading.Event()
        self.msg_queue: queue.Queue = queue.Queue()
        self.ffmpeg = locate_ffmpeg()
        self._update_available_version: str | None = None

        # Widgets, deren Texte bei Sprachwechsel neu gesetzt werden müssen
        self._localized_widgets: list[tuple] = []

        self._build_ui()
        self._pump_queue()

        if not self.ffmpeg:
            self.root.after(300, self._warn_no_ffmpeg)

        if self.config.get("auto_check_updates", True):
            self.root.after(800, lambda: self.check_for_updates(silent=True))

    def _warn_no_ffmpeg(self):
        messagebox.showwarning(
            self.t.t("dialog.no_ffmpeg_title"),
            self.t.t("dialog.no_ffmpeg_msg"))

    def _setup_logo(self):
        self._logo_header_img = make_logo(64)
        self._logo_about_img = make_logo(96)
        self.logo_header = ctk.CTkImage(light_image=self._logo_header_img,
                                        dark_image=self._logo_header_img, size=(64, 64))
        self.logo_about = ctk.CTkImage(light_image=self._logo_about_img,
                                       dark_image=self._logo_about_img, size=(96, 96))
        try:
            self._tk_icon = ImageTk.PhotoImage(self._logo_header_img)
            self.root.iconphoto(True, self._tk_icon)
        except Exception:
            pass

    # ----- Sprache ----------------------------------------------------------

    def _register(self, widget, key, **kwargs):
        """Widget registrieren, damit es bei Sprachwechsel neu beschriftet wird.
        kwargs werden an t() weitergegeben (z.B. format-args)."""
        self._localized_widgets.append((widget, key, kwargs))

    def set_language(self, new_lang: str):
        if new_lang not in SUPPORTED_LANGS or new_lang == self.lang:
            return
        self.lang = new_lang
        self.t.set_lang(new_lang)
        self.config["language"] = new_lang
        updater.save_config(self.config)
        self._apply_language()

    def _apply_language(self):
        """Alle registrierten Widgets neu beschriften."""
        self.root.title(self.t.t("app.window_title", version=VERSION))
        for widget, key, kwargs in self._localized_widgets:
            try:
                widget.configure(text=self.t.t(key, **kwargs))
            except Exception:
                pass

        # spezielle Widgets, die nicht 'text' sondern 'placeholder_text' haben
        try:
            self.url_entry.configure(placeholder_text=self.t.t("ui.url_placeholder"))
        except Exception:
            pass

        # Update-Pille ggf. neu beschriften
        if self._update_available_version:
            self.update_pill.configure(
                text=self.t.t("update.pill", version=self._update_available_version))

    # ----- UI ---------------------------------------------------------------

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.root, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 5))
        ctk.CTkLabel(header, image=self.logo_header, text="").pack(side="left", padx=(0, 14))

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(titles, text="YouTube Audio Downloader",
                     font=ctk.CTkFont(size=22, weight="bold"), anchor="w"
                     ).pack(anchor="w")
        subtitle = ctk.CTkLabel(titles, text=self.t.t("app.subtitle"),
                                font=ctk.CTkFont(size=12), text_color="gray70", anchor="w")
        subtitle.pack(anchor="w", pady=(2, 0))
        self._register(subtitle, "app.subtitle")

        # Update-Pille
        self.update_pill = ctk.CTkButton(
            header, text=self.t.t("update.pill_generic"),
            width=140, height=30,
            fg_color=("#0a7c00", "#1b8f0c"),
            hover_color=("#0e9100", "#22a013"),
            command=self._on_update_pill_click)

        about_btn = ctk.CTkButton(header, text=self.t.t("ui.about"), width=70, height=30,
                                  fg_color="transparent", border_width=1,
                                  text_color=("gray10", "gray90"),
                                  command=self._open_about)
        about_btn.pack(side="right", padx=(10, 0))
        self._register(about_btn, "ui.about")

        # URL
        url_card = ctk.CTkFrame(self.root)
        url_card.pack(fill="x", padx=20, pady=(15, 6))
        url_label = ctk.CTkLabel(url_card, text=self.t.t("ui.url_label"), anchor="w",
                                 font=ctk.CTkFont(size=12, weight="bold"))
        url_label.pack(fill="x", padx=15, pady=(12, 4))
        self._register(url_label, "ui.url_label")

        self.url_entry = ctk.CTkEntry(
            url_card, placeholder_text=self.t.t("ui.url_placeholder"), height=36)
        self.url_entry.pack(fill="x", padx=15, pady=(0, 14))

        # Format
        fmt_card = ctk.CTkFrame(self.root)
        fmt_card.pack(fill="x", padx=20, pady=6)
        fmt_label = ctk.CTkLabel(fmt_card, text=self.t.t("ui.format_label"), anchor="w",
                                 font=ctk.CTkFont(size=12, weight="bold"))
        fmt_label.pack(fill="x", padx=15, pady=(12, 4))
        self._register(fmt_label, "ui.format_label")

        row = ctk.CTkFrame(fmt_card, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(0, 14))
        flac_rb = ctk.CTkRadioButton(row, text=self.t.t("format.flac"),
                                     variable=self.fmt, value="flac24")
        flac_rb.pack(side="left", padx=(0, 25))
        self._register(flac_rb, "format.flac")

        mp3_rb = ctk.CTkRadioButton(row, text=self.t.t("format.mp3"),
                                    variable=self.fmt, value="mp3")
        mp3_rb.pack(side="left")
        self._register(mp3_rb, "format.mp3")

        # Zielordner
        path_card = ctk.CTkFrame(self.root)
        path_card.pack(fill="x", padx=20, pady=6)
        path_label = ctk.CTkLabel(path_card, text=self.t.t("ui.target_label"), anchor="w",
                                  font=ctk.CTkFont(size=12, weight="bold"))
        path_label.pack(fill="x", padx=15, pady=(12, 4))
        self._register(path_label, "ui.target_label")

        prow = ctk.CTkFrame(path_card, fg_color="transparent")
        prow.pack(fill="x", padx=15, pady=(0, 14))
        ctk.CTkEntry(prow, textvariable=self.target_dir, height=36
                     ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        browse_btn = ctk.CTkButton(prow, text=self.t.t("ui.browse"), width=130, height=36,
                                   command=self._pick_folder)
        browse_btn.pack(side="right")
        self._register(browse_btn, "ui.browse")

        # Action-Buttons
        btn_row = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(14, 5))
        self.btn_download = ctk.CTkButton(btn_row, text=self.t.t("ui.start_download"),
                                          height=46,
                                          font=ctk.CTkFont(size=15, weight="bold"),
                                          command=self._start)
        self.btn_download.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._register(self.btn_download, "ui.start_download")

        self.btn_cancel = ctk.CTkButton(btn_row, text=self.t.t("ui.cancel"),
                                        height=46, width=130,
                                        fg_color="#8b0000", hover_color="#a50000",
                                        state="disabled", command=self._request_cancel)
        self.btn_cancel.pack(side="right")
        self._register(self.btn_cancel, "ui.cancel")

        # Progress + Status
        self.progress = ctk.CTkProgressBar(self.root, height=14)
        self.progress.pack(fill="x", padx=20, pady=(10, 4))
        self.progress.set(0)
        self.status = ctk.CTkLabel(self.root, text=self.t.t("status.ready"),
                                   text_color="gray70", anchor="w")
        self.status.pack(fill="x", padx=22, pady=(0, 6))
        self._register(self.status, "status.ready")

        # Protokoll
        log_card = ctk.CTkFrame(self.root)
        log_card.pack(fill="both", expand=True, padx=20, pady=(4, 12))
        log_label = ctk.CTkLabel(log_card, text=self.t.t("ui.log_label"), anchor="w",
                                 font=ctk.CTkFont(size=12, weight="bold"))
        log_label.pack(fill="x", padx=15, pady=(10, 4))
        self._register(log_label, "ui.log_label")
        self.log = ctk.CTkTextbox(log_card, font=ctk.CTkFont(family="Consolas", size=11))
        self.log.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        # Footer
        ctk.CTkLabel(self.root,
                     text=f"© {YEAR}  {AUTHOR}   ·   {LICENSE} License",
                     font=ctk.CTkFont(size=10), text_color="gray50"
                     ).pack(pady=(0, 10))

    # ----- Update-Logik ----------------------------------------------------

    def check_for_updates(self, silent: bool = True, parent=None):
        threading.Thread(target=self._check_update_thread,
                         args=(silent, parent), daemon=True).start()

    def _check_update_thread(self, silent: bool, parent):
        info = updater.fetch_latest_info()
        latest = updater.latest_version(info)
        current = updater.get_current_yt_dlp_version()

        if not latest:
            if not silent:
                self.root.after(0, messagebox.showwarning,
                                self.t.t("update.check_title"),
                                self.t.t("update.check_failed"))
            return

        if updater.is_newer(latest, current):
            self._update_available_version = latest
            self.root.after(0, self._show_update_available, latest, silent, parent)
        else:
            if not silent:
                self.root.after(0, messagebox.showinfo,
                                self.t.t("update.check_title"),
                                self.t.t("update.check_uptodate", version=current))

        self.config["last_known_version"] = latest
        updater.save_config(self.config)

    def _show_update_available(self, version: str, silent: bool, parent):
        if not self.update_pill.winfo_ismapped():
            self.update_pill.pack(side="right", padx=(6, 0))
        self.update_pill.configure(text=self.t.t("update.pill", version=version))
        self._post("log", self.t.t("log.update_available", version=version))

        if silent:
            return

        answer = messagebox.askyesno(
            self.t.t("update.available_title"),
            self.t.t("update.available_msg",
                     current=updater.get_current_yt_dlp_version(),
                     available=version),
            parent=parent or self.root)
        if answer:
            UpdateDialog(self.root, version, self.t, on_done=self._after_update_install)

    def _on_update_pill_click(self):
        if not self._update_available_version:
            return
        if messagebox.askyesno(
                self.t.t("update.install_confirm_title"),
                self.t.t("update.install_confirm_msg",
                         version=self._update_available_version),
                parent=self.root):
            UpdateDialog(self.root, self._update_available_version, self.t,
                         on_done=self._after_update_install)

    def _after_update_install(self, success: bool):
        if success:
            self.update_pill.pack_forget()
            self._post("log", self.t.t("log.update_done"))
            self.status.configure(text=self.t.t("status.update_installed"))

    # ----- Queue / Threading -----------------------------------------------

    def _pump_queue(self):
        try:
            while True:
                kind, payload = self.msg_queue.get_nowait()
                if kind == "log":
                    self.log.insert("end", payload + "\n")
                    self.log.see("end")
                elif kind == "status":
                    self.status.configure(text=payload)
                elif kind == "progress":
                    self.progress.set(max(0.0, min(1.0, payload)))
                elif kind == "done":
                    self._after_download(payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(80, self._pump_queue)

    def _post(self, kind, payload=""):
        self.msg_queue.put((kind, payload))

    # ----- Actions ---------------------------------------------------------

    def _pick_folder(self):
        d = filedialog.askdirectory(initialdir=self.target_dir.get())
        if d:
            self.target_dir.set(d)

    def _open_about(self):
        AboutWindow(self.root, self.logo_about, self)

    def _request_cancel(self):
        if self.busy:
            self.cancel.set()
            self._post("log", self.t.t("log.cancel_requested"))
            self._post("status", self.t.t("status.cancelling"))

    def _start(self):
        if self.busy:
            return
        url = sanitize_url(self.url_entry.get())
        if not url:
            messagebox.showwarning(self.t.t("dialog.hint"),
                                   self.t.t("dialog.missing_url"))
            return
        if not re.search(r"https?://", url):
            messagebox.showwarning(self.t.t("dialog.hint"),
                                   self.t.t("dialog.invalid_url"))
            return

        path = self.target_dir.get().strip()
        if not path:
            messagebox.showwarning(self.t.t("dialog.hint"),
                                   self.t.t("dialog.missing_target"))
            return
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror(self.t.t("dialog.error"),
                                 self.t.t("dialog.target_create_failed", err=str(e)))
            return

        if not self.ffmpeg:
            messagebox.showerror(self.t.t("dialog.no_ffmpeg_title"),
                                 self.t.t("dialog.no_ffmpeg_short"))
            return

        self.busy = True
        self.cancel.clear()
        self.btn_download.configure(state="disabled", text=self.t.t("ui.downloading"))
        self.btn_cancel.configure(state="normal")
        self.log.delete("1.0", "end")
        self.progress.set(0)

        threading.Thread(target=self._worker,
                         args=(url, path, self.fmt.get()),
                         daemon=True).start()

    def _after_download(self, ok: bool):
        self.busy = False
        self.btn_download.configure(state="normal", text=self.t.t("ui.start_download"))
        self.btn_cancel.configure(state="disabled")
        if ok:
            self.progress.set(1.0)
            self.status.configure(text=self.t.t("status.done"))
        else:
            self.status.configure(text=self.t.t("status.ended"))

    # ----- Download-Worker -------------------------------------------------

    def _worker(self, url: str, target: str, fmt: str):
        try:
            fmt_label = self.t.t("log.format_flac") if fmt == "flac24" else self.t.t("log.format_mp3")
            self._post("log", self.t.t("log.start_download"))
            self._post("log", self.t.t("log.url_line", url=url))
            self._post("log", self.t.t("log.format_line", fmt=fmt_label))
            self._post("log", self.t.t("log.target_line", target=target))
            self._post("log", self.t.t("log.ffmpeg_line", path=self.ffmpeg))
            override_marker = self.t.t("log.override_marker") if updater.is_override_active() else ""
            self._post("log", self.t.t("log.ytdlp_line",
                                       version=updater.get_current_yt_dlp_version(),
                                       override=override_marker))
            self._post("log", "")

            is_pl = self._probe_playlist(url)
            kind = self.t.t("log.kind_playlist") if is_pl else self.t.t("log.kind_single")
            self._post("log", self.t.t("log.detected", kind=kind) + "\n")

            opts = self._make_ydl_opts(target, fmt, is_pl)

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.add_post_processor(CoverArtSaver(self.t), when="post_process")
                ydl.download([url])

            if self.cancel.is_set():
                self._post("log", self.t.t("log.cancelled"))
                self._post("done", False)
            else:
                self._post("log", self.t.t("log.all_done"))
                self._post("done", True)

        except yt_dlp.utils.DownloadCancelled:
            self._post("log", self.t.t("log.cancelled_by_user"))
            self._post("done", False)
        except Exception as e:
            self._post("log", self.t.t("log.error", err=str(e)))
            self._post("log", traceback.format_exc())
            self._post("done", False)

    def _probe_playlist(self, url: str) -> bool:
        url_l = url.lower()
        url_indicates_pl = "playlist?list=" in url_l or "/playlist/" in url_l
        try:
            probe = yt_dlp.YoutubeDL({
                "quiet": True, "no_warnings": True,
                "extract_flat": True, "skip_download": True,
                "playlist_items": "1",
            })
            with probe:
                info = probe.extract_info(url, download=False)
            return bool(info and info.get("_type") == "playlist")
        except Exception as e:
            self._post("log", self.t.t("log.playlist_probe_failed", err=str(e)))
            return url_indicates_pl

    def _make_ydl_opts(self, target: str, fmt: str, is_playlist: bool) -> dict:
        if is_playlist:
            outtmpl = os.path.join(target, "%(playlist_title)s",
                                   "%(playlist_index)02d - %(title)s.%(ext)s")
        else:
            outtmpl = os.path.join(target, "%(title)s.%(ext)s")

        opts = {
            "outtmpl": outtmpl,
            "ignoreerrors": True,
            "ffmpeg_location": self.ffmpeg,
            "progress_hooks": [self._on_progress],
            "quiet": True,
            "no_warnings": False,
            "noprogress": True,
            "logger": self._logger(),
            "writethumbnail": True,
            "noplaylist": False,
        }

        # Postprocessor-Reihenfolge ist nicht egal:
        #   1. Audio extrahieren
        #   2. Thumbnail in JPG umwandeln (sonst WebP — manche Player mögen das nicht in FLAC)
        #   3. Metadaten setzen
        #   4. Thumbnail einbetten (already_have_thumbnail=True → File bleibt liegen,
        #      damit unser CoverArtSaver es danach noch als cover.jpg/folder.jpg übernehmen kann)
        pps = [
            {"key": "FFmpegExtractAudio",
             "preferredcodec": "flac" if fmt == "flac24" else "mp3",
             "preferredquality": "0" if fmt == "flac24" else "320"},
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg"},
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail", "already_have_thumbnail": True},
        ]

        if fmt == "flac24":
            opts["postprocessor_args"] = {
                "ffmpegextractaudio": ["-sample_fmt", "s32"],
            }

        opts["postprocessors"] = pps
        return opts

    # ----- yt-dlp Callbacks ------------------------------------------------

    def _on_progress(self, d):
        if self.cancel.is_set():
            raise yt_dlp.utils.DownloadCancelled()

        st = d.get("status")
        if st == "downloading":
            try:
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done = d.get("downloaded_bytes", 0)
                if total:
                    self._post("progress", done / total)

                spd = d.get("speed") or 0
                spd_s = f"{spd/1024/1024:5.2f} MB/s" if spd else "  …  "
                eta = d.get("eta")
                eta_s = f"{int(eta)}s" if eta else "—"

                info = d.get("info_dict") or {}
                title = info.get("title", "")
                idx = info.get("playlist_index")
                n = info.get("n_entries")
                prefix = f"[{idx}/{n}] " if idx and n else ""

                pct = int((done / total) * 100) if total else 0
                self._post("status", self.t.t("status.downloading_fmt",
                                              prefix=prefix, title=title[:55],
                                              pct=pct, speed=spd_s, eta=eta_s))
            except Exception:
                pass

        elif st == "finished":
            fn = d.get("filename", "")
            self._post("log", self.t.t("log.downloaded", filename=Path(fn).name))
            self._post("status", self.t.t("status.converting"))
            self._post("progress", 1.0)

    def _logger(self):
        app = self

        class _Log:
            def debug(self, msg):
                if not msg or msg.startswith("[debug] "):
                    return
                if msg.startswith("[download] Destination:"):
                    return
                if msg.startswith("[download]") and "%" in msg:
                    return
                app._post("log", msg)

            def info(self, msg):
                if msg:
                    app._post("log", msg)

            def warning(self, msg):
                if msg:
                    app._post("log", f"⚠  {msg}")

            def error(self, msg):
                if msg:
                    app._post("log", f"✗  {msg}")

        return _Log()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        App().run()
    except Exception:
        traceback.print_exc()
        input("Press any key to exit…")
