"""MCP server for Spectator Data Collector.

Exposes the same operations as the REST API (except file download)
by delegating to :class:`collector.service.SpectatorService`.

Claude on the user's laptop connects via MCP over the LAN to perform
natural language queries on captured media.
"""

import dataclasses
import logging

from datetime import datetime

from mcp.server.mcpserver import MCPServer

from spectatordb.models import MediaType

from collector.service import SpectatorService

logger = logging.getLogger(__name__)


def create_mcp_server(service: SpectatorService) -> MCPServer:
    """Create the MCP server with tools backed by the shared service layer.

    Parameters
    ----------
    service : SpectatorService
        The shared service layer (same instance used by REST).

    Returns
    -------
    MCPServer
        The configured MCP server.
    """
    mcp = MCPServer(
        name="spectator",
        instructions=(
            "Spectator Data Collector MCP server. "
            "Use these tools to query captured images and videos "
            "from the IoT Spectator device, check device health, "
            "and trigger on-demand captures."
        ),
    )

    @mcp.tool(
        name="query_media",
        description=(
            "Query captured media records with composable filters. "
            "All parameters are optional. Returns a list of matching records "
            "ordered by capture time (newest first). "
            "Labels use ANY-match semantics (at least one label matches)."
        ),
    )
    def query_media(
        start: datetime | None = None,
        end: datetime | None = None,
        media_type: str | None = None,
        device_id: str | None = None,
        labels: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict]:
        mt = MediaType(media_type) if media_type else None
        records = service.query_media(
            start=start,
            end=end,
            media_type=mt,
            device_id=device_id,
            labels=labels,
            limit=limit,
            offset=offset,
        )
        return [dataclasses.asdict(r) for r in records]

    @mcp.tool(
        name="get_record",
        description="Get a single media record's metadata by its ID.",
    )
    def get_record(id: str) -> dict:
        record = service.get_record(id)
        return dataclasses.asdict(record)

    @mcp.tool(
        name="device_status",
        description=(
            "Get the current health status of the IoT device, "
            "including CPU usage, memory, disk capacity, temperature, "
            "and connected cameras. The 'camera' field reports whether the "
            "capture monitor is running and, if not, why it failed."
        ),
    )
    def device_status() -> dict:
        return service.device_status()

    @mcp.tool(
        name="capture_now",
        description=(
            "Trigger an immediate image or video capture from the camera. "
            "Fails with an error if the camera is unavailable; call "
            "device_status to see why."
        ),
    )
    def capture_now() -> dict:
        return service.capture_now()

    return mcp
