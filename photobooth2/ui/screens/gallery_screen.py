"""
Gallery screen with grid view and single-image detail view.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class GalleryScreen(QWidget):
    back_requested = pyqtSignal()
    print_requested = pyqtSignal(Path)
    delete_requested = pyqtSignal(Path)
    image_selected = pyqtSignal(Path)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._images: List[Path] = []
        self._current: Path | None = None
        self._current_pixmap: QPixmap | None = None

        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 80, 24, 16)
        root.setSpacing(8)

        self._stack = QStackedWidget(self)
        root.addWidget(self._stack, 1)

        # --- Grid-Ansicht --------------------------------------------------
        grid_page = QWidget()
        grid_layout = QVBoxLayout(grid_page)
        grid_layout.setContentsMargins(8, 0, 8, 0)
        grid_layout.setSpacing(8)

        self._empty_label = QLabel("Noch keine Bilder vorhanden.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #6d5a44;")
        font = QFont()
        font.setPointSize(14)
        self._empty_label.setFont(font)

        self._list = QListWidget()
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.setSpacing(12)
        self._list.setIconSize(QSize(220, 220))
        self._list.setUniformItemSizes(True)
        self._list.setStyleSheet(
            """
            QListWidget {
                border: none;
                background: transparent;
            }
            """
        )
        self._list.itemActivated.connect(self._on_item_activated)
        self._list.itemClicked.connect(self._on_item_activated)

        grid_layout.addWidget(self._empty_label)
        grid_layout.addWidget(self._list, 1)

        # Bottom bar for gallery back button with padding
        grid_buttons = QHBoxLayout()
        grid_buttons.setContentsMargins(12, 8, 12, 12)
        back_icon = self._load_icon("back.png")
        self._grid_back_btn = self._create_icon_button(back_icon)
        self._grid_back_btn.clicked.connect(self.back_requested.emit)
        grid_buttons.addWidget(self._grid_back_btn, 0, Qt.AlignmentFlag.AlignLeft)
        grid_buttons.addStretch(1)

        grid_layout.addLayout(grid_buttons)

        self._stack.addWidget(grid_page)

        # --- Detail-Ansicht -----------------------------------------------
        detail_page = QWidget()
        detail_layout = QVBoxLayout(detail_page)
        detail_layout.setContentsMargins(16, 72, 16, 16)
        detail_layout.setSpacing(12)

        self._detail_image = QLabel()
        self._detail_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._detail_image.setMinimumHeight(0)

        # Bottom-Bar mit Zurück/Drucken/Löschen
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(12, 8, 12, 12)
        self._detail_back_btn = self._create_icon_button(self._load_icon("back.png"))
        self._detail_back_btn.clicked.connect(self._show_grid)

        self._print_btn = self._create_icon_button(self._load_icon("print.png"))
        self._delete_btn = self._create_icon_button(self._load_icon("delete.png"))

        self._print_btn.clicked.connect(self._emit_print_current)
        self._delete_btn.clicked.connect(self._emit_delete_current)

        bottom_bar.addWidget(self._detail_back_btn, 0, Qt.AlignmentFlag.AlignLeft)
        bottom_bar.addStretch(1)
        bottom_bar.addWidget(self._print_btn, 0, Qt.AlignmentFlag.AlignRight)
        bottom_bar.addWidget(self._delete_btn, 0, Qt.AlignmentFlag.AlignRight)

        detail_layout.addWidget(self._detail_image, 1)
        detail_layout.addLayout(bottom_bar)

        self._stack.addWidget(detail_page)

        self._show_grid()

    def _create_icon_button(self, icon: QIcon | None) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(64, 64)
        if icon:
            btn.setIcon(icon)
            btn.setIconSize(QSize(32, 32))
        btn.setStyleSheet(
            """
            QPushButton {
                background-color: #5a7a6b;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #6c8c7d;
            }
            QPushButton:pressed {
                background-color: #4a6a5b;
            }
            """
        )
        return btn

    def _load_icon(self, filename: str) -> QIcon | None:
        path = ASSETS_DIR / filename
        return QIcon(str(path)) if path.exists() else None

    # ------------------------------------------------------------------ API

    def set_images(self, images: List[Path]) -> None:
        """Populate the grid with the given image paths."""
        self._images = [p for p in images if p.exists()]
        self._list.clear()

        if not self._images:
            self._empty_label.show()
        else:
            self._empty_label.hide()
            for path in self._images:
                pixmap = QPixmap(str(path))
                if pixmap.isNull():
                    continue
                icon_pixmap = pixmap.scaled(
                    self._list.iconSize(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                item = QListWidgetItem()
                item.setIcon(QIcon(icon_pixmap))
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                item.setToolTip(path.name)
                self._list.addItem(item)

        self._show_grid()

    def remove_image(self, image: Path) -> None:
        """Remove an image from the grid after deletion."""
        image_str = str(image)
        # Liste aktualisieren
        self._images = [p for p in self._images if str(p) != image_str]

        for i in range(self._list.count() - 1, -1, -1):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == image_str:
                self._list.takeItem(i)

        if not self._images:
            self._empty_label.show()
            self._show_grid()

    # ---------------------------------------------------------------- Events

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        path = Path(data)
        self.image_selected.emit(path)

    def _show_grid(self) -> None:
        self._stack.setCurrentIndex(0)
        # Grid back button stays visible
        self._current = None
        self._current_pixmap = None
        self._detail_image.clear()

    def show_detail(self, path: Path) -> None:
        if not path.exists():
            logger.warning("Detail image missing: %s", path)
            return

        self._current = path
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            logger.warning("Failed to load detail image: %s", path)
            return

        self._current_pixmap = pixmap
        self._update_detail_pixmap()

        self._stack.setCurrentIndex(1)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._update_detail_pixmap()

    def _update_detail_pixmap(self) -> None:
        if not self._current_pixmap:
            return
        label_size = self._detail_image.size()
        if label_size.isEmpty():
            label_size = self._stack.size()
            if label_size.isEmpty():
                return
        scaled = self._current_pixmap.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._detail_image.setPixmap(scaled)

    # ---------------------------------------------------------------- Actions

    def _emit_print_current(self) -> None:
        if self._current is not None:
            self.print_requested.emit(self._current)

    def _emit_delete_current(self) -> None:
        if self._current is not None:
            self.delete_requested.emit(self._current)
