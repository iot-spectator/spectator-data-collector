"""Asynchronous capture pipeline."""

import asyncio
import logging
import pathlib

from spectatordb.models import MediaType
from spectatordb.spectatordb import SpectatorDB

from collector.capture.recorder import ImageRecorder, VideoRecorder
from collector.capture.task import CaptureTask
from collector.config import CollectorConfig
from collector.enrichment.base import Enricher


logger = logging.getLogger(__name__)


class CapturePipeline:
    """Async queue consumer that records, enriches, and stores captures.

    Parameters
    ----------
    queue : asyncio.Queue[CaptureTask | None]
        The task queue. A ``None`` sentinel signals shutdown.
    db : SpectatorDB
        The database for storing media.
    config : CollectorConfig
        Collector configuration.
    enricher : Enricher | None
        Optional enricher for AI labeling.
    """

    def __init__(
        self,
        queue: asyncio.Queue[CaptureTask | None],
        db: SpectatorDB,
        config: CollectorConfig,
        enricher: Enricher | None = None,
    ) -> None:
        self._queue = queue
        self._db = db
        self._config = config
        self._enricher = enricher
        self._image_recorder = ImageRecorder()
        self._video_recorder = VideoRecorder()
        self._running = False

    async def run(self) -> None:
        """Process tasks from the queue until stopped."""
        self._running = True
        tmp_dir = pathlib.Path(self._config.storage.tmp_dir)
        loop = asyncio.get_running_loop()

        logger.info("CapturePipeline started.")
        while self._running:
            task = await self._queue.get()
            if task is None:
                break

            try:
                await self._process_task(task, tmp_dir, loop)
            except Exception:
                logger.exception("Error processing capture task.")
            finally:
                self._queue.task_done()

        logger.info("CapturePipeline stopped.")

    async def _process_task(
        self,
        task: CaptureTask,
        tmp_dir: pathlib.Path,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        if task.media_type == MediaType.IMAGE:
            recorder = self._image_recorder
        else:
            recorder = self._video_recorder

        file_path = await loop.run_in_executor(None, recorder.record, task, tmp_dir)
        logger.info("Recorded %s to %s", task.media_type.value, file_path)

        labels: list[str] = []
        description: str | None = None
        embedding: list[float] | None = None

        if self._enricher is not None:
            result = await loop.run_in_executor(
                None, self._enricher.enrich, file_path, task.media_type
            )
            labels = result.labels
            description = result.description
            embedding = result.embedding

        await loop.run_in_executor(
            None,
            lambda: self._db.insert(
                file=file_path,
                media_type=task.media_type,
                captured_at=task.captured_at,
                duration=task.video_duration,
                device_id=self._config.device.device_id,
                labels=labels,
                description=description,
                embedding=embedding,
            ),
        )
        logger.info("Stored record for %s capture.", task.media_type.value)

        # Clean up temp file (DB has its own copy)
        file_path.unlink(missing_ok=True)

    async def stop(self) -> None:
        """Signal the pipeline to stop."""
        self._running = False
        await self._queue.put(None)
