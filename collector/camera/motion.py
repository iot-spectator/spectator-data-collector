"""Motion detection using OpenCV MOG2 background subtraction."""

import cv2
import numpy


class MotionDetector:
    """Detects motion in video frames using background subtraction.

    Parameters
    ----------
    sensitivity : float
        Fraction of changed pixels (0-1) required to trigger motion.
    """

    def __init__(self, sensitivity: float = 0.005) -> None:
        self._sensitivity = sensitivity
        self._subtractor = cv2.createBackgroundSubtractorMOG2()
        self._kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    def detect(self, frame: numpy.ndarray) -> bool:
        """Check whether the frame contains motion.

        Parameters
        ----------
        frame : numpy.ndarray
            A BGR frame from OpenCV.

        Returns
        -------
        bool
            ``True`` if motion is detected.
        """
        mask = self._subtractor.apply(frame)
        # Reduce noise with morphological operations
        mask = cv2.erode(mask, self._kernel, iterations=1)
        mask = cv2.dilate(mask, self._kernel, iterations=2)

        changed_fraction = cv2.countNonZero(mask) / mask.size
        return changed_fraction > self._sensitivity

    def reset(self) -> None:
        """Reset the background model."""
        self._subtractor = cv2.createBackgroundSubtractorMOG2()
