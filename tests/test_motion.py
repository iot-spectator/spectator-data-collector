"""Tests for collector.camera.motion."""

import numpy

from collector.camera.motion import MotionDetector


def test_no_motion_on_static_frames():
    detector = MotionDetector(sensitivity=0.005)
    frame = numpy.full((480, 640, 3), 128, dtype=numpy.uint8)
    # Feed several identical frames to build the background model
    for _ in range(30):
        detector.detect(frame)
    # After background is established, a static frame should not trigger
    assert detector.detect(frame) is False


def test_motion_detected_on_changed_frame():
    detector = MotionDetector(sensitivity=0.005)
    bg = numpy.full((480, 640, 3), 128, dtype=numpy.uint8)
    # Build background model
    for _ in range(30):
        detector.detect(bg)
    # Introduce a large change
    changed = bg.copy()
    changed[100:300, 100:500] = 255
    assert detector.detect(changed) is True


def test_high_sensitivity_ignores_small_change():
    detector = MotionDetector(sensitivity=0.9)
    bg = numpy.full((480, 640, 3), 128, dtype=numpy.uint8)
    for _ in range(30):
        detector.detect(bg)
    # Small change
    changed = bg.copy()
    changed[200:210, 200:210] = 255
    assert detector.detect(changed) is False


def test_reset():
    detector = MotionDetector(sensitivity=0.005)
    frame = numpy.full((480, 640, 3), 128, dtype=numpy.uint8)
    for _ in range(30):
        detector.detect(frame)
    detector.reset()
    # After reset, the first frame is treated as new; MOG2 might detect
    # changes as the model re-learns. Just verify no crash.
    detector.detect(frame)
