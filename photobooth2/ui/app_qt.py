"""
Qt application bootstrap: load settings, wire
controller launch the main window.
"""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication

from photobooth2.config.loader import Settings, load_settings
from photobooth2.controller.app_controller import AppController
from photobooth2.devices.camera_manager import CameraManager
from photobooth2.devices.dslr_camera import DslrCamera
from photobooth2.devices.external_display import ExternalDisplay
from photobooth2.devices.printer import Printer
from photobooth2.features.collage_capture import CollageCaptureFeature
from photobooth2.features.gallery import GalleryFeature
from photobooth2.features.single_photo import SinglePhotoFeature
from photobooth2.features.slideshow import SlideshowFeature
from photobooth2.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def _build_controller(settings: Settings) -> AppController:
    camera_manager = CameraManager()
    dslr_camera = DslrCamera(settings.output_dir)
    printer = Printer()
    gallery_feature = GalleryFeature(settings.output_dir)
    single_photo_feature = SinglePhotoFeature(camera_manager, settings.output_dir)
    collage_feature = CollageCaptureFeature(
        camera_manager,
        settings.output_dir,
        settings.collage_count,
        settings.collage_overlay_path,
    )
    external_display = ExternalDisplay()
    slideshow_feature = SlideshowFeature(gallery_feature, external_display)

    return AppController(
        settings=settings,
        camera_manager=camera_manager,
        dslr_camera=dslr_camera,
        printer=printer,
        gallery_feature=gallery_feature,
        single_photo_feature=single_photo_feature,
        collage_feature=collage_feature,
        slideshow_feature=slideshow_feature,
    )


def run_app() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    app = QApplication(sys.argv)
    settings = load_settings()
    controller = _build_controller(settings)

    window = MainWindow(settings, controller)
    window.showFullScreen()

    logger.info("Photobooth 2.0 started")
    sys.exit(app.exec())
