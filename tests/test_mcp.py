"""Tests for collector.mcp."""

import json

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from spectatordb.models import MediaRecord, MediaType

from collector.camera.monitor import CameraUnavailableError
from collector.mcp import create_mcp_server


def _make_mcp():
    service = MagicMock()
    mcp = create_mcp_server(service)
    return mcp, service


def _payload(result):
    """Return a tool result's value, whichever shape mcp 2.x used for it.

    2.x returns a ``CallToolResult`` instead of the bare sequence of content
    blocks 1.x returned, and it serializes the two return types differently:
    a tool declaring ``-> list[...]`` carries the real value in
    ``structured_content["result"]`` and emits one content block per element
    (so an empty list emits none), while a tool declaring ``-> dict`` leaves
    ``structured_content`` unset and emits a single JSON block. Both are
    normalized back to the value the tool actually returned.
    """
    assert result.is_error is False
    if result.structured_content is not None:
        return result.structured_content["result"]
    assert result.content, "tool returned neither structured content nor blocks"
    return json.loads(result.content[0].text)


def _make_record(**kwargs):
    defaults = dict(
        media_type=MediaType.IMAGE,
        captured_at=datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
        format="jpg",
        size=100,
    )
    defaults.update(kwargs)
    return MediaRecord(**defaults)


@pytest.mark.asyncio
async def test_query_media_tool():
    mcp, service = _make_mcp()
    record = _make_record()
    service.query_media.return_value = [record]

    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "query_media" in tool_names

    result = await mcp.call_tool("query_media", {"limit": 10})
    service.query_media.assert_called_once_with(
        start=None,
        end=None,
        media_type=None,
        device_id=None,
        labels=None,
        limit=10,
        offset=None,
    )

    records = _payload(result)
    assert len(records) == 1
    assert records[0]["media_type"] == MediaType.IMAGE.value


@pytest.mark.asyncio
async def test_query_media_with_media_type():
    mcp, service = _make_mcp()
    service.query_media.return_value = []

    await mcp.call_tool("query_media", {"media_type": "image"})
    call_kwargs = service.query_media.call_args.kwargs
    assert call_kwargs["media_type"] == MediaType.IMAGE


@pytest.mark.asyncio
async def test_query_media_with_labels():
    mcp, service = _make_mcp()
    service.query_media.return_value = []

    await mcp.call_tool("query_media", {"labels": ["person", "car"]})
    call_kwargs = service.query_media.call_args.kwargs
    assert call_kwargs["labels"] == ["person", "car"]


@pytest.mark.asyncio
async def test_query_media_returns_empty_list_when_nothing_matches():
    """An empty result emits zero content blocks under mcp 2.x."""
    mcp, service = _make_mcp()
    service.query_media.return_value = []

    result = await mcp.call_tool("query_media", {"limit": 10})
    assert _payload(result) == []


@pytest.mark.asyncio
async def test_get_record_tool():
    mcp, service = _make_mcp()
    record = _make_record(id="test-id")
    service.get_record.return_value = record

    result = await mcp.call_tool("get_record", {"id": "test-id"})
    service.get_record.assert_called_once_with("test-id")
    assert _payload(result)["id"] == "test-id"


@pytest.mark.asyncio
async def test_device_status_tool():
    mcp, service = _make_mcp()
    service.device_status.return_value = {"cpu": "ok", "memory": "ok"}

    result = await mcp.call_tool("device_status", {})
    service.device_status.assert_called_once()
    assert _payload(result) == {"cpu": "ok", "memory": "ok"}


@pytest.mark.asyncio
async def test_capture_now_tool():
    mcp, service = _make_mcp()
    service.capture_now.return_value = {"status": "capture requested"}

    result = await mcp.call_tool("capture_now", {})
    service.capture_now.assert_called_once()
    assert _payload(result) == {"status": "capture requested"}


@pytest.mark.asyncio
async def test_capture_now_tool_errors_when_camera_unavailable():
    mcp, service = _make_mcp()
    service.capture_now.side_effect = CameraUnavailableError(
        "Camera 0 is failed: Cannot open camera 0"
    )

    with pytest.raises(Exception, match="Cannot open camera 0"):
        await mcp.call_tool("capture_now", {})


@pytest.mark.asyncio
async def test_all_tools_registered():
    mcp, _ = _make_mcp()
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    assert tool_names == {"query_media", "get_record", "device_status", "capture_now"}
