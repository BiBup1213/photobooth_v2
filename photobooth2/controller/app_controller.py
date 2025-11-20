"""
Central controller that wires UI events to domain features and devices.
"""
from __future__ import annotations

import logging
from pathlib import Path

from photobooth2.config.loader import Settings
from photobooth2.devices.dslr_camera import DslrCamera
from photobooth2.devices.printer import Printer
from photobooth2.features.collage_capture import CollageCaptureFeature
from photobooth2.features.gallery import GalleryFeature
from photobooth2.features.single_photo import SinglePhotoFeature
from photobooth2.features.slideshow import SlideshowFeature

logger = logging.getLogger(__name__)


class AppController:
    def __init__(
        self,
        settings: Settings,
        camera: DslrCamera,
        printer: Printer,
        gallery_feature: GalleryFeature,
        single_photo_feature: SinglePhotoFeature,
        collage_feature: CollageCaptureFeature,
        slideshow_feature: SlideshowFeature,
    ) -> None:
        self.settings = settings
        self.camera = camera
        self.printer = printer
        self.gallery = gallery_feature
        self.single_photo = single_photo_feature
        self.collage = collage_feature
        self.slideshow = slideshow_feature

        self.last_captured: Path | None = None

    def capture_single_photo(self) -> Path | None:
        try:
            self.last_captured = self.single_photo.capture()
            return self.last_captured
        except Exception:
            logger.exception("Single photo capture failed")
            return None

    def capture_collage(self) -> Path | None:
        try:
            self.last_captured = self.collage.capture_collage()
            return self.last_captured
        except Exception:
            logger.exception("Collage capture failed")
            return None

    def list_gallery(self) -> list[Path]:
        return self.gallery.list_images()

    def print_last_capture(self) -> bool:
        if not self.last_captured:
            logger.warning("No capture available to print")
            return False
        return self.print_image(self.last_captured)

    def print_image(self, image: Path) -> bool:
        try:
            self.printer.print_image(image)
            return True
        except Exception:
            logger.exception("Printing failed")
            return False

    def start_slideshow(self) -> None:
        self.slideshow.start()
