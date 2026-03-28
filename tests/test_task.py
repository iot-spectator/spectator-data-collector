"""Tests for collector.capture.task."""

from datetime import datetime, timezone

import numpy

from spectatordb.models import MediaType

from collector.capture.task import CaptureTask


def test_image_task():
    frame = numpy.zeros((480, 640, 3), dtype=numpy.uint8)
    now = datetime.now(timezone.utc)
    task = CaptureTask(
        frames=[frame],
        captured_at=now,
        media_type=MediaType.IMAGE,
    )
    assert len(task.frames) == 1
    assert task.media_type == MediaType.IMAGE
    assert task.video_duration is None


def test_video_task():
    frames = [numpy.zeros((480, 640, 3), dtype=numpy.uint8) for _ in range(10)]
    now = datetime.now(timezone.utc)
    task = CaptureTask(
        frames=frames,
        captured_at=now,
        media_type=MediaType.VIDEO,
        video_duration=5.0,
    )
    assert len(task.frames) == 10
    assert task.media_type == MediaType.VIDEO
    assert task.video_duration == 5.0
