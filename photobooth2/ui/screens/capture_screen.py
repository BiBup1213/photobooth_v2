"""
Screen showing a simple countdown before taking a single photo.
"""
from __future__ import annotations

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CaptureScreen(QWidget):
    """Displays a countdown and emits when it finishes."""

    countdown_finished = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._remaining = 0

        self.setStyleSheet("background-color: black;")

        self._label = QLabel("", self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(64)
        font.setBold(True)
        self._label.setFont(font)
        self._label.setStyleSheet("color: white;")

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    def start_countdown(self, seconds: int = 3) -> None:
        """Start or restart the countdown timer."""

        self._timer.stop()
        self._remaining = max(0, seconds)
        self._label.setText(str(self._remaining) if self._remaining > 0 else "Foto!")

        if self._remaining == 0:
            self.countdown_finished.emit()
            return

        self._timer.start()

    def _tick(self) -> None:
        self._remaining -= 1

        if self._remaining <= 0:
            self._timer.stop()
            self._label.setText("Foto!")
            self.countdown_finished.emit()
            return

        self._label.setText(str(self._remaining))
