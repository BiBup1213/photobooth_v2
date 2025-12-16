"""
Editable QR card text fields with custom font loading for the
wedding-style overlay.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"


@lru_cache(maxsize=8)
def load_app_font(font_path: str) -> str:
    """
    Load a TTF/OTF font and return its family name. Cached.
    Raises if missing or cannot be loaded.
    """
    path = Path(font_path)
    if not path.exists():
        raise FileNotFoundError(f"Font file not found: {path}")

    font_id = QFontDatabase.addApplicationFont(str(path))
    if font_id == -1:
        raise RuntimeError(f"Unable to load font: {path}")

    families = QFontDatabase.applicationFontFamilies(font_id)
    if not families:
        raise RuntimeError(f"No font families found in: {path}")

    return families[0]


class QrCardTextFields(QWidget):
    """
    Two-line editable text stack for a QR card overlay.
    """

    def __init__(
        self,
        font_family: str,
        title_text: str = "",
        subtitle_text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Keep parent card styling in control; we just remain transparent.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.title_edit = self._build_line_edit(
            font_family=font_family,
            point_size=19,
            text=title_text,
            placeholder="Text 1",
            max_len=40,
            fixed_height=34,
        )
        self.subtitle_edit = self._build_line_edit(
            font_family=font_family,
            point_size=16,
            text=subtitle_text,
            placeholder="Text 2 - Date",
            max_len=60,
            fixed_height=30,
        )

        layout.addWidget(self.title_edit)
        layout.addWidget(self.subtitle_edit)

    def _build_line_edit(
        self,
        font_family: str,
        point_size: int,
        text: str,
        placeholder: str,
        max_len: int,
        fixed_height: int,
    ) -> QLineEdit:
        line = QLineEdit(text)
        line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line.setPlaceholderText(placeholder)
        line.setMaxLength(max_len)
        line.setFixedHeight(fixed_height)

        line.setFont(QFont(font_family, point_size))

        # Kiosk/touch friendliness
        line.setClearButtonEnabled(False)
        line.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        line.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        line.setStyleSheet(
            """
            QLineEdit {
                background: transparent;
                border: none;
                color: #c84b4b;
                padding: 4px 8px;
                selection-color: #f3e7d3;
                selection-background-color: #c84b4b;
            }
            QLineEdit:focus {
                border-bottom: 2px solid rgba(200, 75, 75, 0.45);
                background-color: rgba(200, 75, 75, 0.06);
            }
            """
        )

        # put cursor at end for convenience
        line.setCursorPosition(len(line.text()))
        return line
