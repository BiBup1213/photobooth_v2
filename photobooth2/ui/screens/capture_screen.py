"""
Screen showing a themed countdown before taking a single photo.
"""

from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CaptureScreen(QWidget):
    """
    Sequence:
      1. Zeigt "Bitte lächeln" groß in der Mitte.
      2. Text fadet weg.
      3. Großer Countdown (3,2,1) startet.
      4. Danach: countdown_finished-Signal.

    Der X-Button oben rechts sendet close_requested,
    das MainWindow entscheidet dann, ob die App beendet
    oder zum Startscreen zurückgekehrt wird.
    """

    countdown_finished = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._remaining = 0

        # Timer für eigentlichen Countdown
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._tick)

        # Timer, der kurz "Bitte lächeln" stehen lässt, bevor gefadet wird
        self._intro_hold_timer = QTimer(self)
        self._intro_hold_timer.setSingleShot(True)
        self._intro_hold_timer.timeout.connect(self._start_message_fade)

        self._build_ui()
        self._setup_fade_animation()

    # ------------------------------------------------------------------ UI-Aufbau

    def _build_ui(self) -> None:
        # Hintergrund im selben Beige wie Startscreen
        self.setStyleSheet("background-color: #f3e7d3;")

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 40)
        root.setSpacing(10)

        # Mittelbereich: "Bitte lächeln" + große Zahl
        self._message_label = QLabel("Bitte lächeln")
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_font = QFont()
        msg_font.setPointSize(56)  # deutlich größer
        msg_font.setBold(True)
        self._message_label.setFont(msg_font)
        # reiner Text, kein Kasten darunter
        self._message_label.setStyleSheet("color: #5a4c3b; background: transparent;")

        self._count_label = QLabel("")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_font = QFont()
        count_font.setPointSize(160)  # richtig fett groß
        count_font.setBold(True)
        self._count_label.setFont(count_font)
        self._count_label.setStyleSheet("color: #5a4c3b; background: transparent;")
        root.addStretch(1)
        root.addWidget(self._message_label, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._count_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self._cancel_button = QPushButton("Abbrechen")
        self._cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_button.setMinimumHeight(64)
        self._cancel_button.setStyleSheet(
            """
            QPushButton {
                background-color: #5a4c3b;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 16px 28px;
                font-size: 28px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #907A5F; }
            QPushButton:pressed { background-color: #4a6a5b; }
            """
        )
        self._cancel_button.clicked.connect(self._on_cancel_clicked)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self._cancel_button)
        button_row.addStretch(1)

        root.addSpacing(10)
        root.addLayout(button_row)
        root.addStretch(1)

    def _setup_fade_animation(self) -> None:
        # Opacity-Effekt + Animation für "Bitte lächeln"
        self._opacity_effect = QGraphicsOpacityEffect(self._message_label)
        self._message_label.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(1.0)

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(800)  # ms
        self._fade_anim.setStartValue(1.0)
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self._fade_anim.finished.connect(self._on_message_faded)

    # ------------------------------------------------------------------ Public API

    def start_countdown(self, seconds: int = 3) -> None:
        """
        Neuer Ablauf:
        - Countdown 3,2,1
        - danach: "Bitte lächeln"
        - danach sofort countdown_finished -> Foto
        """

        # Reset
        self._countdown_timer.stop()
        self._intro_hold_timer.stop()
        self._fade_anim.stop()

        self._remaining = max(0, seconds)

        # Message verstecken bis später
        self._message_label.hide()
        self._opacity_effect.setOpacity(1.0)

        # Countdown starten
        self._count_label.setText(str(self._remaining))
        self._countdown_timer.start()

    # ------------------------------------------------------------------ Ablauf intern

    def _start_message_fade(self) -> None:
        # Direkt Foto auslösen
        self.countdown_finished.emit()

    def _on_message_faded(self) -> None:
        # Text ausblenden und Countdown einblenden
        self._message_label.hide()

        # erste Zahl setzen und Timer starten
        self._count_label.setText(str(self._remaining))
        self._countdown_timer.start()

    def _tick(self) -> None:
        self._remaining -= 1

        if self._remaining <= 0:
            self._countdown_timer.stop()

            # Countdown ist fertig → "Bitte lächeln" zeigen (0,6s)
            self._count_label.setText("")  # Zahl ausblenden

            self._message_label.setText("Bitte lächeln")
            self._message_label.show()

            # Kurze Pause, dann Foto auslösen
            self._intro_hold_timer.start(600)
            return

        # Weiter Countdown anzeigen
        self._count_label.setText(str(self._remaining))

    # ------------------------------------------------------------------ Cancel

    def _on_cancel_clicked(self) -> None:
        self._intro_hold_timer.stop()
        self._countdown_timer.stop()
        self._fade_anim.stop()
        self.close_requested.emit()
