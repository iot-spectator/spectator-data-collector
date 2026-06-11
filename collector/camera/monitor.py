"""Camera monitor — background thread for motion detection and capture."""

import asyncio
import logging
import threading
import time

from datetime import datetime, timezone

import cv2

from spectatordb.models import MediaType

from collector.camera.motion import MotionDetector
from collector.capture.task import CaptureTask
from collector.config import CollectorConfig

logger = logging.getLogger(__name__)


class CameraMonitor:
    """Background thread that reads camera frames and detects motion.

    When motion is detected (or an on-demand capture is requested), a
    :class:`CaptureTask` is enqueued for the async pipeline.

    Parameters
    ----------
    config : CollectorConfig
        Collector configuration.
    queue : asyncio.Queue[CaptureTask | None]
        The async queue shared with the capture pipeline.
    loop : asyncio.AbstractEventLoop
        The main event loop (for ``run_coroutine_threadsafe``).
    """

    def __init__(
        self,
        config: CollectorConfig,
        queue: asyncio.Queue[CaptureTask | None],
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self._config = config
        self._queue = queue
        self._loop = loop
        self._motion_detector = MotionDetector(
            sensitivity=config.motion.sensitivity,
        )
        self._running = False
        self._capture_requested = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the camera monitor thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("CameraMonitor started.")

    def stop(self) -> None:
        """Stop the camera monitor thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        logger.info("CameraMonitor stopped.")

    def request_capture(self) -> None:
        """Request an immediate capture (called from REST/MCP)."""
        self._capture_requested.set()

    def _run(self) -> None:
        cap = cv2.VideoCapture(self._config.device.camera_index)
        if not cap.isOpened():
            logger.error("Cannot open camera %d", self._config.device.camera_index)
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
        logger.info(
            "Camera %d opened (%.1f FPS).", self._config.device.camera_index, fps
        )

        try:
            while self._running:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Frame read failed; retrying...")
                    time.sleep(0.1)
                    continue

                triggered = (
                    self._capture_requested.is_set()
                    or self._motion_detector.detect(frame)
                )
                if not triggered:
                    continue

                self._capture_requested.clear()

                if self._config.capture.mode == "video":
                    task = self._collect_video(cap, frame, fps)
                else:
                    task = CaptureTask(
                        frames=[frame],
                        captured_at=datetime.now(timezone.utc),
                        media_type=MediaType.IMAGE,
                    )

                asyncio.run_coroutine_threadsafe(self._queue.put(task), self._loop)
                logger.info("Enqueued %s capture task.", task.media_type.value)
        finally:
            cap.release()
            logger.info("Camera released.")

    def _collect_video(
        self, cap: cv2.VideoCapture, trigger_frame: object, fps: float
    ) -> CaptureTask:
        duration = self._config.capture.video_duration
        max_frames = int(fps * duration)
        frames = [trigger_frame]
        captured_at = datetime.now(timezone.utc)

        for _ in range(max_frames - 1):
            if not self._running:
                break
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        return CaptureTask(
            frames=frames,
            captured_at=captured_at,
            media_type=MediaType.VIDEO,
            video_duration=duration,
        )
