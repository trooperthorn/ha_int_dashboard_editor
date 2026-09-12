"""The dashboards block through an included lovelace.yaml and inline in configuration.yaml."""

from __future__ import annotations

from pathlib import Path

import pytest

from custom_components.dashboard_editor.dashboards_config import DashboardsConfig
from custom_components.dashboard_editor.yaml_files import DashboardFileError, DashboardFiles


def _config(config_dir: Path) -> DashboardsConfig:
    return DashboardsConfig(DashboardFiles(config_dir))


def test_entries_follow_the_include(config_dir: Path) -> None:
    result = _config(config_dir).entries()
    assert result["file"] == "lovelace.yaml"
    assert result["writable"] is True
    assert result["mode"] == "yaml"
    assert [e["url_path"] for e in result["entries"]] == ["lovelace", "mobile-dashboard"]
    assert result["entries"][1]["filename"] == "dashboards/mobile.yaml"


def test_add_dashboard_creates_file_and_keeps_comment(config_dir: Path) -> None:
    result = _config(config_dir).upsert(
        "garage-dashboard",
        {"title": "Garage", "icon": "mdi:garage", "show_in_sidebar": False, "filename": "dashboards/garage.yaml"},
        create_file=True,
    )
    assert result == {"created": True, "file_created": True, "restart_required": True}
    text = (config_dir / "lovelace.yaml").read_text(encoding="utf-8")
    assert text.startswith("# Dashboards block")
    assert (
        "  garage-dashboard:\n    mode: yaml\n    title: Garage\n    icon: mdi:garage\n"
        "    show_in_sidebar: false\n    filename: dashboards/garage.yaml\n"
    ) in text
    assert (config_dir / "dashboards" / "garage.yaml").read_text(encoding="utf-8").startswith("title: Garage\n")


def test_update_and_remove(config_dir: Path) -> None:
    cfg = _config(config_dir)
    result = cfg.upsert("mobile-dashboard", {"title": "Phone", "filename": "dashboards/mobile.yaml"}, False)
    assert result["created"] is False and result["file_created"] is False
    entries = _config(config_dir).entries()["entries"]
    assert entries[1]["title"] == "Phone" and entries[1]["icon"] == "mdi:cellphone"
    _config(config_dir).remove("mobile-dashboard")
    entries = _config(config_dir).entries()["entries"]
    assert [e["url_path"] for e in entries] == ["lovelace"]
    assert (config_dir / "dashboards" / "mobile.yaml").exists()


def test_validation(config_dir: Path) -> None:
    cfg = _config(config_dir)
    with pytest.raises(DashboardFileError, match="hyphen"):
        cfg.upsert("Garage", {"filename": "dashboards/g.yaml"}, True)
    with pytest.raises(DashboardFileError, match="yaml"):
        cfg.upsert("a-b", {"filename": "dashboards/g.txt"}, True)
    with pytest.raises(DashboardFileError, match="outside"):
        cfg.upsert("a-b", {"filename": "../g.yaml"}, True)
    with pytest.raises(DashboardFileError, match="does not exist"):
        cfg.upsert("a-b", {"filename": "dashboards/missing.yaml"}, False)
    with pytest.raises(DashboardFileError, match="not in the dashboards block"):
        cfg.remove("nope-nope")


def test_inline_block_and_missing_key(config_dir: Path) -> None:
    (config_dir / "configuration.yaml").write_text("homeassistant:\n  name: T\n", encoding="utf-8")
    cfg = _config(config_dir)
    assert cfg.entries() == {"file": "configuration.yaml", "writable": True, "problem": None, "entries": [], "mode": None}
    cfg.upsert("side-panel", {"title": "Side", "filename": "dashboards/side.yaml"}, True)
    text = (config_dir / "configuration.yaml").read_text(encoding="utf-8")
    assert "lovelace:\n  dashboards:\n    side-panel:\n      mode: yaml\n      title: Side\n" in text
    again = _config(config_dir).entries()
    assert again["file"] == "configuration.yaml" and [e["url_path"] for e in again["entries"]] == ["side-panel"]


def test_unwritable_shapes_are_reported(config_dir: Path) -> None:
    (config_dir / "configuration.yaml").write_text("lovelace: !include_dir_named lovelace\n", encoding="utf-8")
    result = _config(config_dir).entries()
    assert result["writable"] is False and "lovelace key" in result["problem"]
    with pytest.raises(DashboardFileError):
        _config(config_dir).remove("x-y")
