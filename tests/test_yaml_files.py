"""Loading, resolving, and the refusal list."""

from __future__ import annotations

from pathlib import Path

import pytest

from custom_components.dashboard_editor.yaml_files import DashboardFileError, DashboardFiles


def test_resolve_expands_nested_includes(config_dir: Path) -> None:
    files = DashboardFiles(config_dir)
    root = files.path_for("dashboards/mobile.yaml")
    config = files.resolve(files.load(root), root)
    assert config["decluttering_templates"]["room_card"]["card"]["type"] == "custom:bubble-card"
    assert config["views"][0]["header"]["card"]["type"] == "weather-forecast"
    assert config["views"][0]["cards"][0]["type"] == "custom:mushroom-chips-card"
    assert config["views"][0]["cards"][2]["content"] == "Two\nlines\n"
    assert config["views"][1]["cards"][0] == {"type": "entity", "entity": "binary_sensor.garage"}
    assert config["views"][0]["layout"] is None
    assert set(files.loaded_files()) == {
        "dashboards/mobile.yaml",
        "dashboards/shared/templates.yaml",
        "dashboards/shared/weather_summary.yaml",
        "dashboards/shared/security_chips.yaml",
        "dashboards/shared/rooms/garage.yaml",
        "dashboards/shared/garage_status.yaml",
    }


def test_aliases_resolve_to_copies(config_dir: Path) -> None:
    files = DashboardFiles(config_dir)
    root = files.path_for("dashboards/tablet.yaml")
    config = files.resolve(files.load(root), root)
    assert config["views"][0]["visible"] == config["views"][1]["visible"]


def test_secret_tag_is_refused(config_dir: Path) -> None:
    files = DashboardFiles(config_dir)
    root = files.path_for("dashboards/secret.yaml")
    with pytest.raises(DashboardFileError, match="!secret"):
        files.resolve(files.load(root), root)


def test_include_outside_config_dir_is_refused(config_dir: Path) -> None:
    (config_dir / "dashboards" / "escape.yaml").write_text(
        "title: x\nviews: !include ../../outside.yaml\n", encoding="utf-8"
    )
    files = DashboardFiles(config_dir)
    root = files.path_for("dashboards/escape.yaml")
    with pytest.raises(DashboardFileError, match="outside the configuration directory"):
        files.resolve(files.load(root), root)
    with pytest.raises(DashboardFileError):
        files.path_for("/etc/passwd")


def test_self_include_is_refused(config_dir: Path) -> None:
    (config_dir / "dashboards" / "loop.yaml").write_text(
        "title: x\nviews: !include loop.yaml\n", encoding="utf-8"
    )
    files = DashboardFiles(config_dir)
    root = files.path_for("dashboards/loop.yaml")
    with pytest.raises(DashboardFileError, match="includes itself"):
        files.resolve(files.load(root), root)


def test_missing_and_invalid_files(config_dir: Path) -> None:
    files = DashboardFiles(config_dir)
    with pytest.raises(DashboardFileError, match="does not exist"):
        files.load(files.path_for("dashboards/nope.yaml"))
    (config_dir / "dashboards" / "bad.yaml").write_text("views: [\n", encoding="utf-8")
    with pytest.raises(DashboardFileError, match="not valid YAML"):
        files.load(files.path_for("dashboards/bad.yaml"))


def test_dump_round_trips_untouched_files(config_dir: Path) -> None:
    files = DashboardFiles(config_dir)
    for rel in ("dashboards/mobile.yaml", "dashboards/shared/rooms/garage.yaml", "dashboards/tablet.yaml"):
        files.load(files.path_for(rel))
    assert files.changed_files() == {}
    assert files.changed_files({"dashboards/mobile.yaml"}) == {}
