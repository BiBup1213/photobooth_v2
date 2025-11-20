"""
Placeholder screen showing the captured image and print choices.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ResultScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Aufnahme-Ergebnis / Drucken?"), alignment=Qt.AlignmentFlag.AlignCenter)
