"""
Single photo capture workflow independent of UI concerns.
"""
from __future__ import annotations

import logging
from pathlib import Path

from photobooth2.devices.camera_manager import CameraManager

logger = logging.getLogger(__name__)


class SinglePhotoFeature:
    def __init__(self, camera_manager: CameraManager, output_dir: Path) -> None:
        self.camera_manager = camera_manager
        self.output_dir = output_dir

    def capture(self) -> Path:
        logger.info("Starting single photo capture")
        return self.camera_manager.capture_photo(self.output_dir)
