"""
Gallery feature that lists captured assets.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

logger = logging.getLogger(__name__)


class GalleryFeature:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def list_images(self) -> List[Path]:
        """
        Return image files sorted by modification time (newest first).
        """
        if not self.output_dir.exists():
            logger.warning("Output directory %s does not exist", self.output_dir)
            return []

        candidates: Iterable[Path] = self.output_dir.iterdir()
        images = [path for path in candidates if path.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        return sorted(images, key=lambda p: p.stat().st_mtime, reverse=True)
