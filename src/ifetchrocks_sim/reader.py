from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ComponentNode, SaveModel, SaveSummary, ShipModel


class SaveReader:
    """Load I Fetch Rocks save data into structured summaries.

    This is intentionally small for the initial scaffold. Migrate richer parsing
    and simulation graph reconstruction from the existing project over time.
    """

    def load_save_path(self, path: str | Path) -> SaveModel:
        raw = Path(path).read_text(encoding="utf-8")
        payload = json.loads(raw)
        return self.parse_payload(payload)

    def parse_payload(self, payload: dict[str, Any]) -> SaveModel:
        ship_payload = payload.get("ship", {})
        rooms = [_parse_component(c) for c in ship_payload.get("rooms", []) if isinstance(c, dict)]
        floating = [
            _parse_component(c)
            for c in ship_payload.get("floating", [])
            if isinstance(c, dict)
        ]
        return SaveModel(
            ship=ShipModel(rooms=rooms, floating=floating),
            raw=payload,
        )

    def load_path(self, path: str | Path) -> SaveSummary:
        return SaveSummary.from_save_model(self.load_save_path(path))

    def load_payload(self, payload: dict[str, Any]) -> SaveSummary:
        return SaveSummary.from_save_model(self.parse_payload(payload))


def _parse_component(component: dict[str, Any]) -> ComponentNode:
    children = [
        _parse_component(child)
        for child in component.get("children", [])
        if isinstance(child, dict)
    ]

    indexed_children: dict[str, ComponentNode] = {}
    for key, value in component.get("indexedChildren", {}).items():
        if isinstance(value, dict):
            indexed_children[str(key)] = _parse_component(value)

    return ComponentNode(
        type_id=component.get("type"),
        uuid=component.get("uuid"),
        children=children,
        indexed_children=indexed_children,
        raw=component,
    )
