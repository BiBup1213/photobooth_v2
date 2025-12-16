"""
Abstraction for handling a secondary display.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ExternalDisplay:
    def is_available(self) -> bool:
        logger.debug("External display availability check (stub)")
        return False

    def show_slideshow(self) -> None:
        logger.info("Requested to show slideshow on external display (stub)")
