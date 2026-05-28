from __future__ import annotations

import json

_SCHEMA_VERSION = 1


class AmbiguousLabelError(Exception):
    """Raised when a prefix query matches different label values."""


class LabelRegistry:
    """Maps UUID or UUID prefix strings to labels."""

    def __init__(self) -> None:
        self._labels: dict[str, str] = {}

    def set(self, uuid_prefix: str, label: str) -> None:
        self._labels[uuid_prefix] = label

    def get(self, query: str) -> str | None:
        if query in self._labels:
            return self._labels[query]

        matches: dict[str, str] = {}
        for key, label in self._labels.items():
            if query.startswith(key) or key.startswith(query):
                matches[key] = label

        if not matches:
            return None

        distinct = set(matches.values())
        if len(distinct) == 1:
            return next(iter(distinct))

        raise AmbiguousLabelError(
            f"Prefix {query!r} matches {len(matches)} stored entries with "
            "different labels: "
            + ", ".join(f"{k!r}={v!r}" for k, v in sorted(matches.items()))
        )

    def save(self, path: str) -> None:
        payload = {
            "_meta": {"version": _SCHEMA_VERSION},
            "labels": dict(self._labels),
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    def load(self, path: str) -> None:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        self._labels.update(data.get("labels", {}))
