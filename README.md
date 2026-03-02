# Photobooth 2.0

Touch-optimierte Photobooth-Anwendung auf Basis von Python, PyQt6 und gPhoto2.  
Unterstützt DSLR (gPhoto2) oder Webcam, Collagen, Galerie mit Drucken/Löschen und arbeitet im Vollbild für Event-Setups.

---

## 🧭 Projekt-Hintergrund

Photobooth 2.0 ist aus einer klassischen DIY-Photobox entstanden.

Die erste Version war eine einfache Konstruktion:

- DSLR mit manueller Auslösung
- reine Bildspeicherung
- kein eigenes Interface
- stark hardwarezentriert

Mit wachsendem Anspruch entstand der Wunsch nach:

- Touch-Bedienung direkt am Gerät
- einer klar strukturierten Event-UI
- modularer Software-Architektur
- integrierter Druckfunktion
- Galerie mit Lösch- & Printoption
- Design-Themes & Overlay-System
- stabiler Linux-Basis ohne proprietäre Software

Das Ergebnis ist Photobooth 2.0 – eine eigenständige, modulare Python/PyQt6-Anwendung mit klarer Trennung von:

- UI
- Geräteansteuerung
- Drucklogik
- Feature-Workflows
- Konfiguration

---

## 🖥️ Hardware-Setup

Das System basiert auf einem umfunktionierten Lenovo Convertible Touch-Notebook, das als Herzstück der gesamten Photobooth dient.

Warum dieses Setup?

- integriertes Touch-Display
- kompakt und eventtauglich
- keine externe Touch-Hardware nötig
- Linux-kompatibel
- ideal für Vollbild-Kiosk-Modus
- ressourcenschonend durch Wiederverwendung alter Hardware

Das Gerät läuft unter Linux (Fedora) und steuert:

- DSLR via gPhoto2
- Webcam (Fallback via OpenCV)
- Drucker über CUPS (`lp`)
- optional externen Monitor
- Touch-UI (PyQt6)

---

## 🧠 System-Architektur

```
                  ┌───────────────────────────┐
                  │   Lenovo Convertible      │
                  │   Linux + PyQt6 UI        │
                  │   (Photobooth 2.0 App)    │
                  └─────────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
       ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
       │   DSLR       │   │   Drucker   │   │  Externer   │
       │  gPhoto2     │   │   CUPS/lp   │   │  Monitor    │
       └─────────────┘   └─────────────┘   └─────────────┘
                                │
                         ┌──────▼──────┐
                         │   Galerie   │
                         │ Speicherung │
                         └─────────────┘
```

### Architektur-Prinzipien

- Geräte sind kapsuliert (`devices/`)
- Feature-Logik ist getrennt (`features/`)
- UI ist modular in Screens organisiert (`ui/`)
- Zentrale Orchestrierung erfolgt über den `AppController`
- Konfiguration über `settings.toml`

---

## ✨ Features

- Touch-UI mit großen Buttons und Vollbild (PyQt6)
- Einzelbild-Workflow
- Collage-Workflow (optional mit PNG-Overlay)

### Kameraauswahl

- bevorzugt DSLR via gPhoto2
- Fallback auf Webcam (OpenCV)

### Galerie mit

- Grid-Ansicht
- Detailansicht
- Drucken
- Löschen

- Druck über das System-Backend (`lp`/CUPS)
- Optionaler externer Bildschirm (Stub)
- Konfigurierbares Event-Branding

---

## ⚙️ Voraussetzungen

- Python 3.11+ empfohlen
- System: Linux/macOS/Windows  
  (DSLR benötigt gPhoto2 → primär Linux empfohlen)

### Python-Pakete

- `PyQt6`
- `Pillow`
- optional `opencv-python` (für Webcam)

### DSLR

- `gphoto2`
- `libgphoto2`
- beide auf `PATH`

### Drucken

- funktionierendes `lp`/CUPS-Setup

---

## 🚀 Setup

```bash
git clone <dein-fork-oder-url>/photobooth_v2.git
cd photobooth_v2
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install PyQt6 Pillow opencv-python  # opencv optional (für Webcam nötig)
```

---

## ▶ Starten

```bash
python -m photobooth2
```

Die App öffnet im Vollbild.  
Oben rechts: Schließen-Button  
Oben links: Menü / Hamburger

---

## 🧩 Konfiguration

Datei:  
`photobooth2/config/settings.toml`

Falls die Datei fehlt, werden Default-Werte verwendet und `output/` automatisch erstellt.

```toml
[event]
name = "Eure Fotobox"
date = "2024-12-31"
qr_url = "https://example.com/gallery"

[paths]
output_dir = "output"

[collage]
photo_count = 4
# overlay = "assets/floral_overlay.png"
```

### Erklärung

- `output_dir` wird beim Start erzeugt
- `photo_count` steuert die Collage-Schritte
- Werte >4 werden aktuell auf 4 begrenzt
- `overlay` ist optional (PNG mit Alphakanal)

---

## 📁 Verzeichnisstruktur

```
photobooth2/
├── main.py
├── config/
│   └── loader.py
├── controller/
├── devices/
│   ├── dslr (gphoto2)
│   ├── webcam (OpenCV)
│   ├── printer (lp)
│   └── external_display (stub)
├── features/
│   ├── single_photo
│   ├── collage (Pillow)
│   ├── gallery
│   └── slideshow (stub)
└── ui/
   ├── screens
   ├── dialogs
   └── assets
output/
```

---

## 🔧 Hinweise zu Hardware

### DSLR (Linux)

```bash
sudo apt install gphoto2 libgphoto2-dev
gphoto2 --auto-detect
gphoto2 --capture-image-and-download
```

### Webcam

- benötigt `opencv-python`
- erste verfügbare Kamera wird automatisch gewählt

### Druck

```bash
lp testbild.jpg
```

Optional kann ein Queue-Name im Printer-Device hinterlegt werden.

---

## 🧪 Status

- Aktive Entwicklung
- Slideshow & ExternalDisplay sind als Stub vorhanden
- UI-Optimierungen laufen
- Theme- & Design-System wird iterativ erweitert

---

## 🎯 Ziel des Projekts

Photobooth 2.0 ist kein reines GUI-Experiment, sondern ein modular aufgebautes, Linux-basiertes Event-System, das Hardware-Integration, UI-Design und Software-Architektur kombiniert.

Ziel ist ein:

- stabiles
- wartbares
- modular erweiterbares
- eventtaugliches System

auf Basis vollständig kontrollierter Open-Source-Technologien.
