"""
Helpers for loading the wedding overlay font and persisting overlay text lines.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFontDatabase

# Font lives at photobooth2/ui/assets/font/Andrea Bellarosa.ttf
FONT_PATH = Path(__file__).resolve().parent / "assets" / "font" / "Andrea Bellarosa.ttf"

_ORG = "Photobooth"
_APP = "Photobooth2"
_KEY_LINE1 = "overlay/text_line1"
_KEY_LINE2 = "overlay/text_line2"
_DEFAULT_LINE1 = "Text 1"
_DEFAULT_LINE2 = "Txt 2 - Datum"


def _settings() -> QSettings:
    return QSettings(_ORG, _APP)


def load_andrea_bellarosa_font() -> str:
    """
    Load the Andrea Bellarosa font and return its family name.
    Raises if the font file is missing or cannot be loaded.
    """
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Font file not found: {FONT_PATH}")

    font_id = QFontDatabase.addApplicationFont(str(FONT_PATH))
    if font_id == -1:
        raise RuntimeError(f"Unable to load font: {FONT_PATH}")

    families = QFontDatabase.applicationFontFamilies(font_id)
    if not families:
        raise RuntimeError(f"No font families found in: {FONT_PATH}")

    return families[0]


def load_overlay_text() -> tuple[str, str]:
    """
    Load persisted overlay text lines, falling back to defaults.
    """
    settings = _settings()
    line1 = settings.value(_KEY_LINE1, _DEFAULT_LINE1, type=str) or _DEFAULT_LINE1
    line2 = settings.value(_KEY_LINE2, _DEFAULT_LINE2, type=str) or _DEFAULT_LINE2
    return line1, line2


def save_overlay_text(line1: str, line2: str) -> None:
    """
    Persist overlay text lines.
    """
    settings = _settings()
    settings.setValue(_KEY_LINE1, line1)
    settings.setValue(_KEY_LINE2, line2)
