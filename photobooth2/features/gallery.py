"""
Gallery feature that lists and loads captured assets.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

from PIL import Image

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

    def load_image(self, path: Path) -> Image.Image | None:
        """
        Load an image via Pillow. Returns None if loading fails.
        """
        try:
            return Image.open(path)
        except FileNotFoundError:
            logger.error("Requested image missing: %s", path)
        except Exception as exc:
            logger.error("Failed to load image %s: %s", path, exc)
        return None

    def delete_image(self, path: Path) -> None:
        """
        Delete an image file from disk. Does not raise if file is missing.
        """
        try:
            path.unlink()
            logger.info("Deleted image %s", path)
        except FileNotFoundError:
            logger.warning("Tried to delete non-existent image %s", path)
        except OSError as exc:
            logger.error("Failed to delete image %s: %s", path, exc)
            raise
