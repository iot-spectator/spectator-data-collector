"""Integration test for the capture pipeline."""

import asyncio

from datetime import datetime, timezone

import numpy
import pytest

from spectatordb.metadata.sqlite_metadata_store import SQLiteMetadataStore
from spectatordb.models import MediaType
from spectatordb.spectatordb import SpectatorDB
from spectatordb.storage.local_storage import LocalStorage

from collector.capture.pipeline import CapturePipeline
from collector.capture.task import CaptureTask
from collector.config import CollectorConfig


@pytest.fixture
def db(tmp_path):
    storage = LocalStorage(storage_dir=tmp_path / "media")
    metadata_store = SQLiteMetadataStore(db_path=tmp_path / "test.db")
    return SpectatorDB(storage=storage, metadata_store=metadata_store)


@pytest.fixture
def config(tmp_path):
    cfg = CollectorConfig()
    cfg.storage.tmp_dir = str(tmp_path / "tmp")
    return cfg


@pytest.mark.asyncio
async def test_pipeline_processes_image_task(db, config):
    queue: asyncio.Queue[CaptureTask | None] = asyncio.Queue()
    pipeline = CapturePipeline(queue=queue, db=db, config=config)

    frame = numpy.random.randint(0, 255, (480, 640, 3), dtype=numpy.uint8)
    task = CaptureTask(
        frames=[frame],
        captured_at=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
        media_type=MediaType.IMAGE,
    )

    await queue.put(task)
    await queue.put(None)  # Sentinel to stop

    await pipeline.run()

    records = db.query()
    assert len(records) == 1
    assert records[0].media_type == MediaType.IMAGE
    assert records[0].format == "jpg"


@pytest.mark.asyncio
async def test_pipeline_processes_video_task(db, config):
    queue: asyncio.Queue[CaptureTask | None] = asyncio.Queue()
    pipeline = CapturePipeline(queue=queue, db=db, config=config)

    frames = [
        numpy.random.randint(0, 255, (480, 640, 3), dtype=numpy.uint8) for _ in range(5)
    ]
    task = CaptureTask(
        frames=frames,
        captured_at=datetime(2025, 6, 15, 14, 0, 0, tzinfo=timezone.utc),
        media_type=MediaType.VIDEO,
        video_duration=0.25,
    )

    await queue.put(task)
    await queue.put(None)

    await pipeline.run()

    records = db.query()
    assert len(records) == 1
    assert records[0].media_type == MediaType.VIDEO
    assert records[0].format == "avi"
    assert records[0].duration == 0.25
