"""
Slideshow feature that would render images on a secondary display.
"""

from __future__ import annotations

import logging
from pathlib import Path

from photobooth2.devices.external_display import ExternalDisplay
from photobooth2.features.gallery import GalleryFeature

logger = logging.getLogger(__name__)


class SlideshowFeature:
    def __init__(self, gallery: GalleryFeature, external_display: ExternalDisplay) -> None:
        self.gallery = gallery
        self.external_display = external_display

    def start(self) -> None:
        """
        Trigger slideshow on external display if available.
        Currently still a stub for the actual rendering logic.
        """
        if not self.external_display.is_available():
            logger.info("No external display detected; slideshow disabled")
            return
        logger.info("Starting slideshow on external display (stub)")
        self.external_display.show_slideshow()

    def get_slideshow_sequence(self, limit: int = 50) -> list[Path]:
        """
        Return the newest images for slideshow consumption.
        """
        images = self.gallery.list_images()
        return images[:limit]
