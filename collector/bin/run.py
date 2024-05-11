# Copyright © 2024 by IoT Spectator. All rights reserved.

"""Spectator Data Collector Entry."""

import uvicorn


def main() -> None:
    """Entry point."""
    uvicorn.run(app="collector.app:app", host="0.0.0.0", port=13722, reload=True)
