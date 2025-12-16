# Photobooth 2.0
Touch-optimierte Photobooth-Anwendung auf Basis von Python, PyQt6 und gPhoto2. Unterstützt DSLR (gPhoto2) oder Webcam, Collagen, Galerie mit Drucken/Löschen und arbeitet im Vollbild für Event-Setups.

## Features
- Touch-UI mit großen Buttons und Vollbild (PyQt6).
- Einzelbild und Collage-Workflow (optional mit PNG-Overlay).
- Kameraauswahl: bevorzugt DSLR via gPhoto2, Fallback auf Webcam (OpenCV).
- Galerie mit Grid-Ansicht, Detailansicht, Drucken und Löschen.
- Druck über das System-Backend (`lp`/CUPS); optionaler externer Bildschirm (Stub).

## Voraussetzungen
- Python 3.11+ empfohlen.
- System: Linux/macOS/Windows (DSLR benötigt gPhoto2 → primär Linux).
- Pakete (Python): `PyQt6`, `Pillow`, optional `opencv-python` (für Webcam).
- DSLR: `gphoto2` und `libgphoto2` installiert und auf `PATH`.
- Drucken: funktionierendes `lp`/CUPS-Setup, falls genutzt.

## Setup
```bash
git clone <dein-fork-oder-url>/photobooth_v2.git
cd photobooth_v2
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install PyQt6 Pillow opencv-python  # opencv optional, aber nötig für Webcam
```

## Starten
```bash
python -m photobooth2      # ruft photobooth2/main.py auf
```
Die App öffnet im Vollbild; oben rechts ist ein Schließen-Button, oben links ein Menü/Hamburger.

## Konfiguration
Datei: `photobooth2/config/settings.toml` (falls fehlt, werden Defaults genutzt und `output/` angelegt).
```toml
[event]
name = "Eure Fotobox"
date = "2024-12-31"
qr_url = "https://example.com/gallery"

[paths]
output_dir = "output"      # Speicherort für Fotos/Collagen

[collage]
photo_count = 4            # Anzahl Aufnahmen pro Collage
# overlay = "assets/floral_overlay.png"  # optionales PNG (RGBA), wird über Collage gelegt
```
- `output_dir` wird beim Start erzeugt, wenn nicht vorhanden.
- `photo_count` steuert die Collage-Schritte; >4 wird auf 4 begrenzt.
- `overlay`: optionaler Pfad zu einem PNG mit Alphakanal, das über die Collage gelegt wird.

## Verzeichnisstruktur
```
photobooth2/
├── main.py                 # Einstiegspunkt (python -m photobooth2)
├── config/loader.py        # Settings laden, Default-Ausgabeordner anlegen
├── controller/             # AppController verbindet UI mit Geräten/Features
├── devices/                # DSLR (gphoto2), Webcam (OpenCV), Printer (lp), ExternalDisplay stub
├── features/               # Single-Foto, Collage (Pillow), Galerie, Slideshow stub
└── ui/                     # Qt-Fenster, Screens, Dialoge, Assets
output/                     # gespeicherte Fotos/Collagen (wird automatisch erstellt)
```

## Hinweise zu Hardware
- **DSLR (gPhoto2, Linux)**  
  ```bash
  sudo apt install gphoto2 libgphoto2-dev
  gphoto2 --auto-detect
  gphoto2 --capture-image-and-download
  ```
- **Webcam**: benötigt `opencv-python`; die App wählt automatisch die erste verfügbare Kamera, wenn keine DSLR gefunden wird.
- **Druck**: `lp <datei>` muss funktionieren; optional kann in `Printer(queue_name=...)` ein Queue-Name hinterlegt werden.

## Status
Aktive Entwicklung. Slideshow/ExternalDisplay sind als Stub vorhanden, funktionieren aber noch nicht produktiv.
