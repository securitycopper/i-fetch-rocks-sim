"""Tests for ifetchrocks_sim.ship_topology.

Loads the module directly via importlib to avoid the package ``__init__``
side-effects (which transitively import ``pyvis``).
"""
import importlib.util
import sys
from pathlib import Path

_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src" / "ifetchrocks_sim" / "ship_topology.py"
)
_spec = importlib.util.spec_from_file_location("ship_topology", _MODULE_PATH)
ship_topology = importlib.util.module_from_spec(_spec)
sys.modules["ship_topology"] = ship_topology
_spec.loader.exec_module(ship_topology)


def test_life_support_large_data_matches_known_port_keys():
    """LifeSupportRoom has 4 known large-data port keys in
    docs/room-port-map.md (2 In + 2 Out). The Unity inventory must match
    that count + direction split — this is the canary that confirms the
    bridge between save data and Unity geometry is sound.
    """
    ls = [
        s for s in ship_topology.SOCKETS
        if s.room == "LifeSupportRoom" and s.size == "Large" and s.domain == "Data"
    ]
    assert len(ls) == 4, f"expected 4 LS Large/Data sockets, got {len(ls)}"
    ins = [s for s in ls if s.direction == "In"]
    outs = [s for s in ls if s.direction == "Out"]
    assert len(ins) == 2, f"expected 2 In, got {len(ins)}"
    assert len(outs) == 2, f"expected 2 Out, got {len(outs)}"


def test_central_room_is_passthrough():
    """CentralRoom has no ``RoomLinkSockets`` — consistent with its role as
    the 16-passthrough room described in docs/ship-topology.md."""
    central = [s for s in ship_topology.SOCKETS if s.room == "CentralRoom"]
    assert central == [], "CentralRoom should have no RoomLinkSockets entries"


def test_room_uuid_map_has_seven_rooms():
    assert len(ship_topology.ROOM_UUID) == 7
    assert ship_topology.ROOM_UUID["CockpitRoom"] == "3de44b84"
    assert ship_topology.ROOM_UUID["LifeSupportRoom"] == "71bf00a3"
    assert ship_topology.ROOM_UUID["CentralRoom"] == "3cd1e5ba"


def test_adjacent_wall_pairings_are_short():
    """Pairings between physically adjacent rooms should be short cables
    (~0.5 m): PowerRoom ↔ UtilityRoom and LifeSupportRoom ↔ CockpitRoom."""
    pairs = ship_topology.compute_pairings()
    adjacent_pairs = {
        frozenset({"PowerRoom", "UtilityRoom"}),
        frozenset({"LifeSupportRoom", "CockpitRoom"}),
    }
    for a, b in pairs:
        if frozenset({a.room, b.room}) in adjacent_pairs:
            d = ship_topology._dist2(a.pos, b.pos) ** 0.5
            assert d < 1.0, (
                f"adjacent {a.room}/{a.name} → {b.room}/{b.name} "
                f"should be <1m, got {d:.2f}m"
            )


def test_wing_to_lifesupport_pairings_are_symmetric():
    """Port and Starboard wings are mirror-symmetric. The two LifeSupport
    Large/Data In sockets should pair one-each with the wings (not both
    with the same wing) — guards against greedy-NN order-dependence bugs.
    """
    pairs = ship_topology.compute_pairings()
    wing_data = [
        (a, b) for a, b in pairs
        if a.domain == "Data" and a.size == "Large"
        and (
            frozenset({a.room, b.room}) == frozenset({"PortWingRoom", "LifeSupportRoom"})
            or frozenset({a.room, b.room}) == frozenset({"StarboardWingRoom", "LifeSupportRoom"})
        )
    ]
    assert len(wing_data) == 2, f"expected 2 wing→LS Data pairs, got {len(wing_data)}"
    wing_rooms = {
        a.room if a.room != "LifeSupportRoom" else b.room
        for a, b in wing_data
    }
    assert wing_rooms == {"PortWingRoom", "StarboardWingRoom"}, (
        f"expected both wings represented, got {wing_rooms}"
    )


def test_pairings_are_deterministic():
    """compute_pairings() must be stable across calls."""
    a = ship_topology.compute_pairings()
    b = ship_topology.compute_pairings()
    assert a == b


def test_find_partner_returns_a_partner_for_paired_sockets():
    """Sockets that appear in PAIRINGS must return a non-None partner.
    NOTE: when a room has duplicate socket names (e.g. two ``LargeDataSocketOut``),
    find_partner_by_unity_name returns the partner of the *first* match —
    this is by design but worth being aware of when bridging to save data.
    """
    for a, b in ship_topology.PAIRINGS:
        assert ship_topology.find_partner_by_unity_name(a.room, a.name) is not None
        assert ship_topology.find_partner_by_unity_name(b.room, b.name) is not None


def test_no_pairing_exceeds_threshold():
    """All pairings should be within the default max_dist (5m). Anything
    longer is almost certainly spurious."""
    pairs = ship_topology.compute_pairings(max_dist=5.0)
    for a, b in pairs:
        d = ship_topology._dist2(a.pos, b.pos) ** 0.5
        assert d <= 5.0


def test_pairings_cover_all_ins():
    """We have 22 Outs and 16 Ins. The pairing should consume *all* Ins
    (since the lack is on the Out side, not the In side)."""
    pairs = ship_topology.compute_pairings()
    ins_in_pairs = {id(b) for a, b in pairs}
    all_ins = [s for s in ship_topology.SOCKETS if s.direction == "In"]
    assert len(ins_in_pairs) == len(all_ins), (
        f"expected all {len(all_ins)} Ins paired, got {len(ins_in_pairs)}"
    )
