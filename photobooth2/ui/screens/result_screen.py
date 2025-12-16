"""
Screen showing the captured photo with print/abort actions and auto-timeout.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class ResultScreen(QWidget):
    """Displays the captured image and offers print/cancel options."""

    print_requested = pyqtSignal()
    cancel_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._image_path: Path | None = None
        self._pixmap: QPixmap | None = None
        self._actions_visible = True

        self._image_label = QLabel("Kein Bild")
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setStyleSheet("background-color: black; color: white;")
        self._image_label.setMinimumSize(400, 300)

        # --- icon-only buttons (transparent, no fill/frame) ---------------
        self._back_button = self._create_icon_only_button("back.png")
        self._home_button = self._create_icon_only_button("home.png")
        self._print_button = self._create_icon_only_button("print.png")

        button_bar = QHBoxLayout()
        button_bar.setContentsMargins(24, 12, 24, 24)
        button_bar.setSpacing(12)

        button_bar.addWidget(self._back_button, 0, Qt.AlignmentFlag.AlignLeft)
        button_bar.addWidget(self._home_button, 0, Qt.AlignmentFlag.AlignLeft)
        button_bar.addStretch(1)
        button_bar.addWidget(self._print_button, 0, Qt.AlignmentFlag.AlignRight)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(8)
        layout.addWidget(self._image_label, stretch=1)
        layout.addLayout(button_bar)

        self._auto_return_timer = QTimer(self)
        self._auto_return_timer.setSingleShot(True)
        self._auto_return_timer.timeout.connect(self._handle_auto_return)

        self._print_button.clicked.connect(self._handle_print)
        self._home_button.clicked.connect(self._handle_cancel)
        self._back_button.clicked.connect(self._handle_cancel)

    # ---------------------------------------------------------------- Buttons

    def _create_icon_only_button(self, filename: str) -> QPushButton:
        """
        Icon-only button:
        - transparent (no platform button frame/fill)
        - no padding / radius
        - fixed click area for touch
        """
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFlat(True)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # consistent touch target
        btn.setFixedSize(96, 96)

        self._apply_icon(btn, filename)

        btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background: transparent;
                border: none;
            }
            QPushButton:pressed {
                background: transparent;
                border: none;
            }
            """
        )
        return btn

    def _apply_icon(self, button: QPushButton, filename: str) -> None:
        path = ASSETS_DIR / filename
        if path.exists():
            icon = QIcon(str(path))
            button.setIcon(icon)

            # For designed PNG buttons, set to match the button size.
            button.setIconSize(QtCore.QSize(96, 96))

    # ---------------------------------------------------------------- API

    def set_actions_visible(self, visible: bool) -> None:
        self._actions_visible = visible
        for btn in (self._print_button, self._home_button, self._back_button):
            btn.setVisible(visible)
            btn.setEnabled(visible)

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

    # ---------------------------------------------------------------- Actions

    def _handle_print(self) -> None:
        self._auto_return_timer.stop()
        self.print_requested.emit()

    def _handle_cancel(self) -> None:
        self._auto_return_timer.stop()
        self.cancel_requested.emit()

    def _handle_auto_return(self) -> None:
        self.cancel_requested.emit()
