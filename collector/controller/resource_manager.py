# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Manages the collected data."""

import fastapi


router = fastapi.APIRouter()


@router.post("/resource/video/export", tags=["video"])
async def export_video(camera_name: str) -> dict:
    """Export collected videos."""
    raise NotImplementedError("The method is not implemented!")
