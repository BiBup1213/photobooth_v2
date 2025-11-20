"""
Start screen showing floral header graphic and icon-only action buttons.
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from photobooth2.config.loader import Settings

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class StartScreen(QWidget):
    photo_requested = pyqtSignal()
    collage_requested = pyqtSignal()
    gallery_requested = pyqtSignal()

    def __init__(self, settings: Settings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings

        # complete window background beige
        self.setStyleSheet("background-color: #f3e7d3;")

        self._floral_pixmap: QPixmap | None = self._load_pixmap(
            ASSETS_DIR / "main_banner_floral.png"
        )
        self._floral_label: QLabel | None = None

        self._build_ui()
        self._update_floral_pixmap()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 40, 80, 40)
        layout.setSpacing(20)

        # -------------------------------------------------
        # FLORAL HEADER (PNG centered, no frame)
        # -------------------------------------------------
        self._floral_label = QLabel()
        self._floral_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._floral_label.setMinimumHeight(420)
        self._floral_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._floral_label.setStyleSheet("background: transparent;")

        layout.addWidget(self._floral_label, stretch=3)

        # -------------------------------------------------
        # BUTTONS (icon-only, centered)
        # -------------------------------------------------
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 40)
        buttons_layout.setSpacing(60)

        gallery_btn = self._create_action_button(ASSETS_DIR / "btn_gallery.png", "Galerie")
        photo_btn = self._create_action_button(ASSETS_DIR / "btn_photo.png", "Foto")
        collage_btn = self._create_action_button(ASSETS_DIR / "btn_collage.png", "Collage")

        gallery_btn.clicked.connect(self.gallery_requested.emit)
        photo_btn.clicked.connect(self.photo_requested.emit)
        collage_btn.clicked.connect(self.collage_requested.emit)

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(gallery_btn)
        buttons_layout.addWidget(photo_btn)
        buttons_layout.addWidget(collage_btn)
        buttons_layout.addStretch(1)

        layout.addLayout(buttons_layout, stretch=1)

    # ------------------------------------------------------------------
    def _create_action_button(self, icon_path: Path, fallback_text: str) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # fixed icon tile size
        btn.setMinimumSize(160, 160)
        btn.setMaximumSize(180, 180)
        btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        icon = self._load_icon(icon_path)
        if icon:
            btn.setIcon(icon)
            btn.setIconSize(QSize(140, 140))
            btn.setText("")
        else:
            btn.setText(fallback_text)
            btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        # pure icon, no background
        btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
            }
            """
        )

        return btn

    # ------------------------------------------------------------------
    def _load_pixmap(self, path: Path) -> QPixmap | None:
        if not path.exists():
            return None
        pixmap = QPixmap(str(path))
        return pixmap if not pixmap.isNull() else None

    def _load_icon(self, path: Path) -> QIcon | None:
        pix = self._load_pixmap(path)
        if pix is None:
            return None
        icon = QIcon(pix)
        return icon if not icon.isNull() else None

    # ------------------------------------------------------------------
    def _update_floral_pixmap(self) -> None:
        if not self._floral_label:
            return
        if not self._floral_pixmap:
            self._floral_label.clear()
            return

        size = self._floral_label.size()
        if size.width() <= 0 or size.height() <= 0:
            return

        scaled = self._floral_pixmap.scaled(
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._floral_label.setPixmap(scaled)

    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_floral_pixmap()
