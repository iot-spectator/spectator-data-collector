import logging
import time

from collector import logger
from collector.devices import usb_webcam

logger.setup_logger(level=logging.DEBUG, console=True)


usb = usb_webcam.USBWebCam(camera_id=0)

#usb.take_image()

#usb.take_images(frequency=3)

#time.sleep(20)

#usb.stop_taking_images()


usb_manager = usb_webcam.USBWebCamManager()

usb_manager.add_camera(camera=usb)

print(usb_manager.list_cameras())

print(usb_manager.get_camera(camera_id=0))
