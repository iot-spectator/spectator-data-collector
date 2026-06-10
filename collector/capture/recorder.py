"""Image and video recorders."""

import pathlib
import uuid

import cv2
import numpy

from collector.capture.task import CaptureTask


class ImageRecorder:
    """Records a single frame as a JPEG image."""

    def record(self, task: CaptureTask, dest: pathlib.Path) -> pathlib.Path:
        """Write the trigger frame to a JPEG file.

        Parameters
        ----------
        task : CaptureTask
            The capture task containing the frame.
        dest : pathlib.Path
            Directory to write the file into.

        Returns
        -------
        pathlib.Path
            Path to the written JPEG file.
        """
        dest.mkdir(parents=True, exist_ok=True)
        file_path = dest / f"{uuid.uuid4()}.jpg"
        cv2.imwrite(str(file_path), task.frames[0])
        return file_path


class VideoRecorder:
    """Records multiple frames as an AVI video.

    Parameters
    ----------
    fps : float
        Frames per second for the output video.
    """

    def __init__(self, fps: float = 20.0) -> None:
        self._fps = fps

    def record(self, task: CaptureTask, dest: pathlib.Path) -> pathlib.Path:
        """Write frames to an AVI file.

        Parameters
        ----------
        task : CaptureTask
            The capture task containing the frames.
        dest : pathlib.Path
            Directory to write the file into.

        Returns
        -------
        pathlib.Path
            Path to the written AVI file.
        """
        dest.mkdir(parents=True, exist_ok=True)
        file_path = dest / f"{uuid.uuid4()}.avi"

        h, w = task.frames[0].shape[:2]
        fourcc = cv2.VideoWriter.fourcc(*"XVID")
        writer = cv2.VideoWriter(str(file_path), fourcc, self._fps, (w, h))
        try:
            for frame in task.frames:
                writer.write(frame)
        finally:
            writer.release()

        return file_path
