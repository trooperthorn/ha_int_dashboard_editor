"""Write-back: every change lands in the file that owns the node, and nothing else moves."""

from __future__ import annotations

import copy
import re
from pathlib import Path

from custom_components.dashboard_editor.reconcile import Reconciler
from custom_components.dashboard_editor.yaml_files import DashboardFiles

from .conftest import FILES, USER_ID

MOBILE = "dashboards/mobile.yaml"


def _load(config_dir: Path, rel: str = MOBILE):
    files = DashboardFiles(config_dir)
    root = files.path_for(rel)
    return files, root, files.resolve(files.load(root), root)


def _apply(files: DashboardFiles, root: Path, new):
    plan = Reconciler(files).apply(root, new)
    changed = {files.relative(p): text for p, text in files.changed_files(set(plan.files)).items()}
    return plan, changed


def test_no_change_is_a_no_op(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    plan, changed = _apply(files, root, copy.deepcopy(config))
    assert plan.changes == []
    assert plan.warnings == [] and plan.blocked == []
    assert changed == {}


def test_scalar_in_root_keeps_comments_and_includes(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    config["views"][0]["title"] = "Phone"
    plan, changed = _apply(files, root, config)
    assert [c.kind for c in plan.changes] == ["set"]
    assert plan.files == [MOBILE]
    text = changed[MOBILE]
    assert re.search(r"  - title: Phone +# the landing view\n", text)
    assert "card: !include shared/weather_summary.yaml" in text
    assert "- !include shared/security_chips.yaml" in text
    assert "cards: !include shared/rooms/garage.yaml" in text
    assert "layout: null" in text or "layout:\n" in text


def test_change_inside_nested_include_lands_in_fragment(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    config["views"][1]["cards"][0]["entity"] = "binary_sensor.garage_door"
    plan, changed = _apply(files, root, config)
    assert plan.files == ["dashboards/shared/garage_status.yaml"]
    assert re.fullmatch(
        r"type: entity\nentity: binary_sensor.garage_door +# zone 7\n",
        changed["dashboards/shared/garage_status.yaml"],
    )
    assert MOBILE not in changed


def test_view_visibility_write(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    config["views"][2]["visible"] = [{"user": USER_ID}]
    config["views"][2]["cards"].append({"type": "markdown", "content": "Laundry"})
    plan, changed = _apply(files, root, config)
    kinds = sorted(c.kind for c in plan.changes)
    assert kinds == ["insert", "replace", "resize"]
    text = changed[MOBILE]
    assert f"    visible:\n      - user: {USER_ID}\n" in text
    assert "    cards:\n      - type: markdown\n        content: Laundry\n" in text


def test_null_key_dropped_by_editor_is_not_a_removal(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    del config["views"][0]["layout"]
    plan, changed = _apply(files, root, config)
    assert plan.changes == []
    assert changed == {}


def test_remove_card_keeps_neighbours(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    del config["views"][0]["cards"][2]
    plan, changed = _apply(files, root, config)
    assert [c.kind for c in plan.changes] == ["remove", "resize"]
    text = changed[MOBILE]
    assert "markdown" not in text
    assert "- !include shared/security_chips.yaml\n      - type: entities\n" in text


def test_reorder_keeps_include_tags(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    cards = config["views"][0]["cards"]
    cards[0], cards[1] = cards[1], cards[0]
    plan, changed = _apply(files, root, config)
    assert [c.kind for c in plan.changes] == ["reorder"]
    text = changed[MOBILE]
    assert text.index("- type: entities") < text.index("- !include shared/security_chips.yaml")
    assert text.count("!include") == FILES[MOBILE].count("!include")


def test_modified_card_is_matched_by_identity(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    cards = config["views"][0]["cards"]
    cards.insert(0, {"type": "button", "entity": "switch.porch"})
    cards[2]["entities"].append("light.porch")
    plan, changed = _apply(files, root, config)
    kinds = sorted(c.kind for c in plan.changes)
    assert kinds == ["insert", "insert", "resize", "resize"]
    text = changed[MOBILE]
    assert "          - light.hall\n          - light.porch\n" in text
    assert "- !include shared/security_chips.yaml" in text


def test_include_replaced_by_other_kind_is_a_warning(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    config["views"][1]["cards"] = {"type": "markdown", "content": "gone"}
    plan, changed = _apply(files, root, config)
    assert any(c.kind == "include_dropped" for c in plan.changes)
    assert plan.warnings and "shared/rooms/garage.yaml" in plan.warnings[0]
    assert "!include shared/rooms/garage.yaml" not in changed[MOBILE]
    assert "dashboards/shared/rooms/garage.yaml" not in changed


def test_anchored_change_is_blocked(config_dir: Path) -> None:
    files, root, config = _load(config_dir, "dashboards/tablet.yaml")
    config["views"][1]["visible"] = True
    plan, changed = _apply(files, root, config)
    assert plan.blocked and "anchored" in plan.blocked[0]
    assert changed == {}


def test_multiline_string_becomes_literal_block(config_dir: Path) -> None:
    files, root, config = _load(config_dir)
    config["views"][0]["cards"][2]["content"] = "Three\nlines\nnow\n"
    _plan, changed = _apply(files, root, config)
    assert "        content: |\n          Three\n          lines\n          now\n" in changed[MOBILE]


def test_shared_fragment_edit_reaches_both_dashboards(config_dir: Path) -> None:
    files, root, config = _load(config_dir, "dashboards/overview.yaml")
    config["views"][0]["cards"][1]["name"] = "Big door"
    plan, changed = _apply(files, root, config)
    assert plan.files == ["dashboards/shared/rooms/garage.yaml"]
    assert "  name: Big door\n" in changed["dashboards/shared/rooms/garage.yaml"]
    other = DashboardFiles(config_dir)
    for rel, text in changed.items():
        other.write(other.path_for(rel), text)
    mobile_root = other.path_for(MOBILE)
    assert other.resolve(other.load(mobile_root), mobile_root)["views"][1]["cards"][1]["name"] == "Big door"
