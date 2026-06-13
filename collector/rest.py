"""FastAPI application and REST routes."""

import dataclasses
import logging

from datetime import datetime

import fastapi

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from spectatordb.models import MediaType

from collector.service import SpectatorService

logger = logging.getLogger(__name__)


def create_app(service: SpectatorService) -> fastapi.FastAPI:
    """Create the FastAPI application.

    Parameters
    ----------
    service : SpectatorService
        The shared service layer.

    Returns
    -------
    fastapi.FastAPI
        The configured application.
    """
    app = fastapi.FastAPI(title="Spectator Data Collector")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["root"])
    async def read_root() -> dict:
        return {"message": "Welcome to Spectator Data Collector!"}

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return service.device_status()

    @app.get("/media", tags=["media"])
    async def query_media(
        media_type: str | None = None,
        device_id: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        labels: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        mt = MediaType(media_type) if media_type else None
        label_list = (
            [lbl.strip() for lbl in labels.split(",") if lbl.strip()]
            if labels
            else None
        )
        records = service.query_media(
            start=start,
            end=end,
            media_type=mt,
            device_id=device_id,
            labels=label_list,
            limit=limit,
            offset=offset,
        )
        return [dataclasses.asdict(r) for r in records]

    @app.get("/media/{id}", tags=["media"])
    async def get_record(id: str) -> dict:
        try:
            record = service.get_record(id)
        except KeyError:
            raise fastapi.HTTPException(status_code=404, detail="Record not found")
        return dataclasses.asdict(record)

    @app.get("/media/{id}/file", tags=["media"])
    async def get_file(id: str) -> FileResponse:
        try:
            file_path = service.retrieve_file(id)
        except KeyError:
            raise fastapi.HTTPException(status_code=404, detail="Record not found")
        return FileResponse(path=file_path)

    @app.post("/capture", tags=["capture"])
    async def capture() -> dict:
        return service.capture_now()

    return app
