"""Tests for Goggles user configuration."""

from pathlib import Path
from goggles.config import load_user_config


def test_load_user_config(tmp_path: Path, monkeypatch):
    cfg_file = tmp_path / "goggles" / "goggles.toml"
    cfg_file.parent.mkdir(parents=True)
    cfg_file.write_text('theme = "dark"\nport = 5000\n', encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    cfg = load_user_config()
    assert cfg.get("theme") == "dark"
    assert cfg.get("port") == 5000


def test_load_user_config_firn_fallback(tmp_path: Path, monkeypatch):
    cfg_file = tmp_path / "firn" / "firn.toml"
    cfg_file.parent.mkdir(parents=True)
    cfg_file.write_text('theme = "light"\nport = 8080\n', encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    cfg = load_user_config()
    assert cfg.get("theme") == "light"
    assert cfg.get("port") == 8080


def test_load_user_config_empty(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    cfg = load_user_config()
    assert cfg == {}
