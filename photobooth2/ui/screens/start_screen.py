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
    QSpacerItem,
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


class QrOverlayWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; border: none;")

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.qr_label.setStyleSheet("background: transparent; border: none;")
        self.qr_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.title_label.setStyleSheet("background: transparent; color: #94480d; border: none;")
        self.title_label.setWordWrap(False)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.subtitle_label.setStyleSheet(
            "background: transparent; color: #94480d; border: none;"
        )
        self.subtitle_label.setWordWrap(False)
        self.subtitle_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._qr_title_spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self._layout.addItem(self._qr_title_spacer)
        self._layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._title_subtitle_spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self._layout.addItem(self._title_subtitle_spacer)
        self._layout.addWidget(self.subtitle_label, alignment=Qt.AlignmentFlag.AlignHCenter)

    def set_qr_pixmap(self, pixmap: QPixmap) -> None:
        self.qr_label.setPixmap(pixmap)

    def clear_qr(self) -> None:
        self.qr_label.clear()

    def update_typography(self, qr_size: int, font_family: str | None) -> None:
        title_pt = self._clamp_int(int(qr_size * 0.16), 18, 32)
        subtitle_pt = self._clamp_int(int(qr_size * 0.11), 14, 22)

        if font_family:
            title_font = QFont(font_family, title_pt)
            title_font.setWeight(QFont.Weight.DemiBold)
            self.title_label.setFont(title_font)
            self.subtitle_label.setFont(QFont(font_family, subtitle_pt))
        else:
            title_font = QFont("Arial", title_pt)
            title_font.setWeight(QFont.Weight.DemiBold)
            self.title_label.setFont(title_font)
            self.subtitle_label.setFont(QFont("Arial", subtitle_pt))

    def update_spacing(self, qr_size: int) -> None:
        top_margin = self._clamp_int(int(qr_size * 0.04), 4, 14)
        gap_qr_to_title = self._clamp_int(int(qr_size * 0.04), 6, 14)
        gap_title_to_subtitle = self._clamp_int(int(qr_size * 0.06), 8, 18)
        left_offset = -self._clamp_int(int(qr_size * 0.03), 6, 14)

        self._layout.setContentsMargins(0, top_margin, 0, 0)
        self.title_label.setContentsMargins(left_offset, 0, 0, 0)
        self._qr_title_spacer.changeSize(
            0, gap_qr_to_title, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self._title_subtitle_spacer.changeSize(
            0, gap_title_to_subtitle, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self._layout.invalidate()

    @staticmethod
    def _clamp_int(value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(value, maximum))


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
        self._qr_pixmap: QPixmap | None = self._load_pixmap(
            ASSETS_DIR / "qr" / "qr_gallery.png"
        )
        self._floral_label: QLabel | None = None
        self._qr_overlay: QrOverlayWidget | None = None
        self._banner_container: QWidget | None = None
        self._overlay_container: QWidget | None = None
        self._root_layout: QVBoxLayout | None = None
        self._buttons_layout: QHBoxLayout | None = None
        self._action_buttons: list[QPushButton] = []
        self._title_label: QLabel | None = None
        self._subtitle_label: QLabel | None = None
        self._overlay_font_family: str | None = self._load_overlay_font()
        self._last_qr_size: int = 0

        self._build_ui()
        self._update_floral_pixmap()
        self._update_qr_pixmap_size()
        self.reload_overlay_text()

    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 40, 80, 40)
        layout.setSpacing(20)
        self._root_layout = layout

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

        self._overlay_container = QWidget()
        self._overlay_container.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self._overlay_container.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )
        self._overlay_container.setStyleSheet("background: transparent; border: none;")

        overlay_layout = QVBoxLayout(self._overlay_container)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(0)

        self._qr_overlay = QrOverlayWidget()
        self._title_label = self._qr_overlay.title_label
        self._subtitle_label = self._qr_overlay.subtitle_label

        overlay_layout.addStretch(45)
        overlay_layout.addWidget(
            self._qr_overlay,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
        )
        overlay_layout.addStretch(55)

        banner_stack.addWidget(self._overlay_container)
        self._overlay_container.raise_()

        layout.addWidget(self._banner_container, stretch=3)

        # -------------------------------------------------
        # BUTTONS (icon-only, centered)
        # -------------------------------------------------
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 40)
        buttons_layout.setSpacing(60)
        self._buttons_layout = buttons_layout

        gallery_btn = self._create_action_button(ASSETS_DIR / "btn_gallery.png", "Galerie")
        photo_btn = self._create_action_button(ASSETS_DIR / "btn_photo.png", "Foto")
        collage_btn = self._create_action_button(ASSETS_DIR / "btn_collage.png", "Collage")
        self._action_buttons = [gallery_btn, photo_btn, collage_btn]

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
    def _calculate_banner_size(self) -> int:
        if not self._banner_container:
            return 0

        width = self._banner_container.width()
        height = self._banner_container.height()
        if width <= 0 or height <= 0:
            return 0

        portrait = height > width

        # padding on BOTH sides (6% each side)
        pad_ratio = 0.06
        avail_w = int(width * (1.0 - 2.0 * pad_ratio))
        avail_h = int(height * (1.0 - 2.0 * pad_ratio))
        if avail_w <= 0 or avail_h <= 0:
            return 0

        limit = min(avail_w, avail_h)  # largest square that fits

        # keep same visual ratio across resolutions; slight orientation bias is ok
        scale = 0.95 if portrait else 0.98

        banner_size = int(limit * scale)

        # only a MIN clamp to avoid absurd tiny rendering
        return max(360, banner_size)


    def _update_floral_pixmap(self) -> None:
        if not self._floral_label:
            return
        if not self._floral_pixmap:
            self._floral_label.clear()
            return

        banner_size = self._calculate_banner_size()
        if banner_size <= 0:
            return

        scaled = self._floral_pixmap.scaled(
            QSize(banner_size, banner_size),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._floral_label.setPixmap(scaled)
        if self._overlay_container:
            self._overlay_container.raise_()

    def _update_qr_pixmap_size(self) -> None:
        if not self._qr_overlay:
            return
        if not self._qr_pixmap:
            self._qr_overlay.clear_qr()
            return

        banner_size = self._calculate_banner_size()
        if banner_size <= 0:
            return

        qr_size = int(banner_size * 0.25)
        qr_size = max(120, min(qr_size, 280))
        self._last_qr_size = qr_size

        scaled_qr = self._qr_pixmap.scaled(
            QSize(qr_size, qr_size),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._qr_overlay.set_qr_pixmap(scaled_qr)
        self._qr_overlay.update_spacing(qr_size)
        self._qr_overlay.update_typography(qr_size, self._overlay_font_family)

    def _update_root_margins(self) -> None:
        if not self._root_layout:
            return
        base = min(self.width(), self.height())
        if base <= 0:
            return
        side = max(20, min(int(base * 0.06), 80))
        top = max(20, min(int(base * 0.03), 40))
        self._root_layout.setContentsMargins(side, top, side, top)

    def _update_button_layout(self) -> None:
        if not self._buttons_layout or not self._action_buttons:
            return
        width = self.width()
        if width <= 0:
            return
        if width < 1100:
            spacing = 36
            min_size = 140
            max_size = 160
            icon_size = 120
        else:
            spacing = 60
            min_size = 160
            max_size = 180
            icon_size = 140

        self._buttons_layout.setSpacing(spacing)
        for button in self._action_buttons:
            button.setMinimumSize(min_size, min_size)
            button.setMaximumSize(max_size, max_size)
            button.setIconSize(QSize(icon_size, icon_size))

    def reload_overlay_text(self) -> None:
        line1, line2 = load_overlay_text()
        if self._title_label:
            self._title_label.setText(line1)
        if self._subtitle_label:
            self._subtitle_label.setText(line2)
        if self._qr_overlay and self._last_qr_size > 0:
            self._qr_overlay.update_typography(
                self._last_qr_size, self._overlay_font_family
            )

    def _load_overlay_font(self) -> str | None:
        try:
            return load_andrea_bellarosa_font()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Could not load overlay font: %s", exc)
            return None

    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_root_margins()
        self._update_floral_pixmap()
        self._update_qr_pixmap_size()
        self._update_button_layout()
