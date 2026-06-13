"""SpectatorService — shared business logic for REST and MCP."""

import pathlib

from datetime import datetime
from typing import cast

from iothealth.device_health import DeviceHealth

from spectatordb.models import MediaRecord, MediaType
from spectatordb.spectatordb import SpectatorDB

from collector.camera.monitor import CameraMonitor
from collector.config import CollectorConfig


class SpectatorService:
    """Business logic shared between the REST and MCP layers.

    Parameters
    ----------
    db : SpectatorDB
        The media database.
    monitor : CameraMonitor
        The camera monitor (for on-demand capture).
    config : CollectorConfig
        Collector configuration.
    """

    def __init__(
        self,
        db: SpectatorDB,
        monitor: CameraMonitor,
        config: CollectorConfig,
    ) -> None:
        self._db = db
        self._monitor = monitor
        self._config = config

    def query_media(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        media_type: MediaType | None = None,
        device_id: str | None = None,
        labels: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[MediaRecord]:
        """Query media records with composable filters."""
        return cast(
            list[MediaRecord],
            self._db.query(
                start=start,
                end=end,
                media_type=media_type,
                device_id=device_id,
                labels=labels,
                limit=limit,
                offset=offset,
            ),
        )

    def get_record(self, id: str) -> MediaRecord:
        """Get a single media record by ID."""
        return self._db.get(id)

    def retrieve_file(self, id: str) -> pathlib.Path:
        """Copy a media file to a temp path for serving.

        Returns
        -------
        pathlib.Path
            Path to the temporary copy of the media file.
        """
        record = self._db.get(id)
        tmp_dir = pathlib.Path(self._config.storage.tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        dest = tmp_dir / f"{record.id}.{record.format}"
        self._db.retrieve(id, dest)
        return dest

    def device_status(self) -> dict:
        """Read device health information."""
        device = DeviceHealth()
        return cast(dict, device.summary())

    def capture_now(self) -> dict:
        """Trigger an immediate capture."""
        self._monitor.request_capture()
        return {"status": "capture requested"}
