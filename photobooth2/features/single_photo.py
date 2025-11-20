"""
Single photo capture workflow independent of UI concerns.
"""
from __future__ import annotations

import logging
from pathlib import Path

from photobooth2.devices.dslr_camera import DslrCamera

logger = logging.getLogger(__name__)


class SinglePhotoFeature:
    def __init__(self, camera: DslrCamera) -> None:
        self.camera = camera

    def capture(self) -> Path:
        logger.info("Starting single photo capture")
        return self.camera.capture_photo()
