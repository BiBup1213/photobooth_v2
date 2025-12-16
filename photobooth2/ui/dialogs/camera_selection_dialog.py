"""
Modal dialog to switch between DSLR and webcam sources.
"""

from __future__ import annotations

from typing import Dict

from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QRadioButton,
    QVBoxLayout,
)

from photobooth2.controller.app_controller import AppController


class CameraSelectionDialog(QDialog):
    def __init__(self, controller: AppController, parent=None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.manager = controller.camera_manager

        self.setWindowTitle("Kamera auswählen")
        self.setModal(True)

        self._button_group = QButtonGroup(self)
        self._radio_webcams: Dict[int, QRadioButton] = {}
        self._dslr_radio: QRadioButton | None = None
        self._ok_button: QDialogButtonBox | None = None

        self._build_ui()
        self._populate_options()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Wähle eine Kameraquelle:"))

        self._options_container = QVBoxLayout()
        layout.addLayout(self._options_container)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._ok_button = buttons

    def _populate_options(self) -> None:
        # Clear previous buttons
        for button in self._button_group.buttons():
            self._button_group.removeButton(button)
            button.deleteLater()
        while self._options_container.count():
            item = self._options_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._radio_webcams.clear()
        self._dslr_radio = None

        # Refresh detection state
        self.controller.refresh_camera_list()

        current_type = self.manager.get_active_type()
        current_webcam = self.manager.active_webcam_index

        # DSLR
        if self.manager.dslr_available:
            dslr_radio = QRadioButton("DSLR (gPhoto2)")
            self._button_group.addButton(dslr_radio)
            self._options_container.addWidget(dslr_radio)
            self._dslr_radio = dslr_radio
            if current_type == "dslr":
                dslr_radio.setChecked(True)

        # Webcams
        for index in self.manager.webcams:
            label = f"Webcam {index}"
            radio = QRadioButton(label)
            self._button_group.addButton(radio)
            self._options_container.addWidget(radio)
            self._radio_webcams[index] = radio
            if current_type == "webcam" and current_webcam == index:
                radio.setChecked(True)

        if not self._button_group.buttons():
            self._options_container.addWidget(QLabel("Keine Kameras gefunden."))
            if self._ok_button:
                self._ok_button.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def _on_accept(self) -> None:
        selected = self._button_group.checkedButton()
        if not selected:
            QMessageBox.warning(self, "Kamera", "Bitte wähle eine Kamera aus.")
            return

        # Determine selection
        if self._dslr_radio and selected is self._dslr_radio:
            success = self.controller.select_dslr()
            if not success:
                QMessageBox.critical(self, "Kamera", "DSLR konnte nicht aktiviert werden.")
                return
            self.accept()
            return

        for index, radio in self._radio_webcams.items():
            if selected is radio:
                success = self.controller.select_webcam(index)
                if not success:
                    QMessageBox.critical(
                        self, "Kamera", f"Webcam {index} konnte nicht aktiviert werden."
                    )
                    return
                self.accept()
                return

        QMessageBox.warning(self, "Kamera", "Ungültige Auswahl.")
