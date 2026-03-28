"""Tests for collector.rest."""

import dataclasses

from datetime import datetime, timezone
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from spectatordb.models import MediaRecord, MediaType

from collector.rest import create_app


def _make_client(tmp_path):
    service = MagicMock()
    app = create_app(service)
    client = TestClient(app)
    return client, service


def test_root(tmp_path):
    client, _ = _make_client(tmp_path)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Welcome" in resp.json()["message"]


def test_health(tmp_path):
    client, service = _make_client(tmp_path)
    service.device_status.return_value = {"cpu": "ok"}
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"cpu": "ok"}


def test_query_media(tmp_path):
    client, service = _make_client(tmp_path)
    record = MediaRecord(
        media_type=MediaType.IMAGE,
        captured_at=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
        format="jpg",
        size=100,
    )
    service.query_media.return_value = [record]
    resp = client.get("/media")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["format"] == "jpg"


def test_get_record(tmp_path):
    client, service = _make_client(tmp_path)
    record = MediaRecord(
        id="test-id",
        media_type=MediaType.IMAGE,
        captured_at=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
        format="jpg",
        size=100,
    )
    service.get_record.return_value = record
    resp = client.get("/media/test-id")
    assert resp.status_code == 200
    assert resp.json()["id"] == "test-id"


def test_get_record_not_found(tmp_path):
    client, service = _make_client(tmp_path)
    service.get_record.side_effect = KeyError("not found")
    resp = client.get("/media/missing-id")
    assert resp.status_code == 404


def test_get_file(tmp_path):
    client, service = _make_client(tmp_path)
    # Create a real file for FileResponse
    file_path = tmp_path / "test.jpg"
    file_path.write_bytes(b"\xff\xd8\xff\xe0")
    service.retrieve_file.return_value = file_path
    resp = client.get("/media/test-id/file")
    assert resp.status_code == 200


def test_get_file_not_found(tmp_path):
    client, service = _make_client(tmp_path)
    service.retrieve_file.side_effect = KeyError("not found")
    resp = client.get("/media/missing-id/file")
    assert resp.status_code == 404


def test_capture(tmp_path):
    client, service = _make_client(tmp_path)
    service.capture_now.return_value = {"status": "capture requested"}
    resp = client.post("/capture")
    assert resp.status_code == 200
    assert resp.json()["status"] == "capture requested"
