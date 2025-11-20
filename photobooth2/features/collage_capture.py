"""
Collage capture workflow. Currently a stub that will later stitch images with Pillow.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from photobooth2.devices.dslr_camera import DslrCamera

logger = logging.getLogger(__name__)


class CollageCaptureFeature:
    def __init__(self, camera: DslrCamera, output_dir: Path, collage_count: int) -> None:
        self.camera = camera
        self.output_dir = output_dir
        self.collage_count = collage_count

    def capture_collage(self) -> Path:
        logger.info("Starting collage capture (%s photos)", self.collage_count)
        photos = [self.camera.capture_photo() for _ in range(self.collage_count)]
        collage_path = self.output_dir / f"collage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        collage_path.touch()
        logger.info("Created placeholder collage %s from %s", collage_path.name, photos)
        return collage_path
