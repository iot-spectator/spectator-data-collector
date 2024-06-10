# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manage USB WebCams."""

import threading

from typing import Optional

import cv2


class USBWebCam:
    """USB WebCam to capture images or videos."""

    def __init__(self, src_dev):
        # Initialize the Webcam instance
        self._src_dev = src_dev
        self._cap = cv2.VideoCapture(self._src_dev)
        self._ret, self._frame = self._cap.read()

        self._frame_size = (
            int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._vid_out = None
        # Initialize the capture thread
        self._thread: Optional[threading.Thread] = None
        self._flag = False

    def take_image() -> None:
        pass

    def take_images() -> None:
        pass

    def stop_images() -> None:
        pass

    def start_video() -> None:
        pass

    def stop_video() -> None:
        pass
