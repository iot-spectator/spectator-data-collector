"""Asynchronous capture pipeline."""

import asyncio
import logging
import pathlib

from spectatordb.models import MediaType, UNSET
from spectatordb.spectatordb import SpectatorDB

from collector.capture.recorder import ImageRecorder, VideoRecorder
from collector.capture.task import CaptureTask
from collector.config import CollectorConfig
from collector.enrichment.base import Enricher

logger = logging.getLogger(__name__)


class CapturePipeline:
    """Async queue consumer that records, stores, and optionally enriches captures.

    The pipeline follows a store-first, enrich-later strategy: media is
    persisted immediately after recording so that a slow or failing enricher
    never causes data loss. Enrichment results are written back via
    ``update_enrichment`` only after the record is safely stored.

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
        recorder = (
            self._image_recorder
            if task.media_type == MediaType.IMAGE
            else self._video_recorder
        )
        file_path = await loop.run_in_executor(None, recorder.record, task, tmp_dir)
        logger.info("Recorded %s to %s", task.media_type.value, file_path)

        record_id = await loop.run_in_executor(
            None,
            lambda: self._db.insert(
                file=file_path,
                media_type=task.media_type,
                captured_at=task.captured_at,
                duration=task.video_duration,
                device_id=self._config.device.device_id,
            ),
        )
        logger.info(
            "Stored record %s for %s capture.", record_id, task.media_type.value
        )

        if self._enricher is not None:
            try:
                result = await loop.run_in_executor(
                    None, self._enricher.enrich, file_path, task.media_type
                )
                embedding = result.embedding if result.embedding_model else None
                embedding_model = result.embedding_model if result.embedding else None
                await loop.run_in_executor(
                    None,
                    lambda: self._db.update_enrichment(
                        record_id,
                        labels=result.labels,
                        description=result.description,
                        embedding=embedding if embedding is not None else UNSET,
                        embedding_model=(
                            embedding_model if embedding_model is not None else UNSET
                        ),
                    ),
                )
                logger.info("Enriched record %s.", record_id)
            except Exception:
                logger.exception(
                    "Enrichment failed for record %s; stored without enrichment.",
                    record_id,
                )

        file_path.unlink(missing_ok=True)

    async def stop(self) -> None:
        """Signal the pipeline to stop."""
        self._running = False
        await self._queue.put(None)
