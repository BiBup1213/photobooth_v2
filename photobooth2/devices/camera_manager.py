"""
Central camera manager to switch between DSLR (gPhoto2) and webcam sources.
"""

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
import shutil
import subprocess
from typing import Callable

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover - optional dependency at runtime
    cv2 = None

from photobooth2.devices.dslr_camera import DslrCamera

logger = logging.getLogger(__name__)


class CameraManager:
    """
    Manages the active capture device and allows switching between DSLR and webcams.
    """

    def __init__(self, webcam_probe_count: int = 5) -> None:
        self.webcam_probe_count = max(1, webcam_probe_count)
        self.active_type: str | None = None  # "dslr" | "webcam" | None
        self.active_device: DslrCamera | object | None = None
        self.active_webcam_index: int | None = None
        self.webcams: list[int] = []
        self.dslr_available: bool = False
        self._callbacks: list[Callable[[str | None], None]] = []

    # ------------------------------------------------------------------ Detection
    def refresh_devices(self) -> None:
        """Probe connected cameras and store availability flags."""
        self.dslr_available = self._detect_dslr()
        self.webcams = self._detect_webcams()

    def _detect_dslr(self) -> bool:
        """
        Use `gphoto2 --auto-detect` to check if a DSLR is connected.
        """
        gphoto = shutil.which("gphoto2")
        if not gphoto:
            logger.info("gphoto2 not found on PATH; skipping DSLR detection")
            return False

        try:
            result = subprocess.run(
                [gphoto, "--auto-detect"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            logger.warning("gphoto2 auto-detect failed: %s", exc.stderr)
            return False
        except OSError as exc:
            logger.warning("Could not execute gphoto2: %s", exc)
            return False

        lines = (result.stdout or "").splitlines()
        # Output contains two header lines; any additional line hints at a camera.
        detected = len(lines) > 2
        logger.info("DSLR detected: %s", detected)
        return detected

    def _detect_webcams(self) -> list[int]:
        """
        Probe webcam indices using OpenCV. Returns a list of available indices.
        """
        if cv2 is None:
            logger.info("OpenCV not available; skipping webcam detection")
            return []

        found: list[int] = []
        for index in range(self.webcam_probe_count):
            cap = cv2.VideoCapture(index)
            try:
                if cap.isOpened():
                    found.append(index)
            finally:
                cap.release()

        logger.info("Detected webcams: %s", found)
        return found

    # ------------------------------------------------------------------ Switching
    def auto_select(self, dslr_instance: DslrCamera | None) -> None:
        """
        Select the best available camera.
        DSLR preferred, then first available webcam. Raises if none found.
        """
        self.refresh_devices()

        if self.dslr_available and dslr_instance:
            self.use_dslr(dslr_instance)
            return

        if self.webcams:
            self.use_webcam(self.webcams[0])
            return

        raise RuntimeError("No camera detected (DSLR or webcam)")

    def use_dslr(self, dslr_instance: DslrCamera) -> None:
        """Switch active device to DSLR."""
        if dslr_instance is None:
            raise ValueError("dslr_instance is required")

        self.release()
        self.active_type = "dslr"
        self.active_device = dslr_instance
        self.active_webcam_index = None
        logger.info("Switched active camera to DSLR")
        self._emit_camera_changed()

    def use_webcam(self, index: int) -> None:
        """Switch active device to the given webcam index."""
        if cv2 is None:
            raise RuntimeError("OpenCV (cv2) is required for webcam usage")

        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to open webcam index {index}")

        self.release()
        self.active_type = "webcam"
        self.active_device = cap
        self.active_webcam_index = index
        logger.info("Switched active camera to webcam %s", index)
        self._emit_camera_changed()

    def release(self) -> None:
        """Release the currently active webcam handle if any."""
        if self.active_type == "webcam" and self.active_device is not None:
            try:
                self.active_device.release()  # type: ignore[call-arg]
            except Exception as exc:
                logger.warning("Failed to release webcam: %s", exc)

        self.active_type = None
        self.active_device = None
        self.active_webcam_index = None

    # ------------------------------------------------------------------ Capture
    def capture_photo(self, output_dir: Path) -> Path:
        """
        Capture a photo with the active device.
        For DSLR, delegates to DslrCamera; for webcam, grabs a frame and saves it.
        """
        if self.active_type == "dslr" and isinstance(self.active_device, DslrCamera):
            return self.active_device.capture_photo()

        if self.active_type == "webcam":
            return self._capture_webcam_frame(output_dir)

        raise RuntimeError("No active camera selected")

    def _capture_webcam_frame(self, output_dir: Path) -> Path:
        if cv2 is None:
            raise RuntimeError("OpenCV (cv2) is required for webcam capture")
        if self.active_device is None:
            raise RuntimeError("Webcam not initialized")

        ret, frame = self.active_device.read()  # type: ignore[attr-defined]
        if not ret or frame is None:
            raise RuntimeError("Failed to read frame from webcam")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = output_dir / f"webcam_{timestamp}.jpg"

        success = cv2.imwrite(str(target), frame)
        if not success:
            raise RuntimeError(f"Failed to save webcam frame to {target}")

        logger.info("Captured webcam frame to %s", target)
        return target

    # ------------------------------------------------------------------ State
    def get_active_type(self) -> str | None:
        return self.active_type

    def get_active_device(self):
        return self.active_device

    def on_camera_changed(self, callback: Callable[[str | None], None]) -> None:
        """Register a callback invoked after the active camera changes."""
        self._callbacks.append(callback)

    def _emit_camera_changed(self) -> None:
        for callback in self._callbacks:
            try:
                callback(self.active_type)
            except Exception as exc:
                logger.warning("Camera change callback failed: %s", exc)
