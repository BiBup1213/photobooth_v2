"""
Main window hosting the stacked screens for the photobooth UI.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QMenu, QMessageBox, QPushButton, QStackedWidget

from photobooth2.config.loader import Settings
from photobooth2.controller.app_controller import AppController
from photobooth2.ui.dialogs.camera_selection_dialog import CameraSelectionDialog
from photobooth2.ui.overlay_text_settings import OverlayTextSettingsDialog
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
        self._capture_mode: str = "single"  # "single" | "collage"
        self._collage_shots: list[Path] = []
        self._collage_target_count: int = max(1, controller.collage.collage_count)
        self._collage_preview_timer = QTimer(self)
        self._collage_preview_timer.setSingleShot(True)
        self._collage_preview_timer.timeout.connect(self._continue_collage_sequence)

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
        self.capture_screen.countdown_finished.connect(self._on_capture_countdown_finished)
        self.capture_screen.close_requested.connect(self._on_capture_close_requested)

        # Result-Screen Aktionen
        self.result_screen.print_requested.connect(self._on_result_print_requested)
        self.result_screen.cancel_requested.connect(self._on_result_cancel_requested)

        # Galerie-Screen Aktionen
        self.gallery_screen.back_requested.connect(self.show_start)
        self.gallery_screen.print_requested.connect(self._on_gallery_print_requested)
        self.gallery_screen.delete_requested.connect(self._on_gallery_delete_requested)
        self.gallery_screen.image_selected.connect(self._on_gallery_image_selected)

        # Permanenter Close-Button oben rechts
        self._create_close_button()
        # Globaler Hamburger oben links
        self._create_menu_button()

        self.show_start()

        if not self.controller.has_active_camera():
            QMessageBox.warning(
                self,
                "Kamera",
                "Keine Kamera verbunden. Bitte anschließen und erneut versuchen.",
            )

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
        if not self._ensure_camera_available():
            return
        logger.info("Start single photo flow")
        self._start_capture_flow("single")

    def _handle_collage(self) -> None:
        if not self._ensure_camera_available():
            return
        logger.info("Start collage flow")
        self._collage_shots = []
        self._collage_target_count = max(1, self.controller.collage.collage_count)
        self._start_capture_flow("collage")

    def _handle_gallery(self) -> None:
        logger.info("Open gallery")
        images = self.controller.list_gallery()
        self.gallery_screen.set_images(images)
        self.stacked.setCurrentWidget(self.gallery_screen)

    # --- Foto-Flow --------------------------------------------------------

    def _on_capture_countdown_finished(self) -> None:
        if self._capture_mode == "collage":
            self._process_collage_capture_step()
        else:
            self._finish_single_capture()

    def _finish_single_capture(self) -> None:
        path = self.controller.capture_single_photo()

        if path is None:
            QMessageBox.critical(self, "Fehler", "Fotoaufnahme fehlgeschlagen.")
            self.show_start()
            return

        self._last_result_path = path
        self.result_screen.set_actions_visible(True)
        self.result_screen.set_image(str(path))
        self.result_screen.start_auto_return(10_000)
        self.stacked.setCurrentWidget(self.result_screen)

    def _process_collage_capture_step(self) -> None:
        shot = self.controller.capture_single_photo()

        if shot is None:
            QMessageBox.critical(self, "Fehler", "Collage-Aufnahme fehlgeschlagen.")
            self._reset_collage_state()
            self.show_start()
            return

        self._collage_shots.append(shot)

        # Show short preview of the captured shot
        self._show_collage_preview(shot)

        if len(self._collage_shots) < self._collage_target_count:
            self._collage_preview_timer.start(2500)
        else:
            self._collage_preview_timer.start(2500)

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

    def _on_capture_close_requested(self) -> None:
        logger.info("Capture flow cancelled by user")
        self._reset_collage_state()
        self._collage_preview_timer.stop()
        self.show_start()

    # --- Galerie-Aktionen -------------------------------------------------

    def _on_gallery_print_requested(self, image: Path) -> None:
        success = self.controller.print_image(image)
        if success:
            QMessageBox.information(self, "Drucken", "Bild wurde an den Drucker gesendet.")
        else:
            QMessageBox.critical(self, "Drucken", "Druckauftrag konnte nicht gestartet werden.")

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
            QMessageBox.critical(self, "Löschen", "Bild konnte nicht gelöscht werden.")
            return

        self.gallery_screen.remove_image(image)

    def _on_gallery_image_selected(self, image: Path) -> None:
        self.gallery_screen.show_detail(image)

    # --- Menü & Kamera-Auswahl -------------------------------------------

    def _open_menu(self) -> None:
        menu = QMenu(self)
        overlay_action = menu.addAction("Overlay Text")
        settings_action = menu.addAction("Einstellungen")
        camera_action = menu.addAction("Kamera auswählen")
        menu.addSeparator()
        quit_action = menu.addAction("Beenden")

        action = menu.exec(self._menu_button.mapToGlobal(self._menu_button.rect().bottomLeft()))
        if action == overlay_action:
            self._open_overlay_text_dialog()
        elif action == settings_action:
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

    def _start_capture_flow(self, mode: str) -> None:
        self._capture_mode = mode
        self.stacked.setCurrentWidget(self.capture_screen)
        self.capture_screen.start_countdown(3)

    def _reset_collage_state(self) -> None:
        self._collage_shots = []
        self._collage_target_count = max(1, self.controller.collage.collage_count)
        self._collage_preview_timer.stop()

    def _ensure_camera_available(self) -> bool:
        if self.controller.has_active_camera():
            return True
        QMessageBox.warning(
            self,
            "Kamera",
            "Keine Kamera verbunden. Bitte anschließen und erneut versuchen.",
        )
        return False

    def _show_collage_preview(self, shot: Path) -> None:
        self.result_screen.set_actions_visible(False)
        self.result_screen.set_image(str(shot))
        self.stacked.setCurrentWidget(self.result_screen)

    def _continue_collage_sequence(self) -> None:
        if len(self._collage_shots) < self._collage_target_count:
            self.stacked.setCurrentWidget(self.capture_screen)
            self.capture_screen.start_countdown(3)
            return

        collage_path = self.controller.compose_collage_from_photos(self._collage_shots)
        if collage_path is None:
            QMessageBox.critical(self, "Fehler", "Collage konnte nicht erstellt werden.")
            self._reset_collage_state()
            self.show_start()
            return

        self._reset_collage_state()
        self._last_result_path = collage_path
        self.result_screen.set_actions_visible(True)
        self.result_screen.set_image(str(collage_path))
        self.result_screen.start_auto_return(10_000)
        self.stacked.setCurrentWidget(self.result_screen)

    # --- Overlay Text -----------------------------------------------------

    def _open_overlay_text_dialog(self) -> None:
        dialog = OverlayTextSettingsDialog(self)
        dialog.overlay_text_saved.connect(self._on_overlay_text_saved)
        dialog.exec()

    def _on_overlay_text_saved(self, line1: str, line2: str) -> None:
        # Update start screen immediately
        self.start_screen.reload_overlay_text()
