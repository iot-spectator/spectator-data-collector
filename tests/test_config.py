"""Tests for collector.config."""

from collector.config import (
    CollectorConfig,
    load_config,
)


def test_defaults():
    config = CollectorConfig()
    assert config.device.camera_index == 0
    assert config.device.device_id == "pi-01"
    assert config.motion.sensitivity == 0.005
    assert config.capture.mode == "image"
    assert config.capture.video_duration == 10.0
    assert config.storage.media_dir == "./media"
    assert config.storage.db_path == "./spectator.db"
    assert config.storage.tmp_dir == "./tmp"
    assert config.server.host == "0.0.0.0"
    assert config.server.port == 13722
    assert config.enrichment.enabled is False


def test_load_config_none():
    config = load_config(None)
    assert config.device.device_id == "pi-01"


def test_load_config_from_toml(tmp_path):
    toml_file = tmp_path / "test.toml"
    toml_file.write_text("""
[device]
camera_index = 2
device_id = "pi-03"

[motion]
sensitivity = 0.01

[capture]
mode = "video"
video_duration = 15.0

[server]
port = 9999
""")
    config = load_config(toml_file)
    assert config.device.camera_index == 2
    assert config.device.device_id == "pi-03"
    assert config.motion.sensitivity == 0.01
    assert config.capture.mode == "video"
    assert config.capture.video_duration == 15.0
    assert config.server.port == 9999
    # Defaults for unset fields
    assert config.server.host == "0.0.0.0"
    assert config.storage.media_dir == "./media"
    assert config.enrichment.enabled is False


def test_load_config_partial_override(tmp_path):
    toml_file = tmp_path / "partial.toml"
    toml_file.write_text("""
[server]
port = 8080
""")
    config = load_config(toml_file)
    assert config.server.port == 8080
    assert config.server.host == "0.0.0.0"
    assert config.device.camera_index == 0
