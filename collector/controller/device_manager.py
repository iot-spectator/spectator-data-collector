# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manages the devices that collect data."""

import fastapi

from iothealth import device_health
from devices import usb_webcam


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


@router.post("/device/video/{device_id}/start", tags=["video"])
async def start_video(device_id: str) -> dict:
    """Start capturing video."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/video/{device_id}/stop", tags=["video"])
async def stop_video(device_id: str) -> dict:
    """Stop capturing video."""
    raise NotImplementedError("The method is not implemented!")


@router.get("/device/video/status", tags=["video"])
async def get_video_status() -> dict:
    """Return all running video process status."""
    raise NotImplementedError("The method is not implemented!")


@router.get("/device/video/{device_id}/status", tags=["video"])
async def get_camera(device_id: str) -> dict:
    """Return a running video process status of a specific."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/image/{device_id}", tags=["image"])
async def take_image(device_id: int, filename: str) -> dict:
    """Return one camera status."""
    webcam = usb_webcam.USBWebCam(device_id=int(device_id))
    webcam.take_image(filename=filename)
