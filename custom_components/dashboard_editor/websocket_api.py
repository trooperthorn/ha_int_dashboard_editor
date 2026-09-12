"""WebSocket commands for the panel. Every command needs an admin session."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .editor import DashboardEditor
from .yaml_files import DashboardFileError

ERR_DASHBOARD_FILE = "dashboard_file"


def _editor(hass: HomeAssistant) -> DashboardEditor:
    return hass.data[DOMAIN]


@callback
def async_register(hass: HomeAssistant) -> None:
    for handler in (
        ws_list,
        ws_resolve,
        ws_plan,
        ws_commit,
        ws_config_get,
        ws_config_set,
        ws_config_remove,
    ):
        websocket_api.async_register_command(hass, handler)


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/list"})
@websocket_api.async_response
async def ws_list(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    result = await hass.async_add_executor_job(_editor(hass).list_dashboards)
    connection.send_result(msg["id"], result)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/resolve", vol.Required("dashboard_id"): str}
)
@websocket_api.async_response
async def ws_resolve(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    try:
        result = await hass.async_add_executor_job(_editor(hass).resolve, msg["dashboard_id"])
    except DashboardFileError as err:
        connection.send_error(msg["id"], ERR_DASHBOARD_FILE, str(err))
        return
    connection.send_result(msg["id"], result)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/plan",
        vol.Required("dashboard_id"): str,
        vol.Required("config"): dict,
    }
)
@websocket_api.async_response
async def ws_plan(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    try:
        plan, _files = await hass.async_add_executor_job(
            _editor(hass).plan, msg["dashboard_id"], msg["config"]
        )
    except DashboardFileError as err:
        connection.send_error(msg["id"], ERR_DASHBOARD_FILE, str(err))
        return
    connection.send_result(msg["id"], plan.as_dict())


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/commit",
        vol.Required("dashboard_id"): str,
        vol.Required("config"): dict,
    }
)
@websocket_api.async_response
async def ws_commit(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    try:
        result = await hass.async_add_executor_job(
            _editor(hass).commit, msg["dashboard_id"], msg["config"]
        )
    except DashboardFileError as err:
        connection.send_error(msg["id"], ERR_DASHBOARD_FILE, str(err))
        return
    connection.send_result(msg["id"], result)


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/config/get"})
@websocket_api.async_response
async def ws_config_get(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    try:
        result = await hass.async_add_executor_job(_editor(hass).dashboards_config().entries)
    except DashboardFileError as err:
        connection.send_error(msg["id"], ERR_DASHBOARD_FILE, str(err))
        return
    connection.send_result(msg["id"], result)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/config/set",
        vol.Required("url_path"): str,
        vol.Required("filename"): str,
        vol.Optional("title"): vol.Any(None, str),
        vol.Optional("icon"): vol.Any(None, str),
        vol.Optional("show_in_sidebar"): vol.Any(None, bool),
        vol.Optional("require_admin"): vol.Any(None, bool),
        vol.Optional("create_file", default=False): bool,
    }
)
@websocket_api.async_response
async def ws_config_set(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    values: dict[str, Any] = {
        k: msg.get(k) for k in ("title", "icon", "show_in_sidebar", "require_admin", "filename") if k in msg
    }
    try:
        result = await hass.async_add_executor_job(
            _editor(hass).dashboards_config().upsert, msg["url_path"], values, msg["create_file"]
        )
    except DashboardFileError as err:
        connection.send_error(msg["id"], ERR_DASHBOARD_FILE, str(err))
        return
    connection.send_result(msg["id"], result)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/config/remove", vol.Required("url_path"): str}
)
@websocket_api.async_response
async def ws_config_remove(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    try:
        result = await hass.async_add_executor_job(
            _editor(hass).dashboards_config().remove, msg["url_path"]
        )
    except DashboardFileError as err:
        connection.send_error(msg["id"], ERR_DASHBOARD_FILE, str(err))
        return
    connection.send_result(msg["id"], result)
