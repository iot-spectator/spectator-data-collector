"""Camera monitor — background thread for motion detection and capture."""

import asyncio
import enum
import logging
import threading
import time

from dataclasses import dataclass
from datetime import datetime, timezone

import cv2
import numpy

from spectatordb.models import MediaType

from collector.camera.motion import MotionDetector
from collector.capture.task import CaptureTask
from collector.config import CollectorConfig

logger = logging.getLogger(__name__)

#: Consecutive failed frame reads tolerated before the camera is declared dead.
#: At the usual ~20 FPS with a 0.1 s backoff this is a few seconds of silence.
MAX_CONSECUTIVE_READ_FAILURES = 30


class CameraUnavailableError(RuntimeError):
    """Raised when an operation needs a camera that is not usable."""


class CameraState(enum.Enum):
    """Lifecycle state of the camera monitor thread."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"


@dataclass(frozen=True)
class CameraStatus:
    """Point-in-time snapshot of the camera monitor's health.

    Attributes
    ----------
    state : CameraState
        Lifecycle state of the monitor thread.
    camera_index : int
        Index of the camera device the monitor was pointed at.
    error : str | None
        Description of the failure when ``state`` is ``FAILED``.
    """

    state: CameraState
    camera_index: int
    error: str | None = None

    @property
    def healthy(self) -> bool:
        """Whether the monitor can currently serve capture requests."""
        return self.state in (CameraState.STARTING, CameraState.RUNNING)

    def to_dict(self) -> dict:
        """Render as JSON-serializable primitives for the health surface."""
        return {
            "state": self.state.value,
            "camera_index": self.camera_index,
            "error": self.error,
            "healthy": self.healthy,
        }


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
        self._state_lock = threading.Lock()
        self._state = CameraState.STOPPED
        self._error: str | None = None

    def start(self) -> None:
        """Start the camera monitor thread."""
        self._running = True
        self._set_state(CameraState.STARTING)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("CameraMonitor started.")

    def stop(self) -> None:
        """Stop the camera monitor thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        with self._state_lock:
            # A recorded failure outlives the shutdown so it stays diagnosable.
            if self._state is not CameraState.FAILED:
                self._state = CameraState.STOPPED
        logger.info("CameraMonitor stopped.")

    def status(self) -> CameraStatus:
        """Return a snapshot of the monitor's current health.

        Returns
        -------
        CameraStatus
            The current state, camera index, and failure reason if any.
        """
        with self._state_lock:
            return CameraStatus(
                state=self._state,
                camera_index=self._config.device.camera_index,
                error=self._error,
            )

    def request_capture(self) -> None:
        """Request an immediate capture (called from REST/MCP).

        Raises
        ------
        CameraUnavailableError
            If the monitor is not running, so the request could never be
            served. Capturing must not look like it succeeded when the
            camera is gone.
        """
        status = self.status()
        if not status.healthy:
            raise CameraUnavailableError(
                f"Camera {status.camera_index} is {status.state.value}"
                + (f": {status.error}" if status.error else "")
            )
        self._capture_requested.set()

    def _set_state(self, state: CameraState, error: str | None = None) -> None:
        with self._state_lock:
            self._state = state
            self._error = error

    def _fail(self, message: str) -> None:
        logger.error("CameraMonitor failed: %s", message)
        self._running = False
        self._set_state(CameraState.FAILED, error=message)

    def _run(self) -> None:
        cap = cv2.VideoCapture(self._config.device.camera_index)
        if not cap.isOpened():
            cap.release()
            self._fail(f"Cannot open camera {self._config.device.camera_index}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
        logger.info(
            "Camera %d opened (%.1f FPS).", self._config.device.camera_index, fps
        )
        self._set_state(CameraState.RUNNING)

        try:
            self._loop_frames(cap, fps)
        except Exception as exc:  # Broad on purpose: the thread must not die mutely.
            self._fail(f"Unexpected error in camera loop: {exc!r}")
        finally:
            cap.release()
            logger.info("Camera released.")
            with self._state_lock:
                if self._state is CameraState.RUNNING:
                    self._state = CameraState.STOPPED

    def _loop_frames(self, cap: cv2.VideoCapture, fps: float) -> None:
        read_failures = 0

        while self._running:
            ret, frame = cap.read()
            if not ret:
                read_failures += 1
                if read_failures >= MAX_CONSECUTIVE_READ_FAILURES:
                    self._fail(
                        f"Camera {self._config.device.camera_index} stopped "
                        f"returning frames after {read_failures} attempts"
                    )
                    return
                logger.warning("Frame read failed; retrying...")
                time.sleep(0.1)
                continue

            read_failures = 0

            triggered = (
                self._capture_requested.is_set() or self._motion_detector.detect(frame)
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

    def _collect_video(
        self, cap: cv2.VideoCapture, trigger_frame: numpy.ndarray, fps: float
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
