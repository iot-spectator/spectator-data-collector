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
    camera_id: Optional[int]
        If present, the given camera's status will be return; otherwise,
        return all camera's status. Default `None`.

    Returns
    -------
    `dict`
        A JSON object contains the camera status.
    """
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/video/start", tags=["camera"])
async def start_capturing_videos(camera_id: Optional[int] = None) -> list[int]:
    """Start capturing videos. If camera_id is not present, all cameras will
    start capturing videos.


    Parameters
    ----------
    camera_id: Optional[int]
        If present, only the given camera will start capturing videos; otherwise,
        all available cameras will start capturing videos. Default `None`.

    Returns
    -------
    list[int]
        The list of camera IDs that have started capturing videos successfully.
    """
    raise NotImplementedError("The method is not implemented!")


@router.post("/device/camera/image", tags=["camera"])
async def take_images(
    camera_id: Optional[int] = None, frequency: Optional[int] = None
) -> list[int]:
    """Take pictures.

    Parameters
    ----------
    camera_id: Optional[int]
        If present, only the given camera will take image(s); otherwise,
        all available cameras will take images. Default `None`.

    frequency: Optional[int]
        The frequency of taking images. Unit: second. If not present,
        only one picture will be taken. Default `None`.

    Returns
    -------
    list[int]
        The list of camera IDs that have started taking images successfully.
    """
    webcam = usb_webcam.USBWebCam(device_id=int(camera_id))

    if frequency:
        raise NotImplementedError("Taking images periodically is not implemented.")
    else:
        if camera_id:
            webcam.take_image()


@router.post("/device/camera/stop", tags=["camera"])
async def stop_camera_activities(camera_id: Optional[int] = None) -> list[int]:
    """Stop camera activities. If camera_id is not present, activities on all
    cameras will be stopped.

    Parameters
    ----------
    camera_id: Optional[int]
        If present, only the activities on the given camera will stop; otherwise,
        all activities on all cameras will stop. Default `None`.

    Returns
    -------
    list[int]
        The list of the stopped cameras.
    """
    raise NotImplementedError("The method is not implemented!")
