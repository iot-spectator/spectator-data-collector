"""Capture task dataclass."""

from dataclasses import dataclass, field
from datetime import datetime

import numpy

from spectatordb.models import MediaType


@dataclass
class CaptureTask:
    """A capture task to be processed by the pipeline.

    Parameters
    ----------
    frames : list[numpy.ndarray]
        Captured frames. A single frame for IMAGE mode, multiple for VIDEO.
    captured_at : datetime
        When the capture was triggered.
    media_type : MediaType
        IMAGE or VIDEO.
    video_duration : float | None
        Duration in seconds for video captures.
    """

    frames: list[numpy.ndarray]
    captured_at: datetime
    media_type: MediaType
    video_duration: float | None = None
