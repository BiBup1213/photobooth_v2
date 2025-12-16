"""
Device abstraction for a DSLR camera controlled via gphoto2.
"""

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
import shutil
import subprocess

logger = logging.getLogger(__name__)


class DslrCamera:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def capture_photo(self) -> Path:
        """
        Capture a photo using gphoto2 and return the saved file path.

        Raises:
            FileNotFoundError: if gphoto2 is not installed or not on PATH.
            subprocess.CalledProcessError / OSError: wenn der gphoto2-Aufruf scheitert.
        """
        gphoto = shutil.which("gphoto2")
        if not gphoto:
            logger.error("gphoto2 not found on PATH; cannot capture photo")
            raise FileNotFoundError("gphoto2 not installed or not on PATH")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.output_dir / f"photo_{timestamp}.jpg"

        command = [
            gphoto,
            "--capture-image-and-download",
            "--force-overwrite",
            "--filename",
            str(target),
        ]

        logger.info("Capturing photo to %s", target)
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode(errors="ignore") if exc.stderr else str(exc)
            logger.error("gphoto2 capture failed: %s", stderr)
            raise
        except OSError as exc:
            logger.error("Could not execute gphoto2: %s", exc)
            raise

        if not target.exists():
            logger.error("Expected captured file missing: %s", target)
            raise FileNotFoundError(f"Capture failed; file not found: {target}")

        logger.info("Photo saved to %s", target)
        return target
