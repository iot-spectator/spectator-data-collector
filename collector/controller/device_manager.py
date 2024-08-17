# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manages the devices that collect data."""

import fastapi

from typing import Optional

from iothealth import device_health

from collector.devices import usb_webcam


router = fastapi.APIRouter()


@router.get("/device/status", tags=["device"])
async def get_status() -> dict:
    """Return the device status and system information.

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
        "platform": device.device_platform(),
        "architecture": device.processor_architecture(),
        "os": device.operating_system(),
        "cameras": device.cameras(),
    }


@router.get("/device/camera/status", tags=["camera"])
async def get_camera_status(camera_id: Optional[int] = None) -> dict:
    """Return camera status. If camera_id is present, only the given camera's status
    will be returned.

    Parameters
    ----------
    `camera_id`: `Optional[int]`
        If present, the given camera's status will be return; otherwise,
        return all camera's status. Default `None`.

    Returns
    -------
    `dict`
        A JSON object contains the camera status.
    """
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/video/start", tags=["camera"])
async def start_capturing_videos(camera_id: int, duration: Optional[int] = 5) -> None:
    """Start capturing videos.

    Parameters
    ----------
    `camera_id`: `int`
        The ID of the camera to be started capturing.

    `duration`: `Optional[int]`
        The duration of each video in minutes. Default is 5 minutes.
    """
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/video/stop", tags=["camera"])
async def stop_capturing_videos(camera_id: int) -> None:
    """Stop capturing videos.

    Parameters
    ----------
    `camera_id`: `int`
        The ID of the camera to be stopped.
    """
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/image/start", tags=["camera"])
async def start_taking_images(camera_id: int, frequency: Optional[int] = None) -> None:
    """Take pictures.

    Parameters
    ----------
    `camera_id`: `int`
        The ID of the camera to take a image.s

    `frequency`: `Optional[int]`
        The frequency of taking images. Unit: second. If not present,
        only one picture will be taken. Default `None`.
    """
    webcam = usb_webcam.USBWebCam(device_id=int(camera_id))

    if frequency:
        raise NotImplementedError("Taking images periodically is not implemented.")
    else:
        webcam.take_image()


@router.post("/device/camera/image/stop", tags=["camera"])
async def stop_taking_images(camera_id: int) -> None:
    """Stop taking images.

    Parameters
    ----------
    `camera_id`: `int`
        The ID of the camera to be stopped.
    """
    raise NotImplementedError("The method is not implemented!")
