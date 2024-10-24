import time

from collector.devices import usb_webcam

usb = usb_webcam.USBWebCam(camera_id=0)

usb.take_images(frequency=3)

time.sleep(20)

usb.stop_taking_images()
