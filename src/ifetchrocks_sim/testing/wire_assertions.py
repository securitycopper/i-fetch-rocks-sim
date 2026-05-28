"""FR-11: Wire Assertion Helpers — unittest mixin for wire state assertions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ifetchrocks_sim.simulator import Simulator


class WireAssertionMixin:
    """Mixin for ``unittest.TestCase`` with domain-specific wire assertions."""

    def assertWireValue(self, sim: Simulator, wire_prefix: str,
                        expected: int, msg: str = '') -> None:
        """Assert the current live value on the wire equals *expected*."""
        net = _resolve_network(sim, wire_prefix)
        actual = net.value
        detail = (f"Wire {wire_prefix}: expected {expected:#06x}, "
                  f"got {actual:#06x}")
        if msg:
            detail = f"{msg} — {detail}"
        assert actual == expected, detail  # noqa: S101 (test helper)

    def assertWireChangedTo(self, capture: dict, wire_uuid: str,
                            tick: int, expected: int, msg: str = '') -> None:
        """Assert that at *tick* the wire had value *expected*."""
        tick_data = capture.get(tick, {})
        values = tick_data.get(wire_uuid, [])
        if not values:
            tail = f" — {msg}" if msg else ""
            raise AssertionError(
                f"Wire {wire_uuid} has no captured value at tick {tick}{tail}")
        actual = values[-1]
        detail = (f"Wire {wire_uuid} at tick {tick}: expected {expected:#06x}, "
                  f"got {actual:#06x}")
        if msg:
            detail = f"{msg} — {detail}"
        assert actual == expected, detail  # noqa: S101

    def assertWireStable(self, capture: dict, wire_uuid: str,
                         expected: int, msg: str = '') -> None:
        """Assert all captured ticks for the wire have the same expected value."""
        for tick, tick_data in sorted(capture.items()):
            values = tick_data.get(wire_uuid, [])
            for v in values:
                if v != expected:
                    detail = (f"Wire {wire_uuid} unstable at tick {tick}: "
                              f"expected {expected:#06x}, got {v:#06x}")
                    if msg:
                        detail = f"{msg} — {detail}"
                    raise AssertionError(detail)

    def assertWireNeverActive(self, capture: dict, wire_uuid: str) -> None:
        """Assert wire was always 0 throughout capture."""
        for tick, tick_data in sorted(capture.items()):
            values = tick_data.get(wire_uuid, [])
            for v in values:
                if v != 0:
                    raise AssertionError(
                        f"Wire {wire_uuid} was active ({v:#06x}) at tick {tick}")


def _resolve_network(sim: 'Simulator', prefix: str):
    """Find the DataNetwork whose UUID starts with *prefix*."""
    for uuid, net in sim.data_network.networks.items():
        if uuid.startswith(prefix):
            return net
    raise KeyError(f"No wire matching prefix {prefix!r}")
