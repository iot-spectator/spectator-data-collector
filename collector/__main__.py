"""Run Spectator Data Collector as a module."""

import argparse
import asyncio
import pathlib

from collector.config import load_config
from collector.collector import SpectatorDataCollector


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Spectator Data Collector")
    parser.add_argument(
        "--config", type=pathlib.Path, default=None,
        help="Path to TOML configuration file.",
    )
    args = parser.parse_args()
    config = load_config(args.config)
    collector = SpectatorDataCollector(config)
    asyncio.run(collector.run())


if __name__ == "__main__":
    main()
