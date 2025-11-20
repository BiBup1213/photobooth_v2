"""
Screen showing the captured photo with print/abort actions and auto-timeout.
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ResultScreen(QWidget):
    """Displays the captured image and offers print/cancel options."""

    print_requested = pyqtSignal()
    cancel_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._image_path: Path | None = None
        self._pixmap: QPixmap | None = None

        self._image_label = QLabel("Kein Bild")
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setStyleSheet("background-color: black; color: white;")
        self._image_label.setMinimumSize(400, 300)

        self._print_button = QPushButton("Drucken")
        self._cancel_button = QPushButton("Nein")

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self._print_button)
        buttons_layout.addWidget(self._cancel_button)
        buttons_layout.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(self._image_label, stretch=1)
        layout.addLayout(buttons_layout)

        self._auto_return_timer = QTimer(self)
        self._auto_return_timer.setSingleShot(True)
        self._auto_return_timer.timeout.connect(self._handle_auto_return)

        self._print_button.clicked.connect(self._handle_print)
        self._cancel_button.clicked.connect(self._handle_cancel)

    def set_image(self, image_path: str) -> None:
        """Load and display the given image path."""

        self._image_path = Path(image_path)
        pixmap = QPixmap(str(self._image_path))
        if pixmap.isNull():
            self._pixmap = None
            self._image_label.setText("Bild konnte nicht geladen werden")
            self._image_label.setPixmap(QPixmap())
            return

        self._pixmap = pixmap
        self._image_label.setText("")
        self._update_scaled_pixmap()

    def start_auto_return(self, timeout_ms: int = 10_000) -> None:
        """Start the timer that auto-returns to the start screen."""

        self._auto_return_timer.stop()
        self._auto_return_timer.start(timeout_ms)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._update_scaled_pixmap()

    def _update_scaled_pixmap(self) -> None:
        if not self._pixmap:
            return

        target_size = self._image_label.size()
        if target_size.isEmpty():
            return

        scaled = self._pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)

    def _handle_print(self) -> None:
        self._auto_return_timer.stop()
        self.print_requested.emit()

    def _handle_cancel(self) -> None:
        self._auto_return_timer.stop()
        self.cancel_requested.emit()

    def _handle_auto_return(self) -> None:
        self.cancel_requested.emit()
