"""Tests for collector.camera.monitor."""

import asyncio
import contextlib
import threading
import time

from unittest.mock import MagicMock, patch

import numpy
import pytest

from collector.camera.monitor import (
    CameraMonitor,
    CameraState,
    CameraUnavailableError,
)
from collector.config import CollectorConfig


def _make_monitor(queue=None, loop=None):
    return CameraMonitor(
        config=CollectorConfig(),
        queue=queue if queue is not None else MagicMock(),
        loop=loop if loop is not None else MagicMock(),
    )


@contextlib.contextmanager
def _background_loop():
    """Run a real event loop in a thread, as ``SpectatorDataCollector`` does."""
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    try:
        yield loop
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=5.0)
        loop.close()


def _fake_capture(*, opened=True, reads=None):
    """Build a stand-in for ``cv2.VideoCapture``.

    Parameters
    ----------
    opened : bool
        What ``isOpened()`` reports.
    reads : object
        Return value for every ``read()`` call. Defaults to a black frame.
    """
    cap = MagicMock()
    cap.isOpened.return_value = opened
    cap.get.return_value = 20.0
    cap.read.return_value = (
        reads if reads is not None else (True, numpy.zeros((8, 8, 3), numpy.uint8))
    )
    return cap


def _join(monitor, timeout=5.0):
    assert monitor._thread is not None
    monitor._thread.join(timeout=timeout)
    assert not monitor._thread.is_alive(), "monitor thread did not exit"


def _wait_for_state(monitor, state, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if monitor.status().state is state:
            return
        time.sleep(0.01)
    pytest.fail(f"monitor never reached {state}; last was {monitor.status().state}")


def test_status_is_stopped_before_start():
    monitor = _make_monitor()
    status = monitor.status()
    assert status.state is CameraState.STOPPED
    assert status.healthy is False
    assert status.error is None


def test_unopenable_camera_marks_monitor_failed():
    monitor = _make_monitor()
    with patch(
        "collector.camera.monitor.cv2.VideoCapture",
        return_value=_fake_capture(opened=False),
    ):
        monitor.start()
        _join(monitor)

    status = monitor.status()
    assert status.state is CameraState.FAILED
    assert status.healthy is False
    assert "Cannot open camera" in (status.error or "")


def test_capture_request_fails_when_camera_unavailable():
    monitor = _make_monitor()
    with patch(
        "collector.camera.monitor.cv2.VideoCapture",
        return_value=_fake_capture(opened=False),
    ):
        monitor.start()
        _join(monitor)

    with pytest.raises(CameraUnavailableError, match="failed"):
        monitor.request_capture()


def test_capture_request_fails_when_never_started():
    monitor = _make_monitor()
    with pytest.raises(CameraUnavailableError, match="stopped"):
        monitor.request_capture()


def test_capture_request_accepted_while_running():
    queue: asyncio.Queue = asyncio.Queue()
    with _background_loop() as loop:
        monitor = _make_monitor(queue=queue, loop=loop)
        with patch(
            "collector.camera.monitor.cv2.VideoCapture", return_value=_fake_capture()
        ):
            monitor.start()
            _wait_for_state(monitor, CameraState.RUNNING)
            monitor.request_capture()
            assert monitor.status().healthy is True

            task = asyncio.run_coroutine_threadsafe(queue.get(), loop).result(
                timeout=5.0
            )
            assert task.frames

            monitor.stop()

    assert monitor.status().state is CameraState.STOPPED


def test_persistent_read_failures_mark_monitor_failed(monkeypatch):
    monkeypatch.setattr("collector.camera.monitor.MAX_CONSECUTIVE_READ_FAILURES", 3)
    monitor = _make_monitor()
    with patch(
        "collector.camera.monitor.cv2.VideoCapture",
        return_value=_fake_capture(reads=(False, None)),
    ):
        monitor.start()
        _join(monitor)

    status = monitor.status()
    assert status.state is CameraState.FAILED
    assert "stopped returning frames" in (status.error or "")


def test_unexpected_loop_error_marks_monitor_failed():
    monitor = _make_monitor()
    cap = _fake_capture()
    cap.read.side_effect = RuntimeError("usb fell out")
    with patch("collector.camera.monitor.cv2.VideoCapture", return_value=cap):
        monitor.start()
        _join(monitor)

    status = monitor.status()
    assert status.state is CameraState.FAILED
    assert "usb fell out" in (status.error or "")


def test_stop_preserves_failure_reason():
    monitor = _make_monitor()
    with patch(
        "collector.camera.monitor.cv2.VideoCapture",
        return_value=_fake_capture(opened=False),
    ):
        monitor.start()
        _join(monitor)
        monitor.stop()

    status = monitor.status()
    assert status.state is CameraState.FAILED
    assert status.error is not None


def test_status_dict_is_json_serializable():
    monitor = _make_monitor()
    payload = monitor.status().to_dict()
    assert payload == {
        "state": "stopped",
        "camera_index": 0,
        "error": None,
        "healthy": False,
    }
