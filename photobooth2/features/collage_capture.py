"""
Collage capture workflow using Pillow to compose multiple photographs.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from PIL import Image, ImageOps

from photobooth2.devices.dslr_camera import DslrCamera

logger = logging.getLogger(__name__)


class CollageCaptureFeature:
    def __init__(
        self,
        camera: DslrCamera,
        output_dir: Path,
        collage_count: int,
        collage_overlay_path: Path | None = None,
    ) -> None:
        self.camera = camera
        self.output_dir = output_dir
        self.collage_count = collage_count
        self.collage_overlay_path = collage_overlay_path

    def capture_collage(self) -> Path:
        """
        Capture several photos and combine them into a simple collage.

        Returns:
            Path to the saved collage image.
        """
        logger.info("Starting collage capture (%s photos)", self.collage_count)

        photos: List[Path] = []
        for index in range(self.collage_count):
            logger.info(
                "Capturing collage photo %s/%s", index + 1, self.collage_count
            )
            photos.append(self.camera.capture_photo())

        images = self._load_and_normalize(photos)
        collage = self._compose(images)

        if self.collage_overlay_path and self.collage_overlay_path.exists():
            collage = self._apply_overlay(collage, self.collage_overlay_path)

        collage_path = self.output_dir / f"collage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        collage.save(collage_path, format="JPEG", quality=90)
        logger.info("Collage saved to %s", collage_path)
        return collage_path

    def _load_and_normalize(self, photos: Iterable[Path]) -> list[Image.Image]:
        """
        Open images and scale them down to a sane size for collage composition.
        """
        normalized: list[Image.Image] = []
        for photo in photos:
            img = Image.open(photo).convert("RGB")
            img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
            normalized.append(img)
        return normalized

    def _compose(self, images: list[Image.Image]) -> Image.Image:
        """
        Compose images into a 2x2-style collage.
        With 3 images the last one spans the bottom row.
        Only the first 4 images are used.
        """
        if not images:
            raise ValueError("No images provided for collage")

        # use at most 4 images
        images = images[:4]
        count = len(images)

        # Base cell size derived from first image to preserve decent quality.
        cell_w, cell_h = images[0].size
        cell_w = max(cell_w, 800)
        cell_h = max(cell_h, 800)

        canvas_w = cell_w * 2
        canvas_h = cell_h * 2

        collage = Image.new("RGB", (canvas_w, canvas_h), color=(245, 245, 245))

        if count == 1:
            positions = [(0, 0)]
            sizes = [(canvas_w, canvas_h)]
        elif count == 2:
            positions = [(0, 0), (cell_w, 0)]
            sizes = [(cell_w, canvas_h), (cell_w, canvas_h)]
        elif count == 3:
            positions = [
                (0, 0),
                (cell_w, 0),
                (0, cell_h),
            ]
            sizes = [
                (cell_w, cell_h),
                (cell_w, cell_h),
                (canvas_w, cell_h),
            ]
        else:  # 4 or more -> 2x2 grid
            positions = [
                (0, 0),
                (cell_w, 0),
                (0, cell_h),
                (cell_w, cell_h),
            ]
            sizes = [
                (cell_w, cell_h),
                (cell_w, cell_h),
                (cell_w, cell_h),
                (cell_w, cell_h),
            ]

        for img, pos, size in zip(images, positions, sizes):
            fitted = ImageOps.contain(img, size, Image.Resampling.LANCZOS)
            x = pos[0] + (size[0] - fitted.size[0]) // 2
            y = pos[1] + (size[1] - fitted.size[1]) // 2
            collage.paste(fitted, (x, y))

        return collage

    def _apply_overlay(self, collage: Image.Image, overlay_path: Path) -> Image.Image:
        """
        Apply an RGBA overlay over the completed collage.
        """
        try:
            overlay = Image.open(overlay_path).convert("RGBA")
        except Exception as exc:  # Pillow can raise multiple error types
            logger.error("Failed to load overlay %s: %s", overlay_path, exc)
            return collage

        overlay = overlay.resize(collage.size, Image.Resampling.LANCZOS)
        base = collage.convert("RGBA")
        composed = Image.alpha_composite(base, overlay)
        return composed.convert("RGB")
