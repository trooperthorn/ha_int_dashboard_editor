"""The panel's commands against a real lovelace setup with YAML dashboards."""

from __future__ import annotations

from pathlib import Path

from homeassistant.core import HomeAssistant

from .conftest import USER_ID


async def _call(client, payload: dict):
    await client.send_json_auto_id(payload)
    return await client.receive_json()


async def test_list_resolve_plan_commit(hass: HomeAssistant, hass_ws_client, setup_entry, config_dir: Path) -> None:
    client = await hass_ws_client(hass)

    listing = await _call(client, {"type": "dashboard_editor/list"})
    assert listing["success"]
    by_id = {d["id"]: d for d in listing["result"]["dashboards"]}
    assert set(by_id) == {"lovelace", "mobile-dashboard", "tablet-dashboard", "secret-dashboard"}
    assert by_id["mobile-dashboard"]["file"] == "dashboards/mobile.yaml"
    assert by_id["mobile-dashboard"]["supported"] is True
    assert "dashboards/shared/garage_status.yaml" in by_id["mobile-dashboard"]["includes"]
    assert by_id["mobile-dashboard"]["scratch_url_path"] == "edit-mobile-dashboard"
    assert by_id["secret-dashboard"]["supported"] is False
    assert "!secret" in by_id["secret-dashboard"]["problem"]
    assert listing["result"]["resource_mode"] == "storage"

    resolved = await _call(client, {"type": "dashboard_editor/resolve", "dashboard_id": "mobile-dashboard"})
    assert resolved["success"]
    config = resolved["result"]["config"]
    assert config["views"][2]["title"] == "Utility Room"

    config["views"][2]["visible"] = [{"user": USER_ID}]
    plan = await _call(client, {"type": "dashboard_editor/plan", "dashboard_id": "mobile-dashboard", "config": config})
    assert plan["success"]
    assert plan["result"]["files"] == ["dashboards/mobile.yaml"]
    assert (config_dir / "dashboards" / "mobile.yaml").read_text(encoding="utf-8").count(USER_ID) == 0

    commit = await _call(client, {"type": "dashboard_editor/commit", "dashboard_id": "mobile-dashboard", "config": config})
    assert commit["success"], commit
    assert commit["result"]["written"] == ["dashboards/mobile.yaml"]
    assert commit["result"]["backup"].startswith(".storage/dashboard_editor/backups/")
    text = (config_dir / "dashboards" / "mobile.yaml").read_text(encoding="utf-8")
    assert f"    visible:\n      - user: {USER_ID}\n" in text
    backup = config_dir / commit["result"]["backup"] / "dashboards" / "mobile.yaml"
    assert backup.read_text(encoding="utf-8").count(USER_ID) == 0

    reloaded = await _call(client, {"type": "lovelace/config", "url_path": "mobile-dashboard", "force": True})
    assert reloaded["success"]
    assert reloaded["result"]["views"][2]["visible"] == [{"user": USER_ID}]

    again = await _call(client, {"type": "dashboard_editor/commit", "dashboard_id": "mobile-dashboard", "config": config})
    assert again["success"] and again["result"]["written"] == [] and again["result"]["backup"] is None


async def test_errors_are_reported(hass: HomeAssistant, hass_ws_client, setup_entry) -> None:
    client = await hass_ws_client(hass)
    missing = await _call(client, {"type": "dashboard_editor/resolve", "dashboard_id": "nope"})
    assert not missing["success"] and missing["error"]["code"] == "dashboard_file"
    secret = await _call(client, {"type": "dashboard_editor/resolve", "dashboard_id": "secret-dashboard"})
    assert not secret["success"] and "!secret" in secret["error"]["message"]


async def test_dashboards_config_commands(hass: HomeAssistant, hass_ws_client, setup_entry, config_dir: Path) -> None:
    client = await hass_ws_client(hass)
    current = await _call(client, {"type": "dashboard_editor/config/get"})
    assert current["success"] and current["result"]["file"] == "lovelace.yaml"

    added = await _call(
        client,
        {
            "type": "dashboard_editor/config/set",
            "url_path": "garage-dashboard",
            "title": "Garage",
            "icon": "mdi:garage",
            "show_in_sidebar": True,
            "require_admin": False,
            "filename": "dashboards/garage.yaml",
            "create_file": True,
        },
    )
    assert added["success"] and added["result"]["restart_required"] is True
    assert (config_dir / "dashboards" / "garage.yaml").exists()

    bad = await _call(
        client,
        {"type": "dashboard_editor/config/set", "url_path": "bad", "filename": "dashboards/x.yaml", "create_file": True},
    )
    assert not bad["success"] and "hyphen" in bad["error"]["message"]

    removed = await _call(client, {"type": "dashboard_editor/config/remove", "url_path": "garage-dashboard"})
    assert removed["success"]
    after = await _call(client, {"type": "dashboard_editor/config/get"})
    assert [e["url_path"] for e in after["result"]["entries"]] == ["lovelace", "mobile-dashboard"]


async def test_non_admin_is_refused(hass: HomeAssistant, hass_ws_client, setup_entry, hass_read_only_access_token) -> None:
    client = await hass_ws_client(hass, hass_read_only_access_token)
    result = await _call(client, {"type": "dashboard_editor/list"})
    assert not result["success"] and result["error"]["code"] == "unauthorized"
