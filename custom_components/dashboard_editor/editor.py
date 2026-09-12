"""The editing session: list YAML dashboards, resolve one, plan and commit a write-back."""

from __future__ import annotations

import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from homeassistant.components.lovelace.const import LOVELACE_DATA, MODE_YAML
from homeassistant.core import HomeAssistant

from .const import BACKUP_DIR, BACKUP_KEEP, DEFAULT_DASHBOARD_ID, DEFAULT_YAML_FILE, SCRATCH_PREFIX
from .dashboards_config import DashboardsConfig
from .reconcile import Plan, Reconciler
from .yaml_files import DashboardFileError, DashboardFiles

_LOGGER = logging.getLogger(__name__)


class DashboardEditor:
    """Stateless service over the configuration directory; every call reloads the files."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    def _files(self) -> DashboardFiles:
        return DashboardFiles(self.hass.config.config_dir)

    def yaml_dashboards(self) -> dict[str, dict[str, Any]]:
        """YAML-mode dashboards Home Assistant registered, keyed by the editor's id."""
        data = self.hass.data.get(LOVELACE_DATA)
        result: dict[str, dict[str, Any]] = {}
        if data is None:
            return result
        for url_path, config in data.dashboards.items():
            if config.mode != MODE_YAML:
                continue
            dashboard_id = url_path or DEFAULT_DASHBOARD_ID
            declared = config.config or {}
            path = getattr(config, "path", None) or self.hass.config.path(DEFAULT_YAML_FILE)
            result[dashboard_id] = {
                "id": dashboard_id,
                "url_path": url_path or DEFAULT_DASHBOARD_ID,
                "title": declared.get("title") or dashboard_id,
                "icon": declared.get("icon"),
                "file": path,
                "scratch_url_path": f"{SCRATCH_PREFIX}{dashboard_id}",
            }
        return result

    def list_dashboards(self) -> dict[str, Any]:
        files = self._files()
        data = self.hass.data.get(LOVELACE_DATA)
        dashboards = []
        for item in self.yaml_dashboards().values():
            entry = {**item}
            try:
                path = files.path_for(item["file"])
                entry["file"] = files.relative(path)
                files.resolve(files.load(path), path)
                entry["includes"] = [f for f in files.loaded_files() if f != entry["file"]]
                entry["supported"] = True
                entry["problem"] = None
            except DashboardFileError as err:
                entry["file"] = str(item["file"])
                entry["includes"] = []
                entry["supported"] = False
                entry["problem"] = str(err)
            files = self._files()
            dashboards.append(entry)
        return {
            "dashboards": dashboards,
            "resource_mode": data.resource_mode if data else None,
            "config_dir": str(files.config_dir),
        }

    def _root(self, files: DashboardFiles, dashboard_id: str) -> Path:
        item = self.yaml_dashboards().get(dashboard_id)
        if item is None:
            raise DashboardFileError(f"{dashboard_id} is not a YAML dashboard")
        return files.path_for(item["file"])

    def resolve(self, dashboard_id: str) -> dict[str, Any]:
        files = self._files()
        root = self._root(files, dashboard_id)
        config = files.resolve(files.load(root), root)
        if not isinstance(config, dict):
            raise DashboardFileError(f"{files.relative(root)} is not a mapping at the top level")
        return {"config": config, "files": files.loaded_files()}

    def plan(self, dashboard_id: str, config: dict[str, Any]) -> tuple[Plan, DashboardFiles]:
        files = self._files()
        root = self._root(files, dashboard_id)
        reconciler = Reconciler(files)
        try:
            plan = reconciler.apply(root, config)
        except ValueError as err:
            raise DashboardFileError(str(err)) from err
        return plan, files

    def commit(self, dashboard_id: str, config: dict[str, Any]) -> dict[str, Any]:
        plan, files = self.plan(dashboard_id, config)
        changed = files.changed_files(set(plan.files))
        backup = None
        if changed:
            backup = self._backup(files, list(changed))
            for path, text in changed.items():
                files.write(path, text)
        result = plan.as_dict()
        result["written"] = sorted(files.relative(p) for p in changed)
        result["backup"] = backup
        return result

    def _backup(self, files: DashboardFiles, paths: list[Path]) -> str:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        root = files.config_dir / BACKUP_DIR
        target = root / stamp
        for path in paths:
            dest = target / files.relative(path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
        sets = sorted(p for p in root.iterdir() if p.is_dir()) if root.exists() else []
        for old in sets[:-BACKUP_KEEP]:
            shutil.rmtree(old, ignore_errors=True)
        return files.relative(target)

    def dashboards_config(self) -> DashboardsConfig:
        return DashboardsConfig(self._files())
