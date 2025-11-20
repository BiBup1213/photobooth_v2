# photobooth_v2
Modulare Photobooth-Software mit PyQt6-Touch-UI, DSLR-Ansteuerung über gPhoto2, Live-Preview, Collagen-Funktion und flexiblem Multi-Screen-Setup. Entwickelt für Events, Hochzeiten und automatisierte Workflows.

📸 Photobooth 2.0

Eine modulare Photobooth-Software auf Basis von Python 3, PyQt6 und gPhoto2.
Das System bietet eine Touch-optimierte Benutzeroberfläche, DSLR-Steuerung, Live-Preview, Collagen-Modus, Mehrbildschirm-Unterstützung und eine erweiterbare Modularchitektur.

🚀 Features

PyQt6 Touch-UI
Vollbild, für Events optimiert, große Buttons, klare Navigation.

DSLR-Anbindung via gPhoto2
Aufnahme, Live-View, Dateihandling.

Webcam-Unterstützung (für Live-Preview oder Alternative zur DSLR)

Mehrbildschirm-Setup
Hauptsteuerung auf Touchscreen, Live-Preview oder Slideshow auf externem Bildschirm.

Modulare Logik
Separate Module für:

Einzelfoto

Collage-Funktion

Kamera-Steuerung

UI-Screens

Event-Flows

Bildverarbeitung
Speicherung, temporäre Ordner, optionale Filter.

📁 Projektstruktur (aktuell/ geplant)
photobooth/
│
├── core/
│   ├── camera/
│   ├── logic/
│   ├── utils/
│   └── events/
│
├── ui/
│   ├── screens/
│   ├── components/
│   └── icons/
│
├── modes/
│   ├── single_photo/
│   └── collage/
│
├── assets/
│   └── templates/   # Rahmen, Overlays usw.
│
├── output/
│   └── photos/      # Generierte Fotos (im .gitignore)
│
├── requirements.txt
└── main.py

🔧 Installation
1. Repository klonen
git clone https://github.com/<dein-name>/photobooth-2.0.git
cd photobooth-2.0

2. Virtuelle Umgebung
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3. Abhängigkeiten installieren
pip install -r requirements.txt

4. Starten
python main.py

📷 DSLR-Unterstützung (Linux)

Voraussetzung:

sudo apt install gphoto2 libgphoto2-dev


Testen:

gphoto2 --auto-detect
gphoto2 --capture-image-and-download

🧪 Entwicklungsstatus

Aktive Entwicklung.
Module, UI und Logik werden iterativ erweitert.
Struktur und Architektur können sich noch ändern.

📄 Lizenz

(Bei Bedarf ergänzen.)
