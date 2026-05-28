from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ComponentNode:
    """Normalized component tree node from a game save."""

    type_id: int | None
    uuid: str | None
    children: list["ComponentNode"] = field(default_factory=list)
    indexed_children: dict[str, "ComponentNode"] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    def count(self) -> int:
        total = 1
        for child in self.children:
            total += child.count()
        for child in self.indexed_children.values():
            total += child.count()
        return total


@dataclass(frozen=True)
class ShipModel:
    """Structured ship payload containing room and floating component roots."""

    rooms: list[ComponentNode] = field(default_factory=list)
    floating: list[ComponentNode] = field(default_factory=list)

    def component_count(self) -> int:
        return sum(node.count() for node in self.rooms) + sum(node.count() for node in self.floating)


@dataclass(frozen=True)
class SaveModel:
    """Structured save payload wrapper."""

    ship: ShipModel
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SaveSummary:
    """Minimal summary extracted from a game save."""

    room_count: int
    floating_count: int
    device_count: int

    @classmethod
    def from_save_model(cls, save: SaveModel) -> "SaveSummary":
        return cls(
            room_count=len(save.ship.rooms),
            floating_count=len(save.ship.floating),
            device_count=save.ship.component_count(),
        )
