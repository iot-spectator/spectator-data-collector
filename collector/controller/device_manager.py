# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manages the devices that collect data."""

import fastapi

from iothealth import device_health


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


@router.post("/device/video/{camera_name}/stop", tags=["video"])
async def stop_video(camera_name: str) -> dict:
    """Stop capturing video."""
    raise NotImplementedError("The method is not implemented!")


@router.get("/device/video/status", tags=["video"])
async def get_cameras() -> dict:
    """Return all the cameras status."""
    raise NotImplementedError("The method is not implemented!")


@router.get("/device/video/{camera_name}/status", tags=["video"])
async def get_camera(camera_name: str) -> dict:
    """Return one camera status."""
    raise NotImplementedError("The method is not implemented!")
