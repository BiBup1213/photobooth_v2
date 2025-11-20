"""
Simple printer abstraction using the system spooler (e.g. CUPS/lp).
For v1 this is a stub that only logs the intent to print.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Printer:
    def __init__(self, queue_name: str | None = None) -> None:
        self.queue_name = queue_name

    def print_image(self, image_path: Path) -> None:
        """Send an image to the printer queue (stubbed)."""
        logger.info("Print requested for %s%s", image_path, f" on {self.queue_name}" if self.queue_name else "")
        # Real implementation would call `lp` or CUPS APIs.
