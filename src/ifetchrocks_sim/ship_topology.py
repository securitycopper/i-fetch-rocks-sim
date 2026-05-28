"""
ifetchrocks_sim.ship_topology
==============================

Inter-room cable topology derived from the ripped Unity Ship geometry.

Background
----------
Save files do not serialise the cable that physically joins two rooms — see
``docs/room-port-map.md``: every wall socket has a UUID local to its own
room, and the in-game cable mesh that bridges two rooms is not encoded in
the JSON. The result: cross-room large-cable wires appear DANGLING when
analysed from a save alone.

However, the topology is recoverable from the level geometry itself. In the
ripped Unity Ship hierarchy
(``Ship/ShipGraphics/ShipInterior/Rooms/<RoomName>/RoomLinkSockets/*``)
every cross-room socket exists as a GameObject whose **name encodes
size/domain/direction** (e.g. ``LargeDataSocketIN``, ``LargePowerSocketOut``)
and whose world position pins it to a specific spot on a specific wall.

This module bakes that data in and pairs the sockets spatially: for each
``Out`` socket the partner is the nearest ``In`` socket of the same size +
domain on a *different* room (cables physically meet at the wall, so
proximity is sufficient).

The Unity-side direction tag follows the same convention noted in
``docs/room-port-map.md`` ("Room.py names are inverted vs data flow"). The
spatial pairing itself is independent of that convention — pairings hold
either way.

Bridging to save port keys
--------------------------
This module gives you Unity-socket-to-Unity-socket pairs. To resolve a
*save* port key to its partner port key:

1. For the source room (UUID), look up the room name via :data:`ROOM_UUID`.
2. Per (size, domain, direction), the save and the Unity inventory should
   have matching counts; assign one-to-one by an agreed ordering
   (e.g. world position sorted on ``(z, x)``).
3. Look up the Unity partner via :func:`find_partner_by_unity_name`.
4. The partner socket's room name maps back to a save UUID, and the same
   ordering gives the partner's save port key.

For Life Support (``71bf00a3``) the counts match its four known large-data
keys (2 In + 2 Out) — see ``tests/test_ship_topology.py``.

Caveats
-------
- ``CentralRoom`` has **no** ``RoomLinkSockets``. It is the "16 passthrough"
  room described in ``docs/ship-topology.md`` and is intentionally absent
  from the data below.
- ``PowerRoom`` maps to one of the two engine-area UUIDs (``73329139`` or
  ``c33bced5``); verify against your save before relying on the mapping.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Unity room name → save room UUID (short form), derived by matching the
# front-to-back ordering observed in the ripped Ship hierarchy with the
# ordering documented in ``docs/ship-topology.md``.
# ---------------------------------------------------------------------------
ROOM_UUID: Dict[str, str] = {
    "CockpitRoom":       "3de44b84",  # Helm (frontmost)
    "LifeSupportRoom":   "71bf00a3",  # Life Support, hosts the CPU project
    "PortWingRoom":      "bad538b2",  # Left Thruster
    "CentralRoom":       "3cd1e5ba",  # Central — 16 passthrough cables
    "StarboardWingRoom": "f0343e44",  # Right Thruster
    "UtilityRoom":       "d002848a",  # Dampeners
    "PowerRoom":         "73329139",  # Engine area (or c33bced5; verify per save)
}


@dataclass(frozen=True)
class Socket:
    """A wall socket on a room boundary, extracted from the Unity hierarchy."""
    room: str                                # Unity room name (key in ROOM_UUID)
    name: str                                # Unity GameObject name (incl. dup suffixes)
    size: str                                # "Large" or "Small"
    domain: str                              # "Power" or "Data"
    direction: str                           # "In" or "Out" (per Unity name)
    pos: Tuple[float, float, float]          # world position (x, y, z)
    simple: bool = False                     # name had "Simple" suffix


# ---------------------------------------------------------------------------
# Cross-room sockets under each room's ``RoomLinkSockets``.
# Extracted from ``Ship/ShipGraphics/ShipInterior/Rooms/<room>/RoomLinkSockets/*``
# in the original IFR Unity level. Positions are world space; small numerical
# noise (~1e-3) is preserved from the source.
# ---------------------------------------------------------------------------
SOCKETS: List[Socket] = [
    # PowerRoom (engine, z=-5.08): 4 LargePower In + 2 LargeData Out.
    Socket("PowerRoom", "LargePowerSocketIN",        "Large", "Power", "In",  ( 0.570, 0.643, -4.019)),
    Socket("PowerRoom", "LargePowerSocketIN",        "Large", "Power", "In",  (-0.570, 0.643, -4.019)),
    Socket("PowerRoom", "LargePowerSocketIN (1)",    "Large", "Power", "In",  ( 0.434, 0.459, -4.019)),
    Socket("PowerRoom", "LargePowerSocketIN (2)",    "Large", "Power", "In",  (-0.434, 0.460, -4.019)),
    Socket("PowerRoom", "LargeDataSocketOut",        "Large", "Data",  "Out", ( 0.434, 1.785, -4.007)),
    Socket("PowerRoom", "LargeDataSocketOut (1)",    "Large", "Data",  "Out", (-0.433, 1.783, -4.007)),

    # UtilityRoom (dampeners, z=-2.58): symmetric — 4 LargePower In/Out, 2 LargeData In/Out.
    Socket("UtilityRoom", "LargePowerSocketIN",      "Large", "Power", "In",  ( 0.570, 0.643, -1.410)),
    Socket("UtilityRoom", "LargePowerSocketIN",      "Large", "Power", "In",  (-0.570, 0.643, -1.410)),
    Socket("UtilityRoom", "LargePowerSocketIN (1)",  "Large", "Power", "In",  ( 0.433, 0.460, -1.410)),
    Socket("UtilityRoom", "LargePowerSocketIN (2)",  "Large", "Power", "In",  (-0.435, 0.460, -1.410)),
    Socket("UtilityRoom", "LargePowerSocketOut",     "Large", "Power", "Out", ( 0.570, 0.643, -3.538)),
    Socket("UtilityRoom", "LargePowerSocketOut",     "Large", "Power", "Out", (-0.570, 0.643, -3.539)),
    Socket("UtilityRoom", "LargePowerSocketOut (1)", "Large", "Power", "Out", (-0.433, 0.458, -3.539)),
    Socket("UtilityRoom", "LargePowerSocketOut (2)", "Large", "Power", "Out", ( 0.435, 0.459, -3.538)),
    Socket("UtilityRoom", "LargeDataSocketOut",      "Large", "Data",  "Out", ( 0.434, 1.784, -1.396)),
    Socket("UtilityRoom", "LargeDataSocketOut (1)",  "Large", "Data",  "Out", (-0.433, 1.782, -1.397)),
    Socket("UtilityRoom", "LargeDataSocketIN",       "Large", "Data",  "In",  ( 0.434, 1.785, -3.529)),
    Socket("UtilityRoom", "LargeDataSocketIN (1)",   "Large", "Data",  "In",  (-0.433, 1.784, -3.529)),

    # StarboardWingRoom (right thruster, x=+2.51): only Out sockets; faces inward to Central.
    Socket("StarboardWingRoom", "LargePowerSocketOut", "Large", "Power", "Out", (1.551, 0.643,  0.480)),
    Socket("StarboardWingRoom", "LargePowerSocketOut", "Large", "Power", "Out", (1.552, 0.643, -0.660)),
    Socket("StarboardWingRoom", "LargeDataSocketOut",  "Large", "Data",  "Out", (1.550, 1.781,  0.344)),
    Socket("StarboardWingRoom", "LargeDataSocketOut",  "Large", "Data",  "Out", (1.550, 1.784, -0.522)),

    # PortWingRoom (left thruster, x=-2.72): mirror of starboard.
    Socket("PortWingRoom", "LargePowerSocketOut",      "Large", "Power", "Out", (-1.537, 0.643, -0.660)),
    Socket("PortWingRoom", "LargePowerSocketOut",      "Large", "Power", "Out", (-1.537, 0.643,  0.480)),
    Socket("PortWingRoom", "LargeDataSocketOut (1)",   "Large", "Data",  "Out", (-1.527, 1.784, -0.525)),
    Socket("PortWingRoom", "LargeDataSocketOut",       "Large", "Data",  "Out", (-1.527, 1.785,  0.344)),

    # LifeSupportRoom (CPU room, z=+2.49): 2 LargePower In + 2 LargePower Out,
    # 2 LargeData In + 2 LargeData Out — matches the 4 known large-data port
    # keys in docs/room-port-map.md.
    Socket("LifeSupportRoom", "LargePowerSocketOut",   "Large", "Power", "Out", ( 0.570, 0.643, 1.532)),
    Socket("LifeSupportRoom", "LargePowerSocketOut",   "Large", "Power", "Out", (-0.570, 0.643, 1.531)),
    Socket("LifeSupportRoom", "LargePowerSocketIN",    "Large", "Power", "In",  ( 0.570, 0.643, 3.660)),
    Socket("LifeSupportRoom", "LargePowerSocketIN",    "Large", "Power", "In",  (-0.570, 0.643, 3.660)),
    Socket("LifeSupportRoom", "LargeDataSocketOut",    "Large", "Data",  "Out", ( 0.434, 1.789, 3.674)),
    Socket("LifeSupportRoom", "LargeDataSocketOut",    "Large", "Data",  "Out", (-0.433, 1.787, 3.673)),
    Socket("LifeSupportRoom", "LargeDataSocketIN",     "Large", "Data",  "In",  ( 0.434, 1.787, 1.529)),
    Socket("LifeSupportRoom", "LargeDataSocketIN",     "Large", "Data",  "In",  (-0.433, 1.786, 1.541)),

    # CockpitRoom (Helm, frontmost, z=+5.14): 2 LargePower Out + 2 LargeData In.
    Socket("CockpitRoom", "LargePowerSocketOut",       "Large", "Power", "Out", ( 0.570, 0.643, 4.182)),
    Socket("CockpitRoom", "LargePowerSocketOut",       "Large", "Power", "Out", (-0.570, 0.643, 4.181)),
    Socket("CockpitRoom", "LargeDataSocketIN",         "Large", "Data",  "In",  ( 0.434, 1.785, 4.190)),
    Socket("CockpitRoom", "LargeDataSocketIN",         "Large", "Data",  "In",  (-0.436, 1.785, 4.190)),
]


def _dist2(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def compute_pairings(max_dist: float = 5.0) -> List[Tuple[Socket, Socket]]:
    """Pair every ``Out`` socket with an ``In`` socket of the same size +
    domain on a *different* room, by globally-sorted distance: enumerate all
    valid candidate pairs, sort by distance ascending, then claim each pair
    if both endpoints are still unused. This yields stable, symmetric
    nearest-neighbour matching (no order-dependence on the source list).

    Returns a list of ``(out_socket, in_socket)`` tuples.
    """
    outs = [s for s in SOCKETS if s.direction == "Out"]
    ins = [s for s in SOCKETS if s.direction == "In"]
    max_d2 = max_dist ** 2

    candidates: List[Tuple[float, int, int]] = []
    for oi, out in enumerate(outs):
        for ii, inn in enumerate(ins):
            if out.room == inn.room:
                continue
            if out.size != inn.size or out.domain != inn.domain:
                continue
            d2 = _dist2(out.pos, inn.pos)
            if d2 <= max_d2:
                candidates.append((d2, oi, ii))
    # Sort by distance, then by indices for determinism on ties.
    candidates.sort()
    used_out: set = set()
    used_in: set = set()
    pairs: List[Tuple[Socket, Socket]] = []
    for d2, oi, ii in candidates:
        if oi in used_out or ii in used_in:
            continue
        used_out.add(oi)
        used_in.add(ii)
        pairs.append((outs[oi], ins[ii]))
    return pairs


# Cached pairings (computed once at import).
PAIRINGS: List[Tuple[Socket, Socket]] = compute_pairings()


def find_partner_by_unity_name(room: str, name: str) -> Optional[Socket]:
    """Look up the cross-room partner for the Unity socket ``room/name``.

    Returns ``None`` if the socket is unknown or has no partner.
    """
    target = next((s for s in SOCKETS if s.room == room and s.name == name), None)
    if target is None:
        return None
    for a, b in PAIRINGS:
        if a is target:
            return b
        if b is target:
            return a
    return None


def room_uuid_for(room_name: str) -> Optional[str]:
    """Return the save UUID for a Unity room name (or ``None`` if unknown)."""
    return ROOM_UUID.get(room_name)


def _summary() -> str:
    lines = [
        f"Ship topology — {len(SOCKETS)} cross-room sockets across {len(set(s.room for s in SOCKETS))} rooms.",
        f"Computed pairings: {len(PAIRINGS)} (CentralRoom is passthrough — no RoomLinkSockets).",
        "",
        "Pairings (Out → In):",
    ]
    for a, b in PAIRINGS:
        d = _dist2(a.pos, b.pos) ** 0.5
        lines.append(
            f"  {a.room:18s} {a.name:34s} → {b.room:18s} {b.name:34s}  "
            f"[{a.size}/{a.domain}]  d={d:.2f}m"
        )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(_summary())
