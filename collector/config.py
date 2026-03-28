"""Configuration dataclasses and TOML loader."""

import pathlib
import tomllib

from dataclasses import dataclass, field


@dataclass
class DeviceConfig:
    """Device configuration."""

    camera_index: int = 0
    device_id: str = "pi-01"


@dataclass
class MotionConfig:
    """Motion detection configuration."""

    sensitivity: float = 0.005


@dataclass
class CaptureConfig:
    """Capture configuration."""

    mode: str = "image"
    video_duration: float = 10.0


@dataclass
class StorageConfig:
    """Storage paths configuration."""

    media_dir: str = "./media"
    db_path: str = "./spectator.db"
    tmp_dir: str = "./tmp"


@dataclass
class ServerConfig:
    """Server configuration."""

    host: str = "0.0.0.0"
    port: int = 13722


@dataclass
class EnrichmentConfig:
    """Enrichment configuration."""

    enabled: bool = False


@dataclass
class CollectorConfig:
    """Top-level configuration composing all sub-configs."""

    device: DeviceConfig = field(default_factory=DeviceConfig)
    motion: MotionConfig = field(default_factory=MotionConfig)
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    enrichment: EnrichmentConfig = field(default_factory=EnrichmentConfig)


def load_config(path: pathlib.Path | None = None) -> CollectorConfig:
    """Load configuration from a TOML file.

    Parameters
    ----------
    path : pathlib.Path | None
        Path to the TOML config file. If ``None``, returns defaults.

    Returns
    -------
    CollectorConfig
        The loaded configuration.
    """
    config = CollectorConfig()
    if path is None:
        return config

    with open(path, "rb") as f:
        data = tomllib.load(f)

    section_map = {
        "device": (config.device, DeviceConfig),
        "motion": (config.motion, MotionConfig),
        "capture": (config.capture, CaptureConfig),
        "storage": (config.storage, StorageConfig),
        "server": (config.server, ServerConfig),
        "enrichment": (config.enrichment, EnrichmentConfig),
    }

    for section_name, (section_obj, _) in section_map.items():
        if section_name in data:
            for key, value in data[section_name].items():
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)

    return config
