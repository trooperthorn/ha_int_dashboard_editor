"""Diagnostics: which YAML dashboards are registered and whether their files resolve."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .editor import DashboardEditor


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    editor: DashboardEditor = hass.data[DOMAIN]
    listing = await hass.async_add_executor_job(editor.list_dashboards)
    listing.pop("config_dir", None)
    return listing
