"""
Main window hosting the stacked screens for the photobooth UI.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

from photobooth2.config.loader import Settings
from photobooth2.controller.app_controller import AppController
from photobooth2.ui.screens.capture_screen import CaptureScreen
from photobooth2.ui.screens.gallery_screen import GalleryScreen
from photobooth2.ui.screens.result_screen import ResultScreen
from photobooth2.ui.screens.start_screen import StartScreen

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, controller: AppController) -> None:
        super().__init__()
        self.settings = settings
        self.controller = controller
        self._last_result_path: Path | None = None

        self.setWindowTitle("Photobooth 2.0")
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.start_screen = StartScreen(settings)
        self.capture_screen = CaptureScreen()
        self.result_screen = ResultScreen()
        self.gallery_screen = GalleryScreen()

        self.stacked.addWidget(self.start_screen)
        self.stacked.addWidget(self.capture_screen)
        self.stacked.addWidget(self.result_screen)
        self.stacked.addWidget(self.gallery_screen)

        self.start_screen.photo_requested.connect(self._handle_single_photo)
        self.start_screen.collage_requested.connect(self._handle_collage)
        self.start_screen.gallery_requested.connect(self._handle_gallery)

        self.capture_screen.countdown_finished.connect(
            self._on_single_photo_countdown_finished
        )
        self.result_screen.print_requested.connect(self._on_result_print_requested)
        self.result_screen.cancel_requested.connect(self._on_result_cancel_requested)

        self.show_start()

    def show_start(self) -> None:
        self.stacked.setCurrentWidget(self.start_screen)

    def _handle_single_photo(self) -> None:
        logger.info("Start single photo flow")
        self.stacked.setCurrentWidget(self.capture_screen)
        self.capture_screen.start_countdown(3)

    def _handle_collage(self) -> None:
        QMessageBox.information(self, "Collage", "Placeholder: Collage-Flow folgt.")
        logger.info("Start collage flow")

    def _handle_gallery(self) -> None:
        QMessageBox.information(self, "Galerie", "Placeholder: Galerie-Ansicht folgt.")
        logger.info("Open gallery")

    def _on_single_photo_countdown_finished(self) -> None:
        path = self.controller.capture_single_photo()

        if path is None:
            QMessageBox.critical(self, "Fehler", "Fotoaufnahme fehlgeschlagen.")
            self.show_start()
            return

        self._last_result_path = path
        self.result_screen.set_image(str(path))
        self.result_screen.start_auto_return(10_000)
        self.stacked.setCurrentWidget(self.result_screen)

    def _on_result_print_requested(self) -> None:
        if not self._last_result_path:
            logger.warning("Print requested but no result available")
            QMessageBox.warning(self, "Drucken", "Kein Bild zum Drucken vorhanden.")
            self.show_start()
            return

        success = self.controller.print_image(self._last_result_path)
        if success:
            QMessageBox.information(self, "Drucken", "Bild wurde an den Drucker gesendet.")
        else:
            QMessageBox.critical(self, "Drucken", "Druckauftrag konnte nicht gestartet werden.")
        self.show_start()

    def _on_result_cancel_requested(self) -> None:
        self.show_start()