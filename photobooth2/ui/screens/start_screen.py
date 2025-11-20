"""
Start screen showing the event banner, QR placeholder and primary actions.
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QFrame

from photobooth2.config.loader import Settings


class StartScreen(QWidget):
    photo_requested = pyqtSignal()
    collage_requested = pyqtSignal()
    gallery_requested = pyqtSignal()

    def __init__(self, settings: Settings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet("background-color: #f3e7d3;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(20)

        banner = QFrame()
        banner.setFrameShape(QFrame.Shape.NoFrame)
        banner.setStyleSheet("background-color: #f9f0df; border-radius: 16px; border: 2px solid #d6c2a1;")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(20, 20, 20, 20)
        banner_layout.setSpacing(12)

        title = QLabel(self.settings.event_name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))

        subtitle = QLabel(self.settings.event_date)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 18))

        qr_placeholder = QLabel("QR-Code \n(Platzhalter)")
        qr_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_placeholder.setStyleSheet("color: #7a6a55; border: 2px dashed #c7b79a; border-radius: 8px;")
        qr_placeholder.setMinimumHeight(160)

        banner_layout.addWidget(title)
        banner_layout.addWidget(subtitle)
        banner_layout.addWidget(qr_placeholder)

        buttons = QFrame()
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setSpacing(20)

        gallery_btn = self._create_action_button("Galerie")
        photo_btn = self._create_action_button("Foto")
        collage_btn = self._create_action_button("Collage")

        gallery_btn.clicked.connect(self.gallery_requested.emit)
        photo_btn.clicked.connect(self.photo_requested.emit)
        collage_btn.clicked.connect(self.collage_requested.emit)

        buttons_layout.addWidget(gallery_btn)
        buttons_layout.addWidget(photo_btn)
        buttons_layout.addWidget(collage_btn)

        layout.addWidget(banner, stretch=2)
        layout.addWidget(buttons, stretch=1)
        layout.setAlignment(buttons, Qt.AlignmentFlag.AlignBottom)

    def _create_action_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setMinimumHeight(80)
        btn.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        btn.setStyleSheet(
            """
            QPushButton { background-color: #5a7a6b; color: white; border: none; border-radius: 12px; }
            QPushButton:hover { background-color: #6c8c7d; }
            QPushButton:pressed { background-color: #4a6a5b; }
            """
        )
        return btn
