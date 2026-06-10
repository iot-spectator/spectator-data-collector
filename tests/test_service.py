"""Tests for collector.service."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from spectatordb.models import MediaRecord, MediaType

from collector.config import CollectorConfig
from collector.service import SpectatorService


def _make_service(tmp_path):
    config = CollectorConfig()
    config.storage.tmp_dir = str(tmp_path / "tmp")
    db = MagicMock()
    monitor = MagicMock()
    return SpectatorService(db=db, monitor=monitor, config=config), db, monitor


def test_query_media_delegates(tmp_path):
    service, db, _ = _make_service(tmp_path)
    db.query.return_value = []
    result = service.query_media(limit=10)
    db.query.assert_called_once_with(
        start=None, end=None, media_type=None,
        device_id=None, labels=None, limit=10, offset=None,
    )
    assert result == []


def test_get_record_delegates(tmp_path):
    service, db, _ = _make_service(tmp_path)
    record = MediaRecord(
        media_type=MediaType.IMAGE,
        captured_at=datetime.now(timezone.utc),
        format="jpg",
        size=100,
    )
    db.get.return_value = record
    result = service.get_record("some-id")
    db.get.assert_called_once_with("some-id")
    assert result is record


def test_retrieve_file_copies_to_tmp(tmp_path):
    service, db, _ = _make_service(tmp_path)
    record = MediaRecord(
        id="test-id",
        media_type=MediaType.IMAGE,
        captured_at=datetime.now(timezone.utc),
        format="jpg",
        size=100,
    )
    db.get.return_value = record
    db.retrieve.return_value = None
    path = service.retrieve_file("test-id")
    assert str(path).endswith("test-id.jpg")
    db.retrieve.assert_called_once_with("test-id", path)


def test_capture_now_calls_monitor(tmp_path):
    service, _, monitor = _make_service(tmp_path)
    result = service.capture_now()
    monitor.request_capture.assert_called_once()
    assert result["status"] == "capture requested"


def test_device_status_returns_dict(tmp_path):
    service, _, _ = _make_service(tmp_path)
    with patch("collector.service.DeviceHealth") as MockHealth:
        instance = MockHealth.return_value
        instance.summary.return_value = {"cpu": "ok"}
        result = service.device_status()
    assert result == {"cpu": "ok"}
