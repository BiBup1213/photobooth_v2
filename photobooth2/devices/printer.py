"""
Simple printer abstraction using the system spooler (e.g. CUPS / lp).
"""

from __future__ import annotations

import logging
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)


class Printer:
    def __init__(self, queue_name: str | None = None) -> None:
        self.queue_name = queue_name

    def print_image(self, image_path: Path) -> None:
        """
        Send an image to the printer queue. Raises on failure so callers can react.

        Raises:
            FileNotFoundError: if the image does not exist.
            subprocess.CalledProcessError / OSError: if lp fails.
        """
        if not image_path.exists():
            logger.error("Image to print not found: %s", image_path)
            raise FileNotFoundError(f"Image not found: {image_path}")

        cmd: list[str] = ["lp"]
        if self.queue_name:
            cmd.extend(["-d", self.queue_name])
        cmd.append(str(image_path))

        logger.info(
            "Sending %s to printer%s",
            image_path,
            f" (queue {self.queue_name})" if self.queue_name else "",
        )
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode(errors="ignore") if exc.stderr else str(exc)
            logger.error("Printing failed: %s", stderr)
            raise
        except OSError as exc:
            logger.error("Could not execute lp: %s", exc)
            raise

        logger.info("Print job submitted for %s", image_path)
