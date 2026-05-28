"""FR-03: Tick Timeline Recorder — record all wire values during simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ifetchrocks_sim.simulator import Simulator


@dataclass
class WireSnapshot:
    """Wire values captured at a single tick (delta-encoded)."""
    tick: int
    wires: dict[str, int] = field(default_factory=dict)


class WireRecorder:
    """Records all data-network wire values on every tick via delta encoding.

    Usage::

        rec = WireRecorder(sim)
        rec.start()
        for t in range(1, 11):
            sim.set_tick(t)
        rec.stop()
        snapshots = rec.get_recording()
    """

    def __init__(self, sim: Simulator) -> None:
        self._sim = sim
        self._recording = False
        self._deltas: list[WireSnapshot] = []
        self._baseline: dict[str, int] = {}
        self._prev: dict[str, int] = {}

    def start(self) -> None:
        """Begin recording.  Captures current wire state as baseline."""
        self._recording = True
        self._baseline = {
            uuid: net.value
            for uuid, net in self._sim.data_network.networks.items()
        }
        self._prev = dict(self._baseline)
        if self._capture not in self._sim._on_tick_callbacks:
            self._sim._on_tick_callbacks.append(self._capture)

    def stop(self) -> None:
        """Stop recording.  Existing data is preserved."""
        self._recording = False
        try:
            self._sim._on_tick_callbacks.remove(self._capture)
        except ValueError:
            pass

    def clear(self) -> None:
        """Discard all recorded data."""
        self._deltas.clear()
        self._baseline.clear()
        self._prev.clear()

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def get_recording(self) -> list[WireSnapshot]:
        """Return all recorded delta snapshots in tick order."""
        return list(self._deltas)

    def query_recording(
        self, wire_prefix: str, ticks: range | None = None
    ) -> list[tuple[int, int]]:
        """Return ``[(tick, value)]`` for a wire across the recording."""
        target = self._resolve_uuid(wire_prefix)
        if target is None:
            return []

        results: list[tuple[int, int]] = []
        current_value = self._baseline.get(target, 0)
        for snap in self._deltas:
            if target in snap.wires:
                current_value = snap.wires[target]
            if ticks is None or snap.tick in ticks:
                results.append((snap.tick, current_value))
        return results

    def diff_recording_ticks(
        self, tick_a: int, tick_b: int
    ) -> dict[str, tuple[int, int]]:
        """Return ``{uuid: (val_a, val_b)}`` for wires changed between ticks."""
        idx_a = idx_b = None
        for i, snap in enumerate(self._deltas):
            if snap.tick == tick_a:
                idx_a = i
            if snap.tick == tick_b:
                idx_b = i
        if idx_a is None or idx_b is None:
            return {}
        state_a = self._state_at(idx_a)
        state_b = self._state_at(idx_b)
        return {
            uuid: (state_a.get(uuid, 0), state_b.get(uuid, 0))
            for uuid in set(state_a) | set(state_b)
            if state_a.get(uuid, 0) != state_b.get(uuid, 0)
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _capture(self, tick: int) -> None:
        if not self._recording:
            return
        current = {
            uuid: net.value
            for uuid, net in self._sim.data_network.networks.items()
        }
        delta = {
            uuid: val
            for uuid, val in current.items()
            if self._prev.get(uuid) != val
        }
        self._deltas.append(WireSnapshot(tick=tick, wires=delta))
        self._prev = current

    def _state_at(self, index: int) -> dict[str, int]:
        """Reconstruct full wire state at a given snapshot index."""
        state = dict(self._baseline)
        for i in range(index + 1):
            state.update(self._deltas[i].wires)
        return state

    def _resolve_uuid(self, prefix: str) -> str | None:
        """Find the full UUID matching *prefix* in baseline or deltas."""
        for uuid in self._baseline:
            if uuid.startswith(prefix):
                return uuid
        for snap in self._deltas:
            for uuid in snap.wires:
                if uuid.startswith(prefix):
                    return uuid
        return None
