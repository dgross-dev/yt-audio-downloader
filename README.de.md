# YouTube Audio Downloader

GUI zum Herunterladen von YouTube-Videos und ‑Playlists als
**FLAC (24 Bit)** oder **MP3 (320 kbps)**. Windows + Linux, deutsch + englisch.

**Autor:** David Christopher Groß · **Lizenz:** MIT (siehe `LICENSE`)

---

## ⚠ Wichtiger Hinweis zur Audioqualität

YouTube liefert Audio grundsätzlich **verlustbehaftet** aus — typischerweise
Opus mit ca. **160 kbps** (premium) oder AAC mit ca. **128 kbps**. Eine echte
Hi-Res-Quelle existiert dort **nicht**.

Was das Programm macht: Es zieht den besten verfügbaren Stream und packt
ihn verlustfrei in einen 24-Bit-FLAC-Container. Damit geht ab dem Download
nichts mehr verloren — die ursprüngliche YouTube-Qualität bleibt aber die
Obergrenze. Es ist nicht dasselbe wie 24-Bit-Studio-Master.

| Format | Verlustfrei ab Download? | Echte Studio-Qualität? |
|---|---|---|
| FLAC (24 Bit) | Ja | Nein — Quelle ist lossy |
| MP3 (320 kbps) | Nein, erneut komprimiert | Nein |

Wer echte Hi-Res-Qualität will: **Qobuz, Tidal Max, Bandcamp** o. Ä.
Für YouTube-Inhalte (Bootlegs, eigene Uploads, Demos, Mixe) ist FLAC 24-Bit
hier die qualitativ beste Lösung.

---

## Funktionen

- Einzelne YouTube-Videos und komplette Playlists
- FLAC verlustfrei (24-Bit-Container) oder MP3 320 kbps CBR
- Cover wird ins Audio eingebettet und zusätzlich als `cover.jpg` + `folder.jpg` im Zielordner abgelegt
- Keine WebP/PNG-Reste — Thumbnails werden zu JPG konvertiert und nach dem Embedden aufgeräumt
- Metadaten (Titel, Künstler, …) werden gesetzt
- Standard-Zielordner: `<Downloads>/YT-Music`
- **ffmpeg ist in der EXE gebündelt** — keine externe Installation nötig
- Automatischer yt-dlp-Update-Check beim Programmstart
- Deutsche und englische Bedienoberfläche, in der App umschaltbar
- Playlist-Tracks landen in einem Unterordner mit Playlist-Titel, durchnummeriert
- Live-Fortschritt, Abbrechen jederzeit möglich

---

## Self-contained EXE — was wirklich enthalten ist

Mit dem mitgelieferten `build.bat` entstehen EXEs, die **alles** beinhalten,
was zum Betrieb nötig ist:

- ✔ Python-Laufzeitumgebung
- ✔ alle Python-Bibliotheken (yt-dlp, customtkinter, Pillow, urllib, …)
- ✔ **ffmpeg** (LGPL-Build von BtbN, ca. 80 MB)
- ✔ App-Icon, Übersetzungen, Logo (programmatisch erzeugt)

**Größe der EXE:** ca. **100–130 MB** (mit gebündeltem ffmpeg).
Ohne ffmpeg-Bundle wären es ~35 MB.

Auf dem Zielrechner wird **nichts** zusätzlich gebraucht außer:
- Internetzugriff (für yt-dlp-Downloads und den Update-Check)
- Schreibrechte auf `%LOCALAPPDATA%` (Standard auf jedem Windows-User-Profil)

Beim ersten Start zeigt Windows Defender SmartScreen ggf. eine Warnung
(„Unbekannter Herausgeber") — normal bei selbst gebauten EXEs ohne Code-Signing.

---

## Standard-Download-Pfad

| Plattform | Pfad |
|---|---|
| Windows | `%USERPROFILE%\Downloads\YT-Music` (auch bei umgeleitetem Downloads-Ordner korrekt) |
| Linux | `~/Downloads/YT-Music` (bzw. `$XDG_DOWNLOAD_DIR/YT-Music`) |
| macOS | `~/Downloads/YT-Music` |

Der Pfad lässt sich in der App pro Download individuell ändern.

---

## Mehrsprachigkeit

Zwei vorkonfigurierte Builds:

| EXE | Default-Sprache |
|---|---|
| `YouTubeAudioDownloader-DE.exe` | Deutsch |
| `YouTubeAudioDownloader-EN.exe` | Englisch |

Die Sprache kann in der App jederzeit über **„Über" → „Sprache"** umgeschaltet
werden. Die Auswahl wird pro Benutzer in `%LOCALAPPDATA%\YouTubeAudioDownloader\config.json`
gespeichert.

---

## yt-dlp Auto-Update

YouTube ändert regelmäßig interne API-Strukturen — yt-dlp muss daher auch
regelmäßig aktualisiert werden, sonst brechen Downloads.

- **Erkennung:** Beim Start vergleicht die App die geladene yt-dlp-Version mit der neuesten auf PyPI
- **Installation:** Auf Bestätigung wird das aktualisierte yt-dlp ins User-Verzeichnis entpackt; beim nächsten Programmstart automatisch geladen
- **Funktioniert in beiden Distributionen** (Python-Modus und EXE)
- **Keine Admin-Rechte nötig**
- **Toggle im Über-Dialog**
- **Rollback** über „Override entfernen"

---

## EXE bauen

### Windows
```bat
build.bat
```

Was passiert:
1. `.venv` wird angelegt (falls noch nicht da)
2. **ffmpeg wird automatisch heruntergeladen** (LGPL-Build von BtbN, ~50 MB Download).
   Wird im Ordner `ffmpeg-bundled/` zwischengespeichert; bei späteren Builds nicht erneut geladen.
3. PyInstaller baut zwei EXEs (DE + EN) mit allen Komponenten inkl. ffmpeg
4. Ergebnis:
   - `dist\YouTubeAudioDownloader-DE.exe`
   - `dist\YouTubeAudioDownloader-EN.exe`

Wenn der ffmpeg-Download fehlschlägt (z. B. kein Internet), läuft der Build
trotzdem durch — die EXE braucht dann ein externes ffmpeg im selben Ordner.

### Linux
```bash
./build.sh
```
Lädt statischen ffmpeg-Build von johnvansickle.com und bündelt ihn analog.

---

## Schnellstart (ohne Build)

Voraussetzungen: **Python ≥ 3.10** und **ffmpeg**.

### Windows
```bat
run.bat
```

### Linux
```bash
chmod +x run.sh
./run.sh
```

Beim ersten Start wird automatisch eine `.venv` angelegt und alle
Abhängigkeiten installiert. Im Python-Modus muss ffmpeg im PATH oder
neben dem Skript vorhanden sein (siehe unten).

---

## ffmpeg manuell installieren (nur für Python-Modus oder bei Build ohne Bundle)

### Windows (portabel, ohne Admin)
1. Statisches Build von <https://www.gyan.dev/ffmpeg/builds/> oder
   <https://github.com/BtbN/FFmpeg-Builds> herunterladen.
2. `ffmpeg.exe` direkt neben das Skript bzw. die EXE legen.

### Linux
```bash
sudo apt install ffmpeg          # Debian/Ubuntu
sudo dnf install ffmpeg          # Fedora
```

---

## Lizenz und Drittsoftware

Eigener Code steht unter der MIT-Lizenz (siehe `LICENSE`).

Die gebündelten Drittkomponenten — insbesondere ffmpeg (LGPL-2.1) und
yt-dlp (Unlicense) — behalten ihre jeweilige Lizenz. Details und
Quellen-Verweise: siehe `THIRD_PARTY_LICENSES.txt`.

**Kurz zur ffmpeg-LGPL:** Wir bündeln einen unmodifizierten LGPL-Build und
rufen ffmpeg als externes Programm auf — d. h. ffmpeg ist nicht in den
Anwendungs-Code linked, sondern wird per Prozess-Aufruf genutzt.
Source-Code von ffmpeg ist über die Upstream-URL frei verfügbar.

---

## Android?

Keine eigene Portierung. Empfohlen (Open Source, via F-Droid):

- **Seal** — [github.com/JunkFood02/Seal](https://github.com/JunkFood02/Seal)
- **YTDLnis** — [github.com/deniscerri/ytdlnis](https://github.com/deniscerri/ytdlnis)
- **NewPipe** — [newpipe.net](https://newpipe.net/)

---

## Rechtliches (Inhalte)

Nutzung in **eigener Verantwortung**. Empfohlen für:

- Eigene Uploads
- Inhalte unter freien Lizenzen (CC, Public Domain)
- Inhalte, an denen du selbst Rechte hältst

---

## Projekt-Struktur

```
yt-audio-downloader/
├── youtube_audio_downloader.py   # Hauptprogramm
├── app_logo.py                   # Logo-Generator
├── updater.py                    # yt-dlp Auto-Update
├── i18n.py                       # Übersetzungen DE/EN
├── paths.py                      # Plattformpfade
├── build_config.py               # Build-Default-Sprache
├── bundle_ffmpeg.py              # ffmpeg-Download für Build
├── requirements.txt
├── run.bat / run.sh              # direkter Start
├── build.bat / build.sh          # EXE-Build (mit ffmpeg-Bundling)
├── LICENSE                       # MIT (eigener Code)
├── THIRD_PARTY_LICENSES.txt      # Drittsoftware (ffmpeg, yt-dlp, ...)
└── README.md
```

---

## Fehlerbehebung

| Problem | Lösung |
|---|---|
| HTTP 403 / Format-Fehler | „Updates suchen" im Über-Dialog → yt-dlp aktualisieren |
| Update-Check schlägt fehl (Corporate-Proxy) | `HTTPS_PROXY`-Env-Variable setzen, oder Auto-Check deaktivieren |
| Override macht Probleme | Über-Dialog → „Override entfernen" → neu starten |
| Windows SmartScreen-Warnung | „Weitere Informationen" → „Trotzdem ausführen" (normal bei selbst gebauten EXEs) |
| ffmpeg-Download im Build fehlgeschlagen | Internet prüfen; alternativ `ffmpeg.exe` manuell in `ffmpeg-bundled/` ablegen |
| GUI startet nicht (Linux) | `sudo apt install python3-tk` |
