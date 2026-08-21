"""Tests for collector.collector wiring."""

from unittest.mock import MagicMock, patch

from collector.collector import create_mcp_app
from collector.config import CollectorConfig


def test_mcp_app_is_bound_to_the_configured_host():
    """The configured bind host reaches sse_app(), not sse_app()'s default.

    mcp 2.x turns on DNS rebinding protection whenever ``sse_app()``'s host is
    a loopback address, and its default is ``127.0.0.1``. Letting that default
    stand while uvicorn binds ``0.0.0.0`` would serve LAN clients an app that
    rejects them — a silent failure, since nothing raises at startup.
    """
    config = CollectorConfig()
    config.mcp.host = "0.0.0.0"

    with patch("collector.collector.create_mcp_server") as create_server:
        create_mcp_app(MagicMock(), config)

    create_server.return_value.sse_app.assert_called_once_with(host="0.0.0.0")


def test_mcp_app_passes_a_custom_host_through():
    config = CollectorConfig()
    config.mcp.host = "192.168.1.50"

    with patch("collector.collector.create_mcp_server") as create_server:
        create_mcp_app(MagicMock(), config)

    create_server.return_value.sse_app.assert_called_once_with(host="192.168.1.50")


def test_mcp_app_returns_a_real_asgi_app():
    """Guard against the helper returning the server instead of its app."""
    config = CollectorConfig()
    config.mcp.host = "0.0.0.0"

    app = create_mcp_app(MagicMock(), config)

    assert callable(app)
    assert any(getattr(route, "path", None) == "/sse" for route in app.routes)
