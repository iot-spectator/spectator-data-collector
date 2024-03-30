"""Spectator Data Collector Entry"""

import uvicorn


def main() -> None:
    uvicorn.run(app="collector.app:app", host="0.0.0.0", port=13722, reload=True)
