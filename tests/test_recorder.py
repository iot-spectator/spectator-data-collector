"""Tests for collector.capture.recorder."""

from datetime import datetime, timezone

import numpy

from spectatordb.models import MediaType

from collector.capture.recorder import ImageRecorder, VideoRecorder
from collector.capture.task import CaptureTask


def _make_frame(h=480, w=640):
    return numpy.random.randint(0, 255, (h, w, 3), dtype=numpy.uint8)


def test_image_recorder_writes_jpg(tmp_path):
    task = CaptureTask(
        frames=[_make_frame()],
        captured_at=datetime.now(timezone.utc),
        media_type=MediaType.IMAGE,
    )
    recorder = ImageRecorder()
    path = recorder.record(task, tmp_path / "out")
    assert path.exists()
    assert path.suffix == ".jpg"
    assert path.stat().st_size > 0


def test_video_recorder_writes_avi(tmp_path):
    frames = [_make_frame() for _ in range(10)]
    task = CaptureTask(
        frames=frames,
        captured_at=datetime.now(timezone.utc),
        media_type=MediaType.VIDEO,
        video_duration=0.5,
    )
    recorder = VideoRecorder(fps=20.0)
    path = recorder.record(task, tmp_path / "out")
    assert path.exists()
    assert path.suffix == ".avi"
    assert path.stat().st_size > 0
