"""
Settings loader that maps configuration from TOML into a typed Settings object.
"""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    event_name: str = "Photobooth 2.0"
    event_date: str = ""
    qr_url: str = "https://example.com"
    output_dir: Path = Path("output")
    collage_count: int = 4
    collage_overlay_path: Path | None = None


def load_settings(settings_path: str | Path | None = None) -> Settings:
    """
    Load settings from a TOML file. Falls back to defaults when the file is
    missing or invalid so the app can still start in a safe state.
    """

    path = Path(settings_path) if settings_path else Path(__file__).with_name("settings.toml")
    settings = Settings()

    if not path.exists():
        logger.warning("Settings file %s not found, using defaults", path)
        _ensure_output_dir(settings.output_dir)
        return settings

    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        logger.error("Failed to parse settings %s: %s", path, exc)
        _ensure_output_dir(settings.output_dir)
        return settings

    event = data.get("event", {})
    paths = data.get("paths", {})
    collage = data.get("collage", {})

    settings.event_name = str(event.get("name", settings.event_name))
    settings.event_date = str(event.get("date", settings.event_date))
    settings.qr_url = str(event.get("qr_url", settings.qr_url))

    settings.output_dir = Path(paths.get("output_dir", settings.output_dir)).expanduser().resolve()
    settings.collage_count = int(collage.get("photo_count", settings.collage_count))

    overlay = collage.get("overlay")
    settings.collage_overlay_path = Path(overlay).expanduser().resolve() if overlay else None

    _ensure_output_dir(settings.output_dir)
    return settings


def _ensure_output_dir(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.error("Could not create output directory %s: %s", path, exc)
