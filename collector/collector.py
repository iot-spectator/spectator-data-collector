"""SpectatorDataCollector — top-level wiring."""

import asyncio
import logging
import pathlib

import uvicorn

from spectatordb.metadata.sqlite_metadata_store import SQLiteMetadataStore
from spectatordb.spectatordb import SpectatorDB
from spectatordb.storage.local_storage import LocalStorage

from collector.camera.monitor import CameraMonitor
from collector.capture.pipeline import CapturePipeline
from collector.capture.task import CaptureTask
from collector.config import CollectorConfig
from collector.enrichment.base import Enricher
from collector.enrichment.local import LocalEnricher
from collector.mcp import create_mcp_server
from collector.rest import create_app
from collector.service import SpectatorService


logger = logging.getLogger(__name__)


class SpectatorDataCollector:
    """Top-level class that wires all components together.

    Parameters
    ----------
    config : CollectorConfig | None
        Configuration. Uses defaults if ``None``.
    """

    def __init__(self, config: CollectorConfig | None = None) -> None:
        self._config = config or CollectorConfig()

        storage = LocalStorage(
            storage_dir=pathlib.Path(self._config.storage.media_dir)
        )
        metadata_store = SQLiteMetadataStore(
            db_path=pathlib.Path(self._config.storage.db_path)
        )
        self._db = SpectatorDB(storage=storage, metadata_store=metadata_store)

        self._enricher: Enricher | None = None
        if self._config.enrichment.enabled:
            self._enricher = LocalEnricher()

        self._queue: asyncio.Queue[CaptureTask | None] = asyncio.Queue()

    async def run(self) -> None:
        """Start the collector: camera, pipeline, and REST server."""
        loop = asyncio.get_running_loop()

        monitor = CameraMonitor(
            config=self._config, queue=self._queue, loop=loop
        )
        pipeline = CapturePipeline(
            queue=self._queue,
            db=self._db,
            config=self._config,
            enricher=self._enricher,
        )
        service = SpectatorService(
            db=self._db, monitor=monitor, config=self._config
        )
        app = create_app(service)

        monitor.start()
        pipeline_task = asyncio.create_task(pipeline.run())

        rest_config = uvicorn.Config(
            app=app,
            host=self._config.server.host,
            port=self._config.server.port,
            log_level="info",
        )
        rest_server = uvicorn.Server(rest_config)

        servers: list[asyncio.Task] = [
            asyncio.create_task(rest_server.serve()),
        ]

        if self._config.mcp.enabled:
            mcp = create_mcp_server(service)
            mcp_app = mcp.sse_app()
            mcp_config = uvicorn.Config(
                app=mcp_app,
                host=self._config.mcp.host,
                port=self._config.mcp.port,
                log_level="info",
            )
            mcp_server = uvicorn.Server(mcp_config)
            servers.append(asyncio.create_task(mcp_server.serve()))
            logger.info(
                "MCP server enabled on %s:%d",
                self._config.mcp.host,
                self._config.mcp.port,
            )

        logger.info("SpectatorDataCollector starting...")
        try:
            await asyncio.gather(*servers)
        finally:
            logger.info("Shutting down...")
            monitor.stop()
            await pipeline.stop()
            await pipeline_task
            logger.info("SpectatorDataCollector stopped.")
