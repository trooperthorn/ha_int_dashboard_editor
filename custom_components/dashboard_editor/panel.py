"""Sidebar panel registration; the bundle is served from this package."""

from __future__ import annotations

import hashlib
import logging
import os

from homeassistant.components import panel_custom
from homeassistant.components.frontend import async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PANEL_NAME = "dashboard-editor-panel"
PANEL_URL = f"/api/panel_custom/{DOMAIN}"
PANEL_TITLE = "Dashboard editor"
PANEL_ICON = "mdi:view-dashboard-edit"
_STATIC_REGISTERED = f"{DOMAIN}.static_path_registered"


def bundle_path() -> str:
    return os.path.join(os.path.dirname(__file__), "frontend", "dist", f"{PANEL_NAME}.js")


def bundle_token_sync(path: str) -> str | None:
    """A content hash for cache busting; blocking, run in the executor."""
    try:
        with open(path, "rb") as handle:
            return hashlib.file_digest(handle, "sha256").hexdigest()[:16]
    except OSError:
        return None


async def async_register_panel(hass: HomeAssistant) -> None:
    path = bundle_path()
    token = await hass.async_add_executor_job(bundle_token_sync, path)
    if token is None:
        _LOGGER.warning("Frontend bundle missing at %s; the panel is not registered", path)
        return
    # aiohttp routes outlive panel removal, so the static path is added once per run.
    if not hass.data.get(_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(PANEL_URL, path, cache_headers=False)]
        )
        hass.data[_STATIC_REGISTERED] = True
    async_remove_panel(hass, DOMAIN, warn_if_unknown=False)
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_NAME,
        frontend_url_path=DOMAIN,
        module_url=f"{PANEL_URL}?v={token}",
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=True,
        config_panel_domain=DOMAIN,
    )


async def async_unregister_panel(hass: HomeAssistant) -> None:
    async_remove_panel(hass, DOMAIN, warn_if_unknown=False)
