"""
Placeholder for future admin/setup UI.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AdminScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Admin/Setup Screen in Arbeit"),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
