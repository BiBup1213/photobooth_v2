"""
Start screen showing floral header graphic and icon-only action buttons.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from photobooth2.config.loader import Settings
from photobooth2.ui.overlay_text_store import (
    load_andrea_bellarosa_font,
    load_overlay_text,
)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

logger = logging.getLogger(__name__)


class StartScreen(QWidget):
    photo_requested = pyqtSignal()
    collage_requested = pyqtSignal()
    gallery_requested = pyqtSignal()

    def __init__(self, settings: Settings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings

        # complete window background beige

        self._floral_pixmap: QPixmap | None = self._load_pixmap(
            ASSETS_DIR / "main_banner_floral.png"
        )
        self._qr_pixmap: QPixmap | None = self._load_pixmap(ASSETS_DIR / "qr" / "qr_gallery.png")
        self._floral_label: QLabel | None = None
        self._qr_label: QLabel | None = None
        self._banner_container: QWidget | None = None
        self._title_label: QLabel | None = None
        self._subtitle_label: QLabel | None = None
        self._overlay_font_family: str | None = self._load_overlay_font()

        self._build_ui()
        self._update_floral_pixmap()
        self._position_qr()
        self.reload_overlay_text()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 40, 80, 40)
        layout.setSpacing(20)

        # -------------------------------------------------
        # FLORAL HEADER (PNG centered, no frame)
        # -------------------------------------------------
        self._banner_container = QWidget()
        self._banner_container.setMinimumHeight(420)
        self._banner_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        banner_stack = QStackedLayout(self._banner_container)
        banner_stack.setContentsMargins(0, 0, 0, 0)
        banner_stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self._floral_label = QLabel()
        self._floral_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._floral_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._floral_label.setStyleSheet("background: transparent;")

        banner_stack.addWidget(self._floral_label)

        self._qr_label = QLabel(self._banner_container)
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._qr_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._qr_label.setStyleSheet("background: transparent; border: none;")
        self._qr_label.raise_()

        self._title_label = QLabel(self._banner_container)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._title_label.setStyleSheet("background: transparent; color: #94480d; border: none;")
        self._title_label.setFixedHeight(45)

        self._subtitle_label = QLabel(self._banner_container)
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._subtitle_label.setStyleSheet("background: transparent; color: #94480d; border: none;")
        self._subtitle_label.setFixedHeight(30)

        layout.addWidget(self._banner_container, stretch=3)

        # -------------------------------------------------
        # BUTTONS (icon-only, centered)
        # -------------------------------------------------
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 40)
        buttons_layout.setSpacing(60)

        gallery_btn = self._create_action_button(ASSETS_DIR / "btn_gallery.png", "Galerie")
        photo_btn = self._create_action_button(ASSETS_DIR / "btn_photo.png", "Foto")
        collage_btn = self._create_action_button(ASSETS_DIR / "btn_collage.png", "Collage")

        gallery_btn.clicked.connect(self.gallery_requested.emit)
        photo_btn.clicked.connect(self.photo_requested.emit)
        collage_btn.clicked.connect(self.collage_requested.emit)

        buttons_layout.addStretch(1)
        buttons_layout.addWidget(gallery_btn)
        buttons_layout.addWidget(photo_btn)
        buttons_layout.addWidget(collage_btn)
        buttons_layout.addStretch(1)

        layout.addLayout(buttons_layout, stretch=1)

    # ------------------------------------------------------------------
    def _create_action_button(self, icon_path: Path, fallback_text: str) -> QPushButton:
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # fixed icon tile size
        btn.setMinimumSize(160, 160)
        btn.setMaximumSize(180, 180)
        btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        icon = self._load_icon(icon_path)
        if icon:
            btn.setIcon(icon)
            btn.setIconSize(QSize(140, 140))
            btn.setText("")
        else:
            btn.setText(fallback_text)
            btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        # pure icon, no background
        btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
            }
            """
        )

        return btn

    # ------------------------------------------------------------------
    def _load_pixmap(self, path: Path) -> QPixmap | None:
        if not path.exists():
            return None
        pixmap = QPixmap(str(path))
        return pixmap if not pixmap.isNull() else None

    def _load_icon(self, path: Path) -> QIcon | None:
        pix = self._load_pixmap(path)
        if pix is None:
            return None
        icon = QIcon(pix)
        return icon if not icon.isNull() else None

    # ------------------------------------------------------------------
    def _update_floral_pixmap(self) -> None:
        if not self._floral_label:
            return
        if not self._floral_pixmap:
            self._floral_label.clear()
            return

        size = self._floral_label.size()
        if size.width() <= 0 or size.height() <= 0:
            return

        scaled = self._floral_pixmap.scaled(
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._floral_label.setPixmap(scaled)

    def _position_qr(self) -> None:
        if not self._qr_label:
            return
        if not self._qr_pixmap:
            self._qr_label.clear()
            self._qr_label.resize(0, 0)
            return
        if not self._floral_label:
            return

        rendered = self._floral_label.pixmap()
        if rendered is None or rendered.isNull():
            self._qr_label.clear()
            self._qr_label.resize(0, 0)
            return

        label_size = self._floral_label.size()
        pm_size = rendered.size()
        pm_w, pm_h = pm_size.width(), pm_size.height()
        if pm_w <= 0 or pm_h <= 0:
            self._qr_label.clear()
            self._qr_label.resize(0, 0)
            return

        off_x = (label_size.width() - pm_w) // 2
        off_y = (label_size.height() - pm_h) // 2

        qr_size = int(pm_w * 0.26)
        qr_size = max(120, min(qr_size, 320))

        scaled_qr = self._qr_pixmap.scaled(
            QSize(qr_size, qr_size),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._qr_label.setPixmap(scaled_qr)
        self._qr_label.resize(scaled_qr.size())

        slot_center_x = off_x + int(pm_w * 0.50)
        slot_center_y = off_y + int(pm_h * 0.36)

        top_left_x = slot_center_x - scaled_qr.width() // 2
        top_left_y = slot_center_y - scaled_qr.height() // 2

        self._qr_label.move(top_left_x, top_left_y)
        self._qr_label.raise_()

        text_width = max(qr_size, int(pm_w * 1.00))
        text_spacing = 30
        text_top = top_left_y + scaled_qr.height() + 20

        if self._title_label:
            self._title_label.resize(text_width, self._title_label.height())
            self._title_label.move(slot_center_x - text_width // 2, text_top)
            self._title_label.raise_()
        if self._subtitle_label:
            sub_y = text_top
            if self._title_label:
                sub_y += self._title_label.height() + text_spacing
            self._subtitle_label.resize(text_width, self._subtitle_label.height())
            self._subtitle_label.move(slot_center_x - text_width // 2, sub_y)
            self._subtitle_label.raise_()

    def reload_overlay_text(self) -> None:
        line1, line2 = load_overlay_text()
        if self._title_label:
            self._title_label.setText(line1)
            if self._overlay_font_family:
                self._title_label.setFont(QFont(self._overlay_font_family, 26))
        if self._subtitle_label:
            self._subtitle_label.setText(line2)
            if self._overlay_font_family:
                self._subtitle_label.setFont(QFont(self._overlay_font_family, 16))

    def _load_overlay_font(self) -> str | None:
        try:
            return load_andrea_bellarosa_font()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Could not load overlay font: %s", exc)
            return None

    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_floral_pixmap()
        self._position_qr()
