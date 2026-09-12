"""Round-trip access to dashboard YAML files with `!include` kept as a tag.

Every file is loaded once per session with ruamel.yaml in round-trip mode, so
comments, key order, quoting, and anchors survive a write. `!include` nodes stay
IncludeTag objects in the tree and are followed only when a resolved copy is
requested. Path rules and the refusal list are in docs/design.md.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from homeassistant.exceptions import HomeAssistantError
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq, TaggedScalar
from ruamel.yaml.scalarstring import LiteralScalarString


class DashboardFileError(HomeAssistantError):
    """A dashboard file could not be used; the message says why."""


class IncludeTag:
    """A `!include <relative path>` scalar kept verbatim in the tree."""

    yaml_tag = "!include"

    def __init__(self, path: str) -> None:
        self.path = path

    def __repr__(self) -> str:
        return f"IncludeTag({self.path!r})"

    @classmethod
    def from_yaml(cls, constructor: Any, node: Any) -> IncludeTag:
        return cls(str(constructor.construct_scalar(node)).strip())

    @classmethod
    def to_yaml(cls, representer: Any, data: IncludeTag) -> Any:
        return representer.represent_scalar(cls.yaml_tag, data.path)


def make_yaml() -> YAML:
    """A round-trip loader and dumper in the style Home Assistant files use."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.register_class(IncludeTag)
    yaml.representer.add_representer(type(None), _represent_null)
    return yaml


def _represent_null(representer: Any, _data: Any) -> Any:
    """Keep `null` spelled out; ruamel's default writes an empty value."""
    return representer.represent_scalar("tag:yaml.org,2002:null", "null")


def yaml_string(value: str) -> Any:
    """Multi-line text is written as a literal block, single lines as they are."""
    if "\n" in value:
        return LiteralScalarString(value)
    return value


def is_anchored(node: Any) -> bool:
    """True when the node carries a YAML anchor (and so may be aliased elsewhere)."""
    anchor = getattr(node, "anchor", None)
    return bool(anchor is not None and getattr(anchor, "value", None))


class DashboardFiles:
    """Loads, resolves, and writes the YAML files under one configuration directory."""

    def __init__(self, config_dir: str | Path) -> None:
        self.config_dir = Path(config_dir).resolve()
        self._yaml = make_yaml()
        self._docs: dict[Path, Any] = {}
        self._texts: dict[Path, str] = {}

    def path_for(self, relative: str, base: Path | None = None) -> Path:
        """Resolve a path from the configuration directory or from another file's folder.

        The result must stay inside the configuration directory; `..` escapes,
        absolute paths outside it, and symlinks that leave it are refused.
        """
        candidate = Path(relative)
        if not candidate.is_absolute():
            root = base.parent if base is not None else self.config_dir
            candidate = root / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.config_dir)
        except ValueError as err:
            raise DashboardFileError(
                f"{relative} points outside the configuration directory"
            ) from err
        return resolved

    def relative(self, path: Path) -> str:
        return path.resolve().relative_to(self.config_dir).as_posix()

    def load(self, path: Path) -> Any:
        """The round-trip document for a file, loaded once and cached."""
        if path in self._docs:
            return self._docs[path]
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError as err:
            raise DashboardFileError(f"{self.relative(path)} does not exist") from err
        except OSError as err:
            raise DashboardFileError(f"{self.relative(path)} could not be read: {err}") from err
        try:
            doc = self._yaml.load(text)
        except Exception as err:
            raise DashboardFileError(f"{self.relative(path)} is not valid YAML: {err}") from err
        self._docs[path] = doc
        self._texts[path] = text
        return doc

    def loaded_files(self) -> list[str]:
        return sorted(self.relative(p) for p in self._docs)

    def include_target(self, tag: IncludeTag, base: Path) -> Path:
        return self.path_for(tag.path, base)

    def resolve(self, node: Any, base: Path, seen: tuple[Path, ...] = ()) -> Any:
        """Plain Python data with every `!include` expanded, as Home Assistant would load it."""
        if isinstance(node, IncludeTag):
            target = self.include_target(node, base)
            if target in seen:
                raise DashboardFileError(f"{self.relative(target)} includes itself")
            return self.resolve(self.load(target), target, (*seen, target))
        if isinstance(node, TaggedScalar):
            tag = getattr(node.tag, "value", node.tag)
            raise DashboardFileError(
                f"{self.relative(base)} uses {tag}, which the editor does not resolve"
            )
        if isinstance(node, CommentedMap):
            if getattr(node, "merge", None):
                raise DashboardFileError(
                    f"{self.relative(base)} uses a merge key (<<), which the editor does not support"
                )
            return {str(k): self.resolve(v, base, seen) for k, v in node.items()}
        if isinstance(node, CommentedSeq):
            return [self.resolve(v, base, seen) for v in node]
        if isinstance(node, dict):
            return {str(k): self.resolve(v, base, seen) for k, v in node.items()}
        if isinstance(node, list):
            return [self.resolve(v, base, seen) for v in node]
        return plain_scalar(node)

    def dump(self, doc: Any) -> str:
        from io import StringIO

        out = StringIO()
        self._yaml.dump(doc, out)
        text = out.getvalue()
        # A file whose root is a list (a cards fragment) is written with the
        # dashes in column 0, the way Home Assistant users write them; the
        # dumper's sequence offset otherwise indents the whole file by two.
        if isinstance(doc, CommentedSeq):
            text = "\n".join(
                line[2:] if line.startswith("  ") else line for line in text.split("\n")
            )
        return text

    def changed_files(self, only: set[str] | None = None) -> dict[Path, str]:
        """Files whose in-memory document no longer matches the text on disk.

        `only` limits the answer to files a reconcile touched, so a file that
        merely round-trips with different formatting is never rewritten.
        """
        changed: dict[Path, str] = {}
        for path, doc in self._docs.items():
            if only is not None and self.relative(path) not in only:
                continue
            text = self.dump(doc)
            if text != self._texts[path]:
                changed[path] = text
        return changed

    def write(self, path: Path, text: str) -> None:
        """Atomic replace so a crash never leaves a half-written dashboard."""
        tmp = path.with_name(f".{path.name}.dashboard_editor.tmp")
        tmp.write_text(text, encoding="utf-8", newline="\n")
        os.replace(tmp, path)
        self._texts[path] = text


def plain_scalar(value: Any) -> Any:
    """Strip ruamel scalar wrappers so equality against JSON from the frontend holds."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return float(value)
    if isinstance(value, str):
        return str(value)
    return value
