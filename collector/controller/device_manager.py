# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manages the devices that collect data."""

import fastapi

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


@router.get("/device/cameras/status", tags=["camera"])
async def get_cameras() -> dict:
    """Return all cameras' status."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/cameras/video/start", tags=["camera"])
async def start_cameras() -> dict:
    """Start capturing videos on all cameras."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/cameras/video/stop", tags=["camera"])
async def stop_cameras() -> dict:
    """Stop capturing videos on all cameras."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/{camera_id}/video/start", tags=["camera"])
async def start_video(camera_id: str) -> dict:
    """Start capturing video."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/{camera_id}/video/stop", tags=["camera"])
async def stop_video(camera_id: str) -> dict:
    """Stop capturing video."""
    raise NotImplementedError("The method is not implemented!")


@router.get("/device/camera/{camera_id}/video/status", tags=["camera"])
async def get_camera(camera_id: str) -> dict:
    """Return a running video process status of a specific."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/{camera_id}/image", tags=["camera"])
async def take_image(camera_id: int, filename: str) -> dict:
    """Take one picture."""
    webcam = usb_webcam.USBWebCam(device_id=int(camera_id))
    webcam.take_image(filename=filename)


@router.post("/device/camera/{camera_id}/images/start", tags=["camera"])
async def start_taking_images(camera_id: int, filename: str) -> dict:
    """Take pictures periodically."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/{camera_id}/images/stop", tags=["camera"])
async def stop_taking_images(camera_id: int, filename: str) -> dict:
    """Take pictures periodically."""
    raise NotImplementedError("The method is not implemented!")
