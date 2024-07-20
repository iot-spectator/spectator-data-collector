# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manages the devices that collect data."""

import fastapi

from typing import Optional

from iothealth import device_health

from collector.devices import usb_webcam


router = fastapi.APIRouter()


@router.get("/device/status", tags=["device"])
async def get_status() -> dict:
    """GET /device/status.

    Returns
    -------
    `dict`
        A JSON object contains the status of the IoT device.
    """
    device = device_health.DeviceHealth()
    return {
        "cpu": device.processors(),
        "memory": device.memory(),
        "disk": device.capacity(),
        "temperature": device.temperature(),
    }


@router.get("/device/info", tags=["device"])
async def get_info() -> dict:
    """GET /device/info.

    Returns
    -------
    `dict`
        A JSON object contains the device's system information.
    """
    device = device_health.DeviceHealth()
    return {
        "platform": device.device_platform(),
        "architecture": device.processor_architecture(),
        "os": device.operating_system(),
        "cameras": device.cameras(),
    }


@router.get("/device/camera/status", tags=["camera"])
async def get_camera_status(camera_id: Optional[int] = None) -> dict:
    """Return camera status. If camera_id is not present, all cameras status
    will be returned.

    Parameters
    ----------
    camera_id: Optional[int]
        Camera ID.
    """
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/video/start", tags=["camera"])
async def start_capturing_videos(camera_id: Optional[int] = None) -> dict:
    """Start capturing videos. If camera_id is not present, all cameras will
    start capturing videos.
    """
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/image", tags=["camera"])
async def take_images_on_all_cameras(
    camera_id: Optional[int] = None, frequency: Optional[int] = None
) -> dict:
    """Take pictures."""
    webcam = usb_webcam.USBWebCam(device_id=int(camera_id))
    webcam.take_image(filename="Temp.jpg")


@router.post("/device/camera/stop", tags=["camera"])
async def stop_camera_activities(camera_id: Optional[int] = None) -> dict:
    """Stop camera activities. If camera_id is not present, activities on all
     cameras will be stopped."""
    raise NotImplementedError("The method is not implemented!")
