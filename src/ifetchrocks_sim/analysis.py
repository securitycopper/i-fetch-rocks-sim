"""FR-13 / FR-14: Signal analysis — frequency stats and wire histograms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ifetchrocks_sim.simulator import Simulator
    from ifetchrocks_sim.recording import WireRecorder


@dataclass
class WireFrequencyStats:
    """Frequency / distribution statistics for one wire over a tick range."""
    wire_prefix: str
    label: str | None
    tick_range: tuple[int, int]     # (first_tick, last_tick) inclusive
    transition_count: int           # number of value changes
    value_distribution: dict[int, int]  # value -> tick_count
    min_value: int
    max_value: int
    mean_value: float
    is_binary: bool                 # True if only 0 and one non-zero value seen
    duty_cycle: float | None        # % ticks where value > 0 (only if is_binary)


# ------------------------------------------------------------------
# FR-13: Signal Frequency Analyzer
# ------------------------------------------------------------------

def analyze_wire_frequency(
    sim: Simulator,
    wire_prefix: str,
    ticks: range,
    label: str | None = None,
) -> WireFrequencyStats:
    """Tick the simulator over *ticks* and compute frequency stats for one wire.

    The simulator is advanced to each tick in *ticks* (must be ascending).
    """
    wire = _resolve_wire(sim, wire_prefix)
    if wire is None:
        raise KeyError(f"No wire matching prefix '{wire_prefix}'")

    net = sim.data_network.get_network(wire)
    prev_value: int | None = None
    transitions = 0
    dist: dict[int, int] = {}
    total = 0

    for t in ticks:
        sim.set_tick(t)
        val = net.value
        dist[val] = dist.get(val, 0) + 1
        total += 1
        if prev_value is not None and val != prev_value:
            transitions += 1
        prev_value = val

    return _build_stats(wire_prefix, label, ticks, dist, transitions, total)


def analyze_wire_frequency_from_recording(
    recorder: WireRecorder,
    wire_prefix: str,
    label: str | None = None,
) -> WireFrequencyStats:
    """Compute frequency stats from an existing WireRecorder recording."""
    pairs = recorder.query_recording(wire_prefix)
    if not pairs:
        raise KeyError(f"No data for wire prefix '{wire_prefix}' in recording")

    prev_value: int | None = None
    transitions = 0
    dist: dict[int, int] = {}

    for _tick, val in pairs:
        dist[val] = dist.get(val, 0) + 1
        if prev_value is not None and val != prev_value:
            transitions += 1
        prev_value = val

    tick_range = range(pairs[0][0], pairs[-1][0] + 1)
    return _build_stats(wire_prefix, label, tick_range, dist, transitions, len(pairs))


# ------------------------------------------------------------------
# FR-14: Wire Value Histogram
# ------------------------------------------------------------------

def print_wire_histogram(
    sim: Simulator,
    wire_prefix: str,
    ticks: range,
    buckets: int = 16,
    label: str | None = None,
    file=None,
) -> None:
    """Print a text histogram of wire values across *ticks*."""
    import sys
    out = file if file is not None else sys.stdout

    wire = _resolve_wire(sim, wire_prefix)
    if wire is None:
        print(f"Wire: {wire_prefix} — not found", file=out)
        return

    net = sim.data_network.get_network(wire)
    dist: dict[int, int] = {}
    total = 0
    for t in ticks:
        sim.set_tick(t)
        val = net.value
        dist[val] = dist.get(val, 0) + 1
        total += 1

    if total == 0:
        print(f"Wire: {wire_prefix} — no ticks", file=out)
        return

    display_label = label or wire_prefix
    print(f"Wire: {display_label} — ticks {ticks.start}-{ticks.stop - 1}", file=out)

    if len(dist) <= buckets:
        _print_exact_dist(dist, total, out)
    else:
        _print_bucketed_dist(dist, total, buckets, out)


def print_wire_histogram_from_recording(
    recorder: WireRecorder,
    wire_prefix: str,
    label: str | None = None,
    buckets: int = 16,
    file=None,
) -> None:
    """Print a text histogram from an existing WireRecorder recording."""
    import sys
    out = file if file is not None else sys.stdout

    pairs = recorder.query_recording(wire_prefix)
    if not pairs:
        print(f"Wire: {wire_prefix} — no data in recording", file=out)
        return

    dist: dict[int, int] = {}
    for _tick, val in pairs:
        dist[val] = dist.get(val, 0) + 1
    total = len(pairs)

    display_label = label or wire_prefix
    print(f"Wire: {display_label} — {total} ticks", file=out)

    if len(dist) <= buckets:
        _print_exact_dist(dist, total, out)
    else:
        _print_bucketed_dist(dist, total, buckets, out)


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _resolve_wire(sim: Simulator, prefix: str) -> str | None:
    for uuid in sim.data_network.networks:
        if uuid.startswith(prefix):
            return uuid
    return None


def _build_stats(
    wire_prefix: str,
    label: str | None,
    ticks: range,
    dist: dict[int, int],
    transitions: int,
    total: int,
) -> WireFrequencyStats:
    if not dist:
        return WireFrequencyStats(
            wire_prefix=wire_prefix, label=label,
            tick_range=(ticks.start, ticks.stop - 1),
            transition_count=0, value_distribution={},
            min_value=0, max_value=0, mean_value=0.0,
            is_binary=False, duty_cycle=None,
        )
    all_vals = sorted(dist.keys())
    min_val = all_vals[0]
    max_val = all_vals[-1]
    mean_val = sum(v * count for v, count in dist.items()) / total
    unique_nonzero = [v for v in all_vals if v != 0]
    is_binary = len(all_vals) <= 2 and (0 in dist)
    duty = None
    if is_binary and total > 0:
        duty = sum(count for v, count in dist.items() if v != 0) / total

    return WireFrequencyStats(
        wire_prefix=wire_prefix,
        label=label,
        tick_range=(ticks.start, ticks.stop - 1),
        transition_count=transitions,
        value_distribution=dict(dist),
        min_value=min_val,
        max_value=max_val,
        mean_value=mean_val,
        is_binary=is_binary,
        duty_cycle=duty,
    )


_BAR_CHAR = '\u2588'
_MAX_BAR_WIDTH = 40


def _print_exact_dist(dist: dict[int, int], total: int, out) -> None:
    max_count = max(dist.values())
    val_width = max(len(str(v)) for v in dist)
    for val in sorted(dist.keys()):
        count = dist[val]
        pct = count / total * 100
        bar_len = int(count / max_count * _MAX_BAR_WIDTH) if max_count else 0
        bar = _BAR_CHAR * bar_len
        print(f"  {val:>{val_width}} |{bar} {count} ({pct:.0f}%)", file=out)


def _print_bucketed_dist(dist: dict[int, int], total: int, buckets: int, out) -> None:
    min_val = min(dist.keys())
    max_val = max(dist.keys())
    span = max_val - min_val + 1
    bucket_size = max(1, span // buckets)

    bucket_counts: dict[int, int] = {}
    for val, count in dist.items():
        b = (val - min_val) // bucket_size
        bucket_counts[b] = bucket_counts.get(b, 0) + count

    max_count = max(bucket_counts.values()) if bucket_counts else 0
    for b in range(buckets):
        lo = min_val + b * bucket_size
        hi = lo + bucket_size - 1
        count = bucket_counts.get(b, 0)
        pct = count / total * 100
        bar_len = int(count / max_count * _MAX_BAR_WIDTH) if max_count else 0
        bar = _BAR_CHAR * bar_len
        print(f"  {lo:>5}-{hi:<5} |{bar} {count} ({pct:.0f}%)", file=out)
