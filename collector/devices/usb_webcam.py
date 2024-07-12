# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manage USB WebCams."""

import pathlib
import threading

import cv2

from typing import Optional


class USBWebCam:
    """USB WebCam to capture images or videos."""

    def __init__(self, device_id: int):
        # Initialize the Webcam instance
        self._device_id = device_id
        self._camera = cv2.VideoCapture(self._device_id)

        self._ret, self._frame = self._camera.read()

        self._frame_size = (
            int(self._camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        self._fps = self._camera.get(cv2.CAP_PROP_FPS)
        self._vid_out = None

        # Initialize the capture thread
        self._thread: Optional[threading.Thread] = None
        self._flag = False

    def __del__(self):
        pass

    def take_image(self, filename: str) -> None:
        success, image = self._camera.read()
        if success:
            cv2.imwrite(filename=filename, img=image)
            self._camera.release()

    def take_images(self, target: pathlib.Path) -> None:
        pass

    def stop_images(self) -> None:
        pass

    def start_video(self, target: pathlib.Path) -> None:
        """Start the camera thread.

        Start a running thread for the camera in the background.
        """
        # Might be configurable
        fourcc = cv2.VideoWriter.fourcc(*"XVID")
        self._vid_out = cv2.VideoWriter(
            str(target), fourcc, self._fps, self._frame_size
        )

        # Setup the thread
        self._thread = threading.Thread(
            target=self._capture, name=f"{USBWebCam.__name__}-{self._device_id}"
        )
        self._flag = True
        self._thread.start()

    def stop_video(self) -> None:
        """Stop the camera thread."""
        self._flag = False
        if self._vid_out:
            self._vid_out.release()
        if self._thread:
            self._thread.join()

    def _capture(self) -> None:
        """Run the camera thread."""
        while self._flag:
            self._ret, self._frame = self._camera.read()
            self._vid_out.write(self._frame)


class USBWebCamManager:

    def __init__(self) -> None:
        pass
