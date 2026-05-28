from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulatorFacade:
    """Placeholder facade for migrated simulator functionality.

    Keep this as the stable entry point while implementation details are moved
    from the existing monorepo.
    """

    tick: int = 0

    def set_tick(self, tick: int) -> None:
        self.tick = tick
