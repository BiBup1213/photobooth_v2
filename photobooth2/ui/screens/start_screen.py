"""
Start screen showing the event banner, QR placeholder and primary actions.
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
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
        self._banner_pixmap: QPixmap | None = self._load_pixmap(ASSETS_DIR / "main_banner_floral.png")
        self._banner_label: QLabel | None = None

        self._build_ui()
        self._update_banner_pixmap()

    def _build_ui(self) -> None:
        self.setStyleSheet("background-color: #f3e7d3;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(30)

        banner_frame = QFrame()
        banner_frame.setFrameShape(QFrame.Shape.NoFrame)
        banner_frame.setStyleSheet(
            "background-color: #f9f0df; border-radius: 20px; border: 2px solid #d6c2a1;"
        )
        banner_layout = QVBoxLayout(banner_frame)
        banner_layout.setContentsMargins(30, 30, 30, 30)
        banner_layout.setSpacing(16)

        self._banner_label = QLabel()
        self._banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._banner_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._banner_label.setMinimumHeight(260)
        self._banner_label.setStyleSheet(
            "background-color: #fff8ec; border-radius: 18px; border: 1px solid #e0d2b8;"
        )

        title = QLabel(self.settings.event_name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #5a4c3b;")

        subtitle = QLabel(self.settings.event_date)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setStyleSheet("color: #6d5a44;")

        qr_placeholder = QLabel("QR-Code (Platzhalter)")
        qr_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_placeholder.setMinimumHeight(120)
        qr_placeholder.setStyleSheet(
            "color: #7a6a55; border: 2px dashed #c7b79a; border-radius: 10px; background-color: #fff8ec;"
        )

        banner_layout.addWidget(self._banner_label)
        banner_layout.addWidget(title)
        banner_layout.addWidget(subtitle)
        banner_layout.addWidget(qr_placeholder)

        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(24)

        gallery_btn = self._create_action_button(ASSETS_DIR / "btn_gallery.png", "Galerie")
        photo_btn = self._create_action_button(ASSETS_DIR / "btn_photo.png", "Foto")
        collage_btn = self._create_action_button(ASSETS_DIR / "btn_collage.png", "Collage")

        gallery_btn.clicked.connect(self.gallery_requested.emit)
        photo_btn.clicked.connect(self.photo_requested.emit)
        collage_btn.clicked.connect(self.collage_requested.emit)

        buttons_layout.addWidget(gallery_btn)
        buttons_layout.addWidget(photo_btn)
        buttons_layout.addWidget(collage_btn)

        layout.addWidget(banner_frame, stretch=2)
        layout.addWidget(buttons_frame, stretch=1)
        layout.setAlignment(buttons_frame, Qt.AlignmentFlag.AlignBottom)

    def _create_action_button(self, icon_path: Path, fallback_text: str) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(110)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        btn.setStyleSheet(
            """
            QPushButton { background-color: #5a7a6b; color: white; border: none; border-radius: 14px; }
            QPushButton:hover { background-color: #6c8c7d; }
            QPushButton:pressed { background-color: #4a6a5b; }
            """
        )

        icon = self._load_icon(icon_path)
        if icon is not None:
            btn.setIcon(icon)
            btn.setIconSize(QSize(128, 128))
            btn.setText("")
        else:
            btn.setText(fallback_text)

        btn.setToolTip(fallback_text)
        return btn

    def _load_pixmap(self, path: Path) -> QPixmap | None:
        if not path.exists():
            return None

        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return None
        return pixmap

    def _load_icon(self, path: Path) -> QIcon | None:
        pixmap = self._load_pixmap(path)
        if pixmap is None:
            return None

        icon = QIcon(pixmap)
        return icon if not icon.isNull() else None

    def _update_banner_pixmap(self) -> None:
        if self._banner_label is None:
            return

        if self._banner_pixmap is None or self._banner_pixmap.isNull():
            self._banner_label.clear()
            return

        if self._banner_label.width() <= 0 or self._banner_label.height() <= 0:
            return

        scaled = self._banner_pixmap.scaled(
            self._banner_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._banner_label.setPixmap(scaled)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._update_banner_pixmap()
