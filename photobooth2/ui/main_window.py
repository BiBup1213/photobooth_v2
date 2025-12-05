"""
Main window hosting the stacked screens for the photobooth UI.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QPushButton,
    QMenu,
)

from photobooth2.config.loader import Settings
from photobooth2.controller.app_controller import AppController
from photobooth2.ui.dialogs.camera_selection_dialog import CameraSelectionDialog
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

        # Stacked screens + global gradient background
        self.stacked = QStackedWidget()
        self.stacked.setObjectName("Background")
        self.stacked.setStyleSheet(
            """
            QWidget#Background {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #F1E3D2,
                    stop: 0.5 #EEDBCC,
                    stop: 1 #E7D0B8
                );
            }
            """
        )
        self.setCentralWidget(self.stacked)

        self.start_screen = StartScreen(settings)
        self.capture_screen = CaptureScreen()
        self.result_screen = ResultScreen()
        self.gallery_screen = GalleryScreen()

        self.stacked.addWidget(self.start_screen)
        self.stacked.addWidget(self.capture_screen)
        self.stacked.addWidget(self.result_screen)
        self.stacked.addWidget(self.gallery_screen)

        # Start-Screen Aktionen
        self.start_screen.photo_requested.connect(self._handle_single_photo)
        self.start_screen.collage_requested.connect(self._handle_collage)
        self.start_screen.gallery_requested.connect(self._handle_gallery)

        # Capture-Screen Aktionen
        self.capture_screen.countdown_finished.connect(
            self._on_single_photo_countdown_finished
        )

        # Result-Screen Aktionen
        self.result_screen.print_requested.connect(self._on_result_print_requested)
        self.result_screen.cancel_requested.connect(self._on_result_cancel_requested)

        # Galerie-Screen Aktionen
        self.gallery_screen.back_requested.connect(self.show_start)
        self.gallery_screen.print_requested.connect(self._on_gallery_print_requested)
        self.gallery_screen.delete_requested.connect(self._on_gallery_delete_requested)

        # Permanenter Close-Button oben rechts
        self._create_close_button()
        # Globaler Hamburger oben links
        self._create_menu_button()

        self.show_start()

    # --- Close-Button -----------------------------------------------------

    def _create_close_button(self) -> None:
        self._close_button = QPushButton("×", self)
        self._close_button.setFixedSize(56, 56)

        font = self._close_button.font()
        font.setPointSize(28)
        font.setBold(True)
        self._close_button.setFont(font)

        self._close_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #5a4c3b;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.06);
                border-radius: 28px;
            }
            """
        )
        self._close_button.clicked.connect(self.close)

    def _create_menu_button(self) -> None:
        self._menu_button = QPushButton("☰", self)
        self._menu_button.setFixedSize(56, 56)

        font = self._menu_button.font()
        font.setPointSize(26)
        font.setBold(True)
        self._menu_button.setFont(font)

        self._menu_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #5a4c3b;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.06);
                border-radius: 28px;
            }
            """
        )
        self._menu_button.clicked.connect(self._open_menu)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        # Close-Button immer oben rechts platzieren
        side_margin = 24
        top_margin = 16
        if hasattr(self, "_close_button"):
            x = self.width() - self._close_button.width() - side_margin
            y = top_margin
            self._close_button.move(x, y)
        if hasattr(self, "_menu_button"):
            x = side_margin
            y = top_margin
            self._menu_button.move(x, y)

    # --- Screen-Wechsel ---------------------------------------------------

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
        logger.info("Open gallery")
        images = self.controller.list_gallery()
        self.gallery_screen.set_images(images)
        self.stacked.setCurrentWidget(self.gallery_screen)

    # --- Foto-Flow --------------------------------------------------------

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
            QMessageBox.information(
                self, "Drucken", "Bild wurde an den Drucker gesendet."
            )
        else:
            QMessageBox.critical(
                self, "Drucken", "Druckauftrag konnte nicht gestartet werden."
            )
        self.show_start()

    def _on_result_cancel_requested(self) -> None:
        self.show_start()

    # --- Galerie-Aktionen -------------------------------------------------

    def _on_gallery_print_requested(self, image: Path) -> None:
        success = self.controller.print_image(image)
        if success:
            QMessageBox.information(
                self, "Drucken", "Bild wurde an den Drucker gesendet."
            )
        else:
            QMessageBox.critical(
                self, "Drucken", "Druckauftrag konnte nicht gestartet werden."
            )

    def _on_gallery_delete_requested(self, image: Path) -> None:
        reply = QMessageBox.question(
            self,
            "Bild löschen",
            "Möchtest du dieses Bild wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        success = self.controller.delete_image(image)
        if not success:
            QMessageBox.critical(
                self, "Löschen", "Bild konnte nicht gelöscht werden."
            )
            return

        self.gallery_screen.remove_image(image)

    # --- Menü & Kamera-Auswahl -------------------------------------------

    def _open_menu(self) -> None:
        menu = QMenu(self)
        settings_action = menu.addAction("Einstellungen")
        camera_action = menu.addAction("Kamera auswählen")
        menu.addSeparator()
        quit_action = menu.addAction("Beenden")

        action = menu.exec(self._menu_button.mapToGlobal(self._menu_button.rect().bottomLeft()))
        if action == settings_action:
            QMessageBox.information(self, "Einstellungen", "Einstellungen folgen.")
        elif action == camera_action:
            self._open_camera_dialog()
        elif action == quit_action:
            self.close()

    def _open_camera_dialog(self) -> None:
        dialog = CameraSelectionDialog(self.controller, self)
        dialog.exec()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        try:
            self.controller.camera_manager.release()
        finally:
            super().closeEvent(event)
