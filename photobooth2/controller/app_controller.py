"""
Central controller that wires UI events to domain features and devices.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from photobooth2.config.loader import Settings
from photobooth2.devices.camera_manager import CameraManager
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
        camera_manager: CameraManager,
        dslr_camera: DslrCamera,
        printer: Printer,
        gallery_feature: GalleryFeature,
        single_photo_feature: SinglePhotoFeature,
        collage_feature: CollageCaptureFeature,
        slideshow_feature: SlideshowFeature,
    ) -> None:
        self.settings = settings
        self.camera_manager = camera_manager
        self.dslr = dslr_camera
        self.printer = printer
        self.gallery = gallery_feature
        self.single_photo = single_photo_feature
        self.collage = collage_feature
        self.slideshow = slideshow_feature

        self.last_captured: Path | None = None
        self._camera_change_callbacks: list[Callable[[str | None], None]] = []
        self.camera_available = False

        self._initialize_camera()

    def capture_single_photo(self) -> Path | None:
        if not self.has_active_camera():
            logger.warning("Capture requested but no active camera available")
            return None
        try:
            self.last_captured = self.single_photo.capture()
            return self.last_captured
        except Exception:
            logger.exception("Single photo capture failed")
            return None

    def capture_collage(self) -> Path | None:
        if not self.has_active_camera():
            logger.warning("Collage capture requested but no active camera available")
            return None
        try:
            self.last_captured = self.collage.capture_collage()
            return self.last_captured
        except Exception:
            logger.exception("Collage capture failed")
            return None

    def compose_collage_from_photos(self, photos: list[Path]) -> Path | None:
        try:
            self.last_captured = self.collage.compose_from_photos(photos)
            return self.last_captured
        except Exception:
            logger.exception("Collage composition failed")
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

    def delete_image(self, image: Path) -> bool:
        try:
            image.unlink()
            return True
        except Exception:
            logger.exception("Deleting image failed")
            return False

    def start_slideshow(self) -> None:
        self.slideshow.start()

    # --- Camera handling -------------------------------------------------
    def _initialize_camera(self) -> None:
        try:
            self.camera_manager.auto_select(self.dslr)
            self.camera_available = True
        except RuntimeError as exc:
            self.camera_available = False
            logger.warning("No camera detected at startup: %s", exc)

    def refresh_camera_list(self) -> None:
        self.camera_manager.refresh_devices()

    def select_dslr(self) -> bool:
        try:
            self.camera_manager.use_dslr(self.dslr)
            self.camera_available = True
            self._emit_camera_changed()
            return True
        except Exception:
            logger.exception("Switching to DSLR failed")
            return False

    def select_webcam(self, index: int) -> bool:
        try:
            self.camera_manager.use_webcam(index)
            self.camera_available = True
            self._emit_camera_changed()
            return True
        except Exception:
            logger.exception("Switching to webcam %s failed", index)
            return False

    def has_active_camera(self) -> bool:
        return self.camera_manager.get_active_type() is not None

    def on_camera_changed(self, callback: Callable[[str | None], None]) -> None:
        self._camera_change_callbacks.append(callback)

    def _emit_camera_changed(self) -> None:
        active = self.camera_manager.get_active_type()
        for callback in self._camera_change_callbacks:
            try:
                callback(active)
            except Exception as exc:
                logger.warning("Camera change callback failed: %s", exc)
