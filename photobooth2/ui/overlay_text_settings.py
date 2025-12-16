"""
Dialog for editing the two overlay text lines shown under the QR code.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from photobooth2.ui.overlay_text_store import (
    load_overlay_text,
    save_overlay_text,
)


class OverlayTextSettingsDialog(QDialog):
    overlay_text_saved = pyqtSignal(str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Overlay Text")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        line1, line2 = load_overlay_text()

        self._line1_edit = QLineEdit(line1)
        self._line1_edit.setMaxLength(40)
        self._line1_edit.setPlaceholderText("Namen")

        self._line2_edit = QLineEdit(line2)
        self._line2_edit.setMaxLength(30)
        self._line2_edit.setPlaceholderText("Datum")

        form.addRow("Namen", self._line1_edit)
        form.addRow("Datum", self._line2_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_save(self) -> None:
        line1 = self._line1_edit.text()
        line2 = self._line2_edit.text()
        save_overlay_text(line1, line2)
        self.overlay_text_saved.emit(line1, line2)
        self.accept()
