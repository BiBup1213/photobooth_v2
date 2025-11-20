"""
Main window hosting the stacked screens for the photobooth UI.
"""
from __future__ import annotations

import logging
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

        self.show_start()

    def show_start(self) -> None:
        self.stacked.setCurrentWidget(self.start_screen)

    def _handle_single_photo(self) -> None:
        QMessageBox.information(self, "Foto", "Placeholder: Foto-Flow folgt.")
        logger.info("Start single photo flow")

    def _handle_collage(self) -> None:
        QMessageBox.information(self, "Collage", "Placeholder: Collage-Flow folgt.")
        logger.info("Start collage flow")

    def _handle_gallery(self) -> None:
        QMessageBox.information(self, "Galerie", "Placeholder: Galerie-Ansicht folgt.")
        logger.info("Open gallery")
