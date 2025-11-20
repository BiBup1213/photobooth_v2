"""
Device abstraction for a DSLR camera controlled via gphoto2.
For now this stub only simulates a capture and writes a placeholder file.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DslrCamera:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def capture_photo(self) -> Path:
        """
        Capture a photo and return the saved file path.
        This placeholder creates an empty file so the UI remains testable without hardware.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.output_dir / f"photo_{timestamp}.jpg"
        logger.info("Simulating photo capture to %s", target)
        try:
            target.touch()
        except OSError as exc:
            logger.error("Failed to write placeholder photo: %s", exc)
            raise
        return target
