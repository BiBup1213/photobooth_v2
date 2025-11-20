"""
Placeholder screen for countdown and capture flow.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CaptureScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Countdown / Capture kommt hier"), alignment=Qt.AlignmentFlag.AlignCenter)
