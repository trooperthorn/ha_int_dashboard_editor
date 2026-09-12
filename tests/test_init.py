"""Setup, panel lifecycle, config flow, and diagnostics."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.config_entries import SOURCE_USER, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.dashboard_editor import panel
from custom_components.dashboard_editor.const import DOMAIN


async def test_setup_registers_panel_and_unload_removes_it(hass: HomeAssistant, setup_entry, monkeypatch) -> None:
    assert setup_entry.state is ConfigEntryState.LOADED
    assert "dashboard_editor" in hass.data["frontend_panels"]
    assert await hass.config_entries.async_unload(setup_entry.entry_id)
    await hass.async_block_till_done()
    assert "dashboard_editor" not in hass.data["frontend_panels"]


async def test_missing_bundle_skips_panel(hass: HomeAssistant, monkeypatch) -> None:
    monkeypatch.setattr(panel, "bundle_token_sync", lambda _path: None)
    register = AsyncMock()
    monkeypatch.setattr(panel.panel_custom, "async_register_panel", register)
    await panel.async_register_panel(hass)
    register.assert_not_called()


async def test_config_flow_single_instance(hass: HomeAssistant, setup_lovelace, monkeypatch) -> None:
    monkeypatch.setattr(panel, "bundle_token_sync", lambda _path: "abc")
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    second = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert second["type"] is FlowResultType.ABORT
    assert second["reason"] == "single_instance_allowed"


async def test_diagnostics(hass: HomeAssistant, setup_entry) -> None:
    from custom_components.dashboard_editor.diagnostics import async_get_config_entry_diagnostics

    data = await async_get_config_entry_diagnostics(hass, setup_entry)
    assert "config_dir" not in data
    assert {d["id"] for d in data["dashboards"]} >= {"mobile-dashboard", "lovelace"}
