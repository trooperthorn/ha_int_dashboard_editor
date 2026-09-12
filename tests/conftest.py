"""Shared fixtures: a dashboard tree shaped like a real YAML-mode install."""

from __future__ import annotations

from pathlib import Path

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.dashboard_editor.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"

USER_ID = "0123456789abcdef0123456789abcdef"

FILES: dict[str, str] = {
    "configuration.yaml": "homeassistant:\n  name: Test\nlovelace: !include lovelace.yaml\n",
    "lovelace.yaml": (
        "# Dashboards block; resource_mode keeps HACS resources in storage.\n"
        "mode: yaml\n"
        "resource_mode: storage\n"
        "dashboards:\n"
        "  lovelace:\n"
        "    mode: yaml\n"
        "    title: Overview\n"
        "    icon: mdi:view-dashboard\n"
        "    show_in_sidebar: true\n"
        "    filename: dashboards/overview.yaml\n"
        "  mobile-dashboard:\n"
        "    mode: yaml\n"
        "    title: Mobile\n"
        "    icon: mdi:cellphone\n"
        "    show_in_sidebar: true\n"
        "    filename: dashboards/mobile.yaml\n"
    ),
    "dashboards/mobile.yaml": (
        "decluttering_templates: !include shared/templates.yaml\n"
        "title: Mobile\n"
        "views:\n"
        "  - title: Phone Overview  # the landing view\n"
        "    path: phone-overview\n"
        "    layout: null\n"
        "    header:\n"
        "      card: !include shared/weather_summary.yaml\n"
        "    cards:\n"
        "      - !include shared/security_chips.yaml\n"
        "      - type: entities\n"
        "        entities:\n"
        "          - light.hall\n"
        "      - type: markdown\n"
        "        content: |\n"
        "          Two\n"
        "          lines\n"
        "  - title: Garage\n"
        "    path: garage\n"
        "    cards: !include shared/rooms/garage.yaml\n"
        "  - title: Utility Room\n"
        "    path: utility-room\n"
        "    visible: true\n"
        "    cards: []\n"
    ),
    "dashboards/overview.yaml": (
        "title: Overview\n"
        "views:\n"
        "  - title: Home\n"
        "    path: home\n"
        "    cards: !include shared/rooms/garage.yaml\n"
    ),
    "dashboards/tablet.yaml": (
        "title: Tablet\n"
        "views:\n"
        "  - title: Kitchen\n"
        "    path: kitchen\n"
        "    visible: &kitchen_users\n"
        "      - user: " + USER_ID + "\n"
        "    cards: []\n"
        "  - title: Office\n"
        "    path: office\n"
        "    visible: *kitchen_users\n"
        "    cards: []\n"
    ),
    "dashboards/secret.yaml": "title: !secret dash_title\nviews: []\n",
    "dashboards/shared/templates.yaml": (
        "# Shared decluttering templates.\n"
        "room_card:\n"
        "  card:\n"
        "    type: custom:bubble-card\n"
        "    entity: light.[[room_id]]\n"
    ),
    "dashboards/shared/weather_summary.yaml": "type: weather-forecast\nentity: weather.home\n",
    "dashboards/shared/security_chips.yaml": (
        "type: custom:mushroom-chips-card\nchips:\n  - type: entity\n    entity: alarm_control_panel.home\n"
    ),
    "dashboards/shared/rooms/garage.yaml": (
        "- !include ../garage_status.yaml\n- type: tile\n  entity: cover.garage\n"
    ),
    "dashboards/shared/garage_status.yaml": "type: entity\nentity: binary_sensor.garage  # zone 7\n",
}


def write_tree(root: Path) -> None:
    for name, text in FILES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    write_tree(tmp_path)
    return tmp_path


@pytest.fixture
def config_entry() -> MockConfigEntry:
    return MockConfigEntry(domain=DOMAIN, title="Dashboard Editor", data={})


@pytest.fixture
async def setup_lovelace(hass: HomeAssistant, config_dir: Path) -> Path:
    hass.config.config_dir = str(config_dir)
    assert await async_setup_component(
        hass,
        "lovelace",
        {
            "lovelace": {
                "mode": "yaml",
                "resource_mode": "storage",
                "dashboards": {
                    "lovelace": {
                        "mode": "yaml",
                        "title": "Overview",
                        "filename": "dashboards/overview.yaml",
                    },
                    "mobile-dashboard": {
                        "mode": "yaml",
                        "title": "Mobile",
                        "icon": "mdi:cellphone",
                        "filename": "dashboards/mobile.yaml",
                    },
                    "tablet-dashboard": {
                        "mode": "yaml",
                        "title": "Tablet",
                        "filename": "dashboards/tablet.yaml",
                    },
                    "secret-dashboard": {
                        "mode": "yaml",
                        "title": "Secret",
                        "filename": "dashboards/secret.yaml",
                    },
                },
            }
        },
    )
    await hass.async_block_till_done()
    return config_dir


@pytest.fixture
async def setup_entry(hass: HomeAssistant, setup_lovelace: Path, config_entry: MockConfigEntry, monkeypatch):
    from custom_components.dashboard_editor import panel

    monkeypatch.setattr(panel, "bundle_token_sync", lambda _path: "0123456789abcdef")
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
