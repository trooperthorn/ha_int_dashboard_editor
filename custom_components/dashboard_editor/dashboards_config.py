"""The `lovelace: dashboards:` block, read and written in place.

Home Assistant registers YAML dashboards once at startup, so every change here
needs a restart; the panel says so. The block may sit in configuration.yaml or
in a file it includes (`lovelace: !include lovelace.yaml`), and both are handled.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ruamel.yaml.comments import CommentedMap

from .const import DASHBOARD_FILE_TEMPLATE
from .yaml_files import DashboardFileError, DashboardFiles, IncludeTag

URL_PATH_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)+$|^lovelace$")
FILENAME_RE = re.compile(r"^[A-Za-z0-9_./-]+\.ya?ml$")
ENTRY_KEYS = ("mode", "title", "icon", "show_in_sidebar", "require_admin", "filename")


class DashboardsConfig:
    """Locates and edits the dashboards block for one configuration directory."""

    def __init__(self, files: DashboardFiles) -> None:
        self.files = files
        self.config_file = files.path_for("configuration.yaml")

    def locate(self) -> tuple[Path, CommentedMap, str | None]:
        """The file and mapping that hold `dashboards:`, or why they cannot be edited."""
        root = self.files.load(self.config_file)
        if not isinstance(root, CommentedMap):
            return self.config_file, root, "configuration.yaml is not a mapping"
        lovelace = root.get("lovelace")
        if lovelace is None:
            return self.config_file, root, None
        if isinstance(lovelace, IncludeTag):
            target = self.files.include_target(lovelace, self.config_file)
            included = self.files.load(target)
            if not isinstance(included, CommentedMap):
                return target, included, f"{self.files.relative(target)} is not a mapping"
            return target, included, None
        if isinstance(lovelace, CommentedMap):
            return self.config_file, root, None
        return self.config_file, root, "the lovelace key is not a mapping the editor can edit"

    def _block(self) -> tuple[Path, CommentedMap]:
        file, holder, problem = self.locate()
        if problem:
            raise DashboardFileError(problem)
        if file == self.config_file:
            lovelace = holder.get("lovelace")
            if lovelace is None:
                lovelace = CommentedMap()
                holder["lovelace"] = lovelace
        else:
            lovelace = holder
        dashboards = lovelace.get("dashboards")
        if dashboards is None:
            dashboards = CommentedMap()
            lovelace["dashboards"] = dashboards
        if not isinstance(dashboards, CommentedMap):
            raise DashboardFileError("lovelace.dashboards is not a mapping")
        return file, dashboards

    def entries(self) -> dict[str, Any]:
        file, holder, problem = self.locate()
        result: dict[str, Any] = {
            "file": self.files.relative(file),
            "writable": problem is None,
            "problem": problem,
            "entries": [],
        }
        if problem:
            return result
        lovelace = holder.get("lovelace") if file == self.config_file else holder
        dashboards = lovelace.get("dashboards") if isinstance(lovelace, CommentedMap) else None
        result["mode"] = lovelace.get("mode") if isinstance(lovelace, CommentedMap) else None
        if isinstance(dashboards, CommentedMap):
            for url_path, entry in dashboards.items():
                if not isinstance(entry, CommentedMap):
                    continue
                item = {"url_path": str(url_path)}
                for key in ENTRY_KEYS:
                    if key in entry:
                        item[key] = self.files.resolve(entry[key], file)
                result["entries"].append(item)
        return result

    def upsert(self, url_path: str, values: dict[str, Any], create_file: bool) -> dict[str, Any]:
        if not URL_PATH_RE.match(url_path):
            raise DashboardFileError(
                "the URL must be lowercase letters, digits and hyphens with at least one hyphen"
            )
        filename = str(values.get("filename") or "")
        if not FILENAME_RE.match(filename):
            raise DashboardFileError("the file name must end in .yaml and stay relative")
        target = self.files.path_for(filename)
        file, dashboards = self._block()
        entry = dashboards.get(url_path)
        created = False
        if entry is None:
            entry = CommentedMap()
            entry["mode"] = "yaml"
            dashboards[url_path] = entry
            created = True
        for key in ("title", "icon", "show_in_sidebar", "require_admin", "filename"):
            if key in values and values[key] is not None:
                entry[key] = values[key]
            elif key in entry and key in values and values[key] is None:
                del entry[key]
        file_created = False
        if not target.exists():
            if not create_file:
                raise DashboardFileError(f"{filename} does not exist; tick create file to add it")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                DASHBOARD_FILE_TEMPLATE.format(title=values.get("title") or url_path),
                encoding="utf-8",
                newline="\n",
            )
            file_created = True
        self._save(file)
        return {"created": created, "file_created": file_created, "restart_required": True}

    def remove(self, url_path: str) -> dict[str, Any]:
        file, dashboards = self._block()
        if url_path not in dashboards:
            raise DashboardFileError(f"{url_path} is not in the dashboards block")
        del dashboards[url_path]
        self._save(file)
        return {"restart_required": True}

    def _save(self, file: Path) -> None:
        text = self.files.dump(self.files.load(file))
        self.files.write(file, text)
