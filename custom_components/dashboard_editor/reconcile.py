"""Write an edited dashboard back into the YAML files it was assembled from.

The edited configuration comes from Home Assistant's storage copy as plain JSON.
The original is the round-trip tree with `!include` tags still in place. The
reconciler walks both together and mutates the round-trip tree in the file that
owns each node, so a change inside a shared fragment lands in the fragment file
and a change beside the include lands in the parent. The matching rules for
lists, the null rule, and the anchor refusal are explained in docs/design.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml.comments import CommentedMap, CommentedSeq, TaggedScalar

from .yaml_files import DashboardFiles, IncludeTag, is_anchored, plain_scalar, yaml_string


@dataclass
class Change:
    file: str
    path: str
    kind: str
    detail: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"file": self.file, "path": self.path, "kind": self.kind, "detail": self.detail}


@dataclass
class Plan:
    changes: list[Change] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)

    @property
    def files(self) -> list[str]:
        return sorted({c.file for c in self.changes})

    def as_dict(self) -> dict[str, Any]:
        return {
            "changes": [c.as_dict() for c in self.changes],
            "files": self.files,
            "warnings": self.warnings,
            "blocked": self.blocked,
        }


def _join(path: str, key: Any) -> str:
    if isinstance(key, int):
        return f"{path}[{key}]"
    return f"{path}.{key}" if path else str(key)


def _kind(value: Any) -> str:
    if isinstance(value, dict):
        return "map"
    if isinstance(value, list):
        return "list"
    return "scalar"


def _card_identity(value: Any) -> tuple[Any, Any] | None:
    """The pair a card is recognised by when its content changed: type plus a name-like key."""
    if not isinstance(value, dict):
        return None
    for key in ("path", "entity", "name", "title", "template"):
        if key in value:
            return (value.get("type"), value.get(key))
    return (value.get("type"), None)


class Reconciler:
    """Applies one edited dashboard to the round-trip documents behind it."""

    def __init__(self, files: DashboardFiles) -> None:
        self.files = files
        self.plan = Plan()

    def apply(self, root_file: Path, new_config: dict[str, Any]) -> Plan:
        doc = self.files.load(root_file)
        if not isinstance(doc, CommentedMap):
            raise ValueError(f"{self.files.relative(root_file)} is not a mapping at the top level")
        if not isinstance(new_config, dict):
            raise ValueError("the edited dashboard is not a mapping")
        self._map(doc, new_config, root_file, "")
        return self.plan

    def _rel(self, file: Path) -> str:
        return self.files.relative(file)

    def _record(self, file: Path, path: str, kind: str, detail: str = "") -> None:
        self.plan.changes.append(Change(self._rel(file), path or "(root)", kind, detail))

    def _blocked(self, file: Path, path: str, why: str) -> None:
        self.plan.blocked.append(f"{self._rel(file)} {path or '(root)'}: {why}")

    def _fresh(self, value: Any) -> Any:
        """A new subtree for the file, with multi-line strings as literal blocks."""
        if isinstance(value, dict):
            out = CommentedMap()
            for k, v in value.items():
                out[k] = self._fresh(v)
            return out
        if isinstance(value, list):
            seq = CommentedSeq()
            for v in value:
                seq.append(self._fresh(v))
            return seq
        if isinstance(value, str):
            return yaml_string(value)
        return value

    def _resolved(self, node: Any, file: Path) -> Any:
        return self.files.resolve(node, file)

    def _node(self, node: Any, new: Any, file: Path, path: str) -> tuple[bool, Any]:
        """Reconcile one node; returns (replace_in_parent, value)."""
        if isinstance(node, IncludeTag):
            return self._include(node, new, file, path)
        if isinstance(node, TaggedScalar):
            if self._resolved(node, file) != new:
                self._blocked(file, path, "tagged value changed; edit the file directly")
            return False, node
        if is_anchored(node) and self._resolved(node, file) != new:
            self._blocked(file, path, "anchored or aliased node changed; edit the file directly")
            return False, node
        if isinstance(node, CommentedMap) and isinstance(new, dict):
            self._map(node, new, file, path)
            return False, node
        if isinstance(node, CommentedSeq) and isinstance(new, list):
            self._list(node, new, file, path)
            return False, node
        if isinstance(node, (CommentedMap, CommentedSeq)) or isinstance(new, (dict, list)):
            self._record(file, path, "replace", f"{_kind(node)} became {_kind(new)}")
            return True, self._fresh(new)
        if plain_scalar(node) != new:
            self._record(file, path, "set", _preview(new))
            return True, self._fresh(new)
        return False, node

    def _include(self, tag: IncludeTag, new: Any, file: Path, path: str) -> tuple[bool, Any]:
        target = self.files.include_target(tag, file)
        included = self.files.load(target)
        if isinstance(included, CommentedMap) and isinstance(new, dict):
            self._map(included, new, target, "")
            return False, tag
        if isinstance(included, CommentedSeq) and isinstance(new, list):
            self._list(included, new, target, "")
            return False, tag
        if self._resolved(tag, file) == new:
            return False, tag
        self.plan.warnings.append(
            f"{self._rel(file)} {path}: the include of {tag.path} was replaced by an inline value"
        )
        self._record(file, path, "include_dropped", tag.path)
        return True, self._fresh(new)

    def _map(self, node: CommentedMap, new: dict[str, Any], file: Path, path: str) -> None:
        for key in list(node.keys()):
            if key in new:
                continue
            # Home Assistant's editor drops keys whose value is null; that is not a removal.
            if node[key] is None:
                continue
            if is_anchored(node[key]):
                self._blocked(file, _join(path, key), "anchored node removed; edit the file directly")
                continue
            del node[key]
            self._record(file, _join(path, key), "delete")
        for key, value in new.items():
            child_path = _join(path, key)
            if key not in node:
                node[key] = self._fresh(value)
                self._record(file, child_path, "add", _preview(value))
                continue
            replace, replacement = self._node(node[key], value, file, child_path)
            if replace:
                node[key] = replacement

    def _list(self, node: CommentedSeq, new: list[Any], file: Path, path: str) -> None:
        resolved = [self._resolved(item, file) for item in node]
        # Position by position when the shapes line up and nothing merely moved;
        # a moved card is found by the matching passes below instead.
        if len(node) == len(new) and all(
            _compatible(o, n) and (o == n or n not in resolved)
            for o, n in zip(resolved, new, strict=True)
        ):
            for index, (item, value) in enumerate(zip(list(node), new, strict=True)):
                replace, replacement = self._node(item, value, file, _join(path, index))
                if replace:
                    node[index] = replacement
            return

        used = [False] * len(node)
        pairing: list[int | None] = [None] * len(new)
        for j, value in enumerate(new):
            for i, original in enumerate(resolved):
                if not used[i] and original == value:
                    used[i] = True
                    pairing[j] = i
                    break
        for j, value in enumerate(new):
            if pairing[j] is not None:
                continue
            identity = _card_identity(value)
            best: int | None = None
            for i, original in enumerate(resolved):
                if used[i] or not _compatible(original, value):
                    continue
                if identity is not None and _card_identity(original) != identity:
                    continue
                if best is None or abs(i - j) < abs(best - j):
                    best = i
            if best is not None:
                used[best] = True
                pairing[j] = best

        for i, item in enumerate(node):
            if not used[i]:
                if is_anchored(item):
                    self._blocked(file, _join(path, i), "anchored item removed; edit the file directly")
                    continue
                self._record(file, _join(path, i), "remove", _preview(resolved[i]))

        rebuilt: list[Any] = []
        for j, value in enumerate(new):
            match = pairing[j]
            if match is None:
                rebuilt.append(self._fresh(value))
                self._record(file, _join(path, j), "insert", _preview(value))
                continue
            replace, replacement = self._node(node[match], value, file, _join(path, match))
            rebuilt.append(replacement if replace else node[match])
        for index, item in enumerate(node):
            if not used[index] and is_anchored(item):
                rebuilt.insert(min(index, len(rebuilt)), item)

        if [id(x) for x in rebuilt] != [id(x) for x in node]:
            if pairing != list(range(len(new))) or len(new) != len(node):
                self._record(file, path, "reorder" if len(new) == len(node) else "resize")
            del node[:]
            node.extend(rebuilt)


def _compatible(original: Any, new: Any) -> bool:
    return _kind(original) == _kind(new)


def _preview(value: Any) -> str:
    if isinstance(value, dict):
        kind = value.get("type")
        label = value.get("title") or value.get("name") or value.get("entity") or value.get("path")
        return f"{kind or 'map'}{f' {label}' if label else ''}"
    if isinstance(value, list):
        return f"list of {len(value)}"
    text = str(value)
    return text if len(text) <= 60 else text[:57] + "..."
