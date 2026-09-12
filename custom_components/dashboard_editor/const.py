"""Constants for the Dashboard Editor integration."""

from __future__ import annotations

DOMAIN = "dashboard_editor"

SCRATCH_PREFIX = "edit-"
DEFAULT_DASHBOARD_ID = "lovelace"
DEFAULT_YAML_FILE = "ui-lovelace.yaml"

BACKUP_DIR = ".storage/dashboard_editor/backups"
BACKUP_KEEP = 20

DASHBOARD_FILE_TEMPLATE = """title: {title}
views:
  - title: Home
    path: home
    cards: []
"""
