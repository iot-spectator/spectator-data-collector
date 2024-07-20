# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manages the collected data."""

import fastapi


router = fastapi.APIRouter()


@router.post("/resource/videos/export", tags=["video"])
async def export_videos() -> dict:
    """Export collected videos."""
    raise NotImplementedError("The method is not implemented!")


@router.post("/resource/images/export", tags=["image"])
async def export_images() -> dict:
    """Export collected images."""
    raise NotImplementedError("The method is not implemented!")
