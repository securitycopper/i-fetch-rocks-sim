import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import TextIO, List, Dict, Optional
import traceback
import json
from enum import Enum
#from typing import

from pyvis.network import Network

from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.controllers.dials.controller_dial import ControllerDial
from ifetchrocks_sim.devices.controllers.special.cargo_gun_controller import CargoGunController
from ifetchrocks_sim.devices.controllers.sliders.small_slider import SmallSlider
from ifetchrocks_sim.devices.controllers.sliders.wide_slider import WideSlider
from ifetchrocks_sim.devices.controllers.switches.four_bit_switch import FourBitSwitch
from ifetchrocks_sim.devices.controllers.switches.four_toggle_switch import FourToggleSwitch
from ifetchrocks_sim.devices.data_distribution.data_conduits.wide_conduit import WideConduit
from ifetchrocks_sim.devices.data_distribution.data_conduits.tall_conduit import TallConduit
from ifetchrocks_sim.devices.data_distribution.data_mergers.binary_merger import BinaryMerger
from ifetchrocks_sim.devices.data_distribution.data_splitters.binary_splitter import BinarySplitter
from ifetchrocks_sim.devices.data_distribution.data_splitters.channel_splitter import ChannelSplitter
from ifetchrocks_sim.devices.data_distribution.data_mergers.packet_vector_merger import PacketVectorMerger
from ifetchrocks_sim.devices.data_distribution.data_splitters.packet_vector_splitter import PacketVectorSplitter
from ifetchrocks_sim.devices.data_monitors.displays.oscilloscope import Oscilloscope
from ifetchrocks_sim.devices.data_processing.binary.Equality import Equality
from ifetchrocks_sim.devices.data_processing.binary.binary_mux import BinaryMux
from ifetchrocks_sim.devices.data_processing.binary.binary_shift import BinaryShift
from ifetchrocks_sim.devices.data_processing.generators.quantum_channel_a import QuantumChannelA
from ifetchrocks_sim.devices.data_processing.generators.quantum_channel_b import QuantumChannelB
from ifetchrocks_sim.devices.data_processing.generators.quantum_channel_c import QuantumChannelC
from ifetchrocks_sim.devices.data_processing.generators.quantum_channel_d import QuantumChannelD
from ifetchrocks_sim.devices.data_monitors.displays.boolean_light import BooleanLight
from ifetchrocks_sim.devices.data_monitors.displays.element_display import ElementDisplay
from ifetchrocks_sim.devices.data_processing.math.arithmetic.add import Add
from ifetchrocks_sim.devices.data_processing.math.arithmetic.minus import Minus
from ifetchrocks_sim.devices.data_processing.math.arithmetic.lerp import Lerp
from ifetchrocks_sim.devices.data_processing.math.arithmetic.percent_multiply import PercentMultiply
from ifetchrocks_sim.devices.data_processing.math.scoped.signal_inequalities import SignalInequalities
from ifetchrocks_sim.devices.data_processing.sensors.gas_sensor import GasSensor
from ifetchrocks_sim.devices.data_processing.math.arithmetic.divide import Divide
from ifetchrocks_sim.devices.data_processing.math.arithmetic.multiply import ArithmeticMultiply
from ifetchrocks_sim.devices.data_processing.binary.binary_or import BinaryOrGate
from ifetchrocks_sim.devices.data_processing.binary.binary_xor import BinaryXorGate
from ifetchrocks_sim.devices.data_processing.binary.binary_and import BinaryAndGate
from ifetchrocks_sim.devices.data_distribution.data_mergers.channel_merger import ChannelMerger
from ifetchrocks_sim.devices.data_processing.memory.large_loop_break import LargeLoopBreak
from ifetchrocks_sim.devices.data_processing.memory.small_loop_break import SmallLoopBreak
from ifetchrocks_sim.devices.large_network_node import LargeNetworkNode
from ifetchrocks_sim.devices.data_processing.logic.logical_nand_gate import LogicalNandGate
from ifetchrocks_sim.devices.data_processing.logic.logical_nor import LogicalNorGate
from ifetchrocks_sim.devices.data_processing.logic.logical_xor_gate import LogicalXorGate
from ifetchrocks_sim.devices.data_processing.logic.logical_xnor_gate import LogicalXnorGate
from ifetchrocks_sim.devices.data_processing.logic.logical_not import LogicalNotGate
from ifetchrocks_sim.devices.data_processing.logic.logical_or import LogicalOrGate
from ifetchrocks_sim.devices.data_processing.logic.logical_mux import LogicalMux
from ifetchrocks_sim.devices.network_node import NetworkNode
from ifetchrocks_sim.devices.network_power_node import NetworkPowerNode

from ifetchrocks_sim.devices.data_processing.memory.memory_bay_signal import MemoryBaySignal
from ifetchrocks_sim.devices.data_processing.memory.memory_bay_vector import MemoryBayVector
from ifetchrocks_sim.devices.data_processing.memory.drives.drive_cartridge import DriveCartridge
from ifetchrocks_sim.devices.data_processing.memory.register import Register
from ifetchrocks_sim.devices.data_distribution.data_splitters.single_channel_splitter import SingleChannelSplitter
from ifetchrocks_sim.devices.data_monitors.speakers.speaker import Speaker
from ifetchrocks_sim.devices.controllers.switches.switch_single import SwitchSingle
from ifetchrocks_sim.devices.power_distribution.power_splitters.large_power_splitter import LargePowerSplitter
from ifetchrocks_sim.devices.power_distribution.power_splitters.large_switched import LargeSwitched
from ifetchrocks_sim.devices.power_distribution.power_splitters.long_power_splitter import LongPowerSplitter
from ifetchrocks_sim.devices.power_distribution.power_splitters.small_switched_power import SmallSwitchedPower
from ifetchrocks_sim.devices.power_distribution.power_splitters.small_power_splitter import SmallPowerSplitter
from ifetchrocks_sim.devices.power_distribution.energy_cells.small_energy_cell import SmallEnergyCell
from ifetchrocks_sim.devices.data_distribution.data_splitters.multiplex_splitter import MultiplexSplitter
from ifetchrocks_sim.devices.data_distribution.data_splitters.flight_splitter import FlightSplitter
from ifetchrocks_sim.devices.data_distribution.data_conduits.large_conduit import LargeConduit
from ifetchrocks_sim.devices.data_distribution.data_conduits.large_conduit_stub import LargeConduitStub
from ifetchrocks_sim.devices.data_distribution.wireless.wireless_transmitter import WirelessTransmitter
from ifetchrocks_sim.devices.data_distribution.wireless.wireless_receiver import WirelessReceiver

from ifetchrocks_sim.devices.unknown_device import UnknownDevice
from ifetchrocks_sim.devices.data_monitors.displays.counter_display import CounterDisplay
from ifetchrocks_sim.devices.data_monitors.displays.value_display import ValueDisplay
from ifetchrocks_sim.devices.data_monitors.displays.binary_light_array import BinaryLightArray
from ifetchrocks_sim.devices.data_monitors.displays.linear_light_array import LinearLightArray

from ifetchrocks_sim.devices.controllers.buttons.button_single import ButtonSingle
from ifetchrocks_sim.devices.controllers.buttons.four_button_bank import FourButtonBank
from ifetchrocks_sim.devices.controllers.switches.eight_bit_switch import EightBitSwitch
from ifetchrocks_sim.devices.controllers.switches.one_bit_switch import OneBitSwitch
from ifetchrocks_sim.devices.controllers.joysticks.horizontal_axis_joystick import HorizontalAxisJoystick
from ifetchrocks_sim.devices.controllers.joysticks.vertical_axis_joystick import VerticalAxisJoystick
from ifetchrocks_sim.devices.controllers.joysticks.two_axis_joystick import TwoAxisJoystick
from ifetchrocks_sim.devices.controllers.joysticks.throttle import Throttle

from ifetchrocks_sim.devices.data_processing.logic.logical_and import LogicalAndGate

from ifetchrocks_sim.backtrace import (
    backtrace_wire as _backtrace_wire_fn,
    print_backtrace as _print_backtrace_fn,
    forwardtrace_wire as _forwardtrace_wire_fn,
    print_forwardtrace as _print_forwardtrace_fn,
    find_signal_path as _find_signal_path_fn,
)
from ifetchrocks_sim.labels import LabelRegistry, AmbiguousLabelError  # noqa: F401 – re-exported


max_int = 65535


@dataclass
class WireDiff:
    """A wire whose value changed between two snapshots (Phase 6)."""
    uuid:   str
    before: int
    after:  int
    label:  Optional[str] = None


@dataclass
class UnknownDeviceEntry:
    """Phase 7: Structured descriptor for one unknown device instance.

    Returned by ``Simulator.list_unknown_devices()`` and
    ``Simulator.inventory_unknown_devices()``.  Type-1 room frames are never
    included — use the plain ``found_devices`` dict for exhaustive iteration.
    """
    type_id: int
    uuid:    str
    room:    str


@dataclass
class RoomPortEntry:
    """Phase 7b: One room-boundary port enumerated from a type-1 room frame.

    Returned by ``Simulator.list_room_ports()`` and aggregated by
    ``Simulator.room_port_summary()``.

    Fields
    ------
    room_uuid  : UUID of the type-1 room frame device.
    room_name  : ComponentLocation enum name ('LIFE_SUPPORT', etc.) or numeric
                 string when the location is unknown.
    port_id    : indexedChildren key (as a string).
    wire_uuid  : UUID of the connected wire node, or None if not present.
    kind       : 'small_data' | 'large_data' | 'power' | 'large_power' | 'unknown'
                 Inferred from the child node's network type (5/4/3/2 respectively).
    direction  : 'in' | 'out' | 'unknown'
                 Drawn from hardcoded metadata for Life Support (UUID prefix
                 ``71bf00a3``); 'unknown' for all other rooms.
    """
    room_uuid:  str
    room_name:  str
    port_id:    str
    wire_uuid:  Optional[str]
    kind:       str
    direction:  str
    label:      Optional[str] = None


@dataclass
class RoomPortDiff:
    """Phase 7c: One room-boundary port that changed between two saves.

    Returned inside :class:`SaveDiff` by
    ``Simulator.diff_simulators()`` / ``Simulator.diff_saves()``.

    Fields
    ------
    room_uuid   : UUID of the type-1 room frame that owns the port.
    room_name   : ComponentLocation enum name for the room.
    port_id     : indexedChildren key (as a string).
    wire_before : Wire UUID in the *before* save, or None when the port is new.
    wire_after  : Wire UUID in the *after* save, or None when the port is removed.
    kind_before : Network kind in the *before* save, or None when port is new.
    kind_after  : Network kind in the *after* save, or None when port is removed.
    direction   : Direction from the before entry where available, or the after
                  entry when the port was added.
    change      : 'added' | 'removed' | 'rewired' | 'kind_changed'
    """
    room_uuid:   str
    room_name:   str
    port_id:     str
    wire_before: Optional[str]
    wire_after:  Optional[str]
    kind_before: Optional[str]
    kind_after:  Optional[str]
    direction:   str
    change:      str


@dataclass
class SaveDiff:
    """Phase 7c: Structured result of comparing two save files.

    Returned by ``Simulator.diff_simulators()`` and ``Simulator.diff_saves()``.

    Fields
    ------
    room_port_diffs      : List of :class:`RoomPortDiff` — one entry per changed
                           room-boundary port.  Ports that are identical in both
                           saves are omitted.
    unknown_device_deltas: ``{type_id: delta}`` for every UnknownDevice type
                           whose count changed.  Positive means more instances
                           in *after*, negative means fewer.  Type-1 room frames
                           are excluded (consistent with
                           :meth:`Simulator.list_unknown_devices`).
    device_count_deltas  : ``{class_name: delta}`` for every device class
                           whose total count across all rooms changed.  Keys are
                           Python class names (e.g. ``'Register'``,
                           ``'UnknownDevice'``).  Zero-delta classes are omitted.
    """
    room_port_diffs:       List['RoomPortDiff']
    unknown_device_deltas: Dict[int, int]
    device_count_deltas:   Dict[str, int]


# ---------------------------------------------------------------------------
# Phase 7b: room-port inventory constants
#
# _NET_TYPE_TO_KIND — maps indexed-child network type to a human-readable kind
# string.  Only the four well-known wired network types are listed; anything
# else resolves to 'unknown'.
#
# _ROOM_PORT_META — maps room-frame UUID prefix → dict(port_id → _PortMeta).
# Each _PortMeta carries direction ('in'/'out') and a human-readable label.
# See docs/room-port-map.md for full RE status and confirmation method.
# ---------------------------------------------------------------------------

_NET_TYPE_TO_KIND: Dict[int, str] = {
    5: 'small_data',
    4: 'large_data',
    3: 'power',
    2: 'large_power',
}


@dataclass(frozen=True)
class _PortMeta:
    """Direction and human-readable label for a room-boundary port."""
    direction: str   # 'in' | 'out'
    label: str       # e.g. 'Data OUT to Utility Room'


# ---- Life Support (UUID 71bf00a3, loc=4) ---------------------------------
# WARNING: Room.py names are INVERTED vs data-flow direction.
#   _out_ fields → data flows INTO room (room is consumer).
#   _in_  fields → data flows OUT of room (room is producer).
_LIFE_SUPPORT_PORTS: Dict[str, _PortMeta] = {
    '-325482860': _PortMeta('out', 'Large Data Instruction Bus IN'),
    '1207760765': _PortMeta('in',  'Large Data Decoded Commands OUT'),
    '65878718':   _PortMeta('in',  'Large Power IN'),
    '-633974235': _PortMeta('out', 'Large Power OUT Bottom Left'),
    '31010700':   _PortMeta('out', 'Data OUT'),
    '1186959326': _PortMeta('in',  'Room Light'),
}

# ---- Helm (UUID 3de44b84, loc=7) ----------------------------------------
_HELM_PORTS: Dict[str, _PortMeta] = {
    '60b2e319': _PortMeta('in',  'Helm Data IN'),
    'e935db8d': _PortMeta('out', 'Helm Data OUT'),
}

# ---- Engine Room sub-frames (loc=1) -------------------------------------
# Frame c33bced5 — main workspace (39 children)
_ENGINE_ROOM_WORKSPACE_PORTS: Dict[str, _PortMeta] = {
    '1899945012': _PortMeta('in', 'Generator Power Bus'),
}

# Frame 5ec0da90 — power distribution + large data inter-room links
# Confirmed 2026-04-05 via RE save cable-add diff.
_ENGINE_ROOM_POWER_DIST_PORTS: Dict[str, _PortMeta] = {
    # Large data
    '1369963593': _PortMeta('in',  'Data IN from Utility Room'),
    '61220091':   _PortMeta('out', 'Data OUT to Utility Room'),
    # Large power (paired with 73329139 generator sub-frame)
    '-698833991':  _PortMeta('out', 'Power OUT Upper Left'),
    '1167983942':  _PortMeta('out', 'Power OUT Lower Right'),
    '293351710':   _PortMeta('out', 'Power OUT Lower Left'),
    '586606824':   _PortMeta('out', 'Power OUT Upper Right'),
}

# Frame 73329139 — generator sub-frame
# All small data confirmed 2026-04-05 via RE save cable-add diff.
_ENGINE_ROOM_GENERATOR_PORTS: Dict[str, _PortMeta] = {
    # Large power (paired with 5ec0da90)
    '-1934607023': _PortMeta('in',  'Power IN Upper Left'),
    '-314435025':  _PortMeta('in',  'Power IN Upper Right'),
    '-193460702':  _PortMeta('in',  'Power IN Lower Left'),
    '-31443502':   _PortMeta('in',  'Power IN Lower Right'),
    '-545936232':  _PortMeta('in',  'Null Port (unknown)'),
    # Small data — axis inputs
    '2105108609':  _PortMeta('in',  'W Axis Input'),
    '1155016266':  _PortMeta('in',  'Z Axis Input'),
    '-992509362':  _PortMeta('in',  'Y Axis Input'),
    '364506720':   _PortMeta('in',  'X Axis Input'),
    # Small data — power & throughput
    '-2045856709': _PortMeta('in',  'Power Output Magnification'),
    '-1734810526': _PortMeta('in',  'Power Generation'),
    '-772166125':  _PortMeta('in',  'Power Throughput'),
    # Small data — instability inputs
    '-598877922':  _PortMeta('in',  'W Axis Instability'),
    '-514153587':  _PortMeta('in',  'Z Axis Instability'),
    '890699255':   _PortMeta('in',  'Y Axis Instability'),
    '1149364333':  _PortMeta('in',  'X Axis Instability'),
    # Small data — oscilloscope outputs
    '-1684163846': _PortMeta('out', 'W Axis Instability Oscilloscope'),
    '176442279':   _PortMeta('out', 'Z Axis Instability Oscilloscope'),
    '-1346510470': _PortMeta('out', 'Y Axis Instability Oscilloscope'),
    '-1647239958': _PortMeta('out', 'X Axis Instability Oscilloscope'),
}

# Frame 1ec5c991 — room-frame connections
_ENGINE_ROOM_LIGHT_PORTS: Dict[str, _PortMeta] = {
    '1935500529': _PortMeta('out', 'Room Light'),
}

# Frame 3a10ba9e — room-frame connections (door to Utility Room)
_ENGINE_ROOM_DOOR_PORTS: Dict[str, _PortMeta] = {
    '578436441': _PortMeta('out', 'Utility Room Door Power'),
    '89895364':  _PortMeta('out', 'Utility Room Door Override'),
}

# ---- Utility Room (UUID d002848a, loc=3) ---------------------------------
# Confirmed 2026-04-04 (RE save). See docs/room-port-map.md for full details.
_UTILITY_ROOM_PORTS: Dict[str, _PortMeta] = {
    # Large power — 4 paired IN connections from Engine Room
    # Each cable has two port keys (IN side + distribution side) within frame.
    '-793811655':  _PortMeta('in',  'Power IN Lower Left (side A)'),
    '-1292777819': _PortMeta('in',  'Power IN Lower Left (side B)'),
    '-214615217':  _PortMeta('in',  'Power IN Upper Right (side A)'),
    '-1592769918': _PortMeta('in',  'Power IN Upper Right (side B)'),
    '486403360':   _PortMeta('in',  'Power IN Upper Left (side A)'),
    '770972091':   _PortMeta('in',  'Power IN Upper Left (side B)'),
    '1933421465':  _PortMeta('in',  'Power IN Lower Right (side A)'),
    '13006070':    _PortMeta('in',  'Power IN Lower Right (side B)'),
    # Large power — solo cross-room endpoints
    '-1652577685': _PortMeta('out', 'Velocity Brakes Power'),
    '1820722088':  _PortMeta('out', 'Magnetosphere Generator Power'),
    '1975293713':  _PortMeta('out', 'Rotation Brakes Power'),
    # Small power
    '-18414241':   _PortMeta('out', 'Hub Door Power'),
    '-207153115':  _PortMeta('out', 'Room Light'),
    '-620460395':  _PortMeta('in',  'Engine Room Door Power'),
    # Large data — paired pass-through cables
    '-794641120':  _PortMeta('in',  'Data IN from Engine Room (Right Cable)'),
    '-500732375':  _PortMeta('out', 'Data OUT to Hub Room (Right Cable)'),
    '-506754480':  _PortMeta('in',  'Data IN from Hub Room (Left Cable)'),
    '-71024863':   _PortMeta('out', 'Data OUT to Engine Room (Left Cable)'),
    # Small data
    '-142578594':  _PortMeta('out', 'Magnetosphere Power Level'),
    '-2119560507': _PortMeta('out', 'Hub Door Override'),
    '-316840760':  _PortMeta('in',  'Magnetosphere Steady Readback'),
    '1124135457':  _PortMeta('out', 'Velocity Brakes Strength'),
    '1153892811':  _PortMeta('out', 'Engine Door Override'),
    '1289695271':  _PortMeta('out', 'Magnetosphere Level Select'),
    '811560911':   _PortMeta('out', 'Rotation Brakes Strength'),
    # Vector cable
    '-552520590':  _PortMeta('out', 'Magnetosphere Vector Config'),
}

# Maps room-frame UUID prefix → per-port metadata dict.
# Prefix length 8 matches the short-UUID convention used throughout the
# codebase (e.g. '71bf00a3').
_ROOM_PORT_META: Dict[str, Dict[str, _PortMeta]] = {
    # Life Support
    '71bf00a3': _LIFE_SUPPORT_PORTS,
    # Helm
    '3de44b84': _HELM_PORTS,
    # Engine Room sub-frames
    'c33bced5': _ENGINE_ROOM_WORKSPACE_PORTS,
    '5ec0da90': _ENGINE_ROOM_POWER_DIST_PORTS,
    '73329139': _ENGINE_ROOM_GENERATOR_PORTS,
    '1ec5c991': _ENGINE_ROOM_LIGHT_PORTS,
    '3a10ba9e': _ENGINE_ROOM_DOOR_PORTS,
    # Utility Room
    'd002848a': _UTILITY_ROOM_PORTS,
}

# Backward-compat alias: direction-only view for code that only needs 'in'/'out'.
_ROOM_PORT_DIRECTIONS: Dict[str, Dict[str, str]] = {
    prefix: {pid: pm.direction for pid, pm in ports.items()}
    for prefix, ports in _ROOM_PORT_META.items()
}


class ComponentType(Enum):
    POST_IT = 125  # Type 125, Payload is for post its
    MEMORY_BAY_SIGNAL = 141           # Raw memory bay, empty (no drive inserted)
    MEMORY_BAY_WITH_DRIVE_A = 153     # Raw memory bay with Drive A inserted (functional); was wrongly noted as BATTERY
    MEMORY_BAY_VECTOR_EMPTY = 143     # Vector memory bay, empty (no drive inserted); same port keys as type 154 (RE-confirmed 2026-03-26)
    MEMORY_BAY_VECTOR = 154           # Vector memory bay with any drive variant (RE-confirmed 2026-03-24)
    DRIVE_A = 139  # Double Check
    DRIVE_B = 156  # Double Check
    DRIVE_C = 157  # Program
    DRIVE_D = 158  # RE-confirmed 2026-03-24
    DRIVE_E = 159  # RE-confirmed 2026-03-24
    #BATTERY = 153
    # LIGHT = 1  # Theory
    DATA_NETWORK = 5

    OSCILLOSCOPE = 6

    BUTTON_SINGLE = 201
    FOUR_BUTTON_BANK = 47  # RE-confirmed 2026-03-24
    LOGICAL_AND = 25
    SWITCH_SINGLE = 202
    SINGLE_CHANNEL_SPLITTER = 14
    LOGICAL_OR = 24
    VALUE_DISPLAY = 71
    ELEMENT_DISPLAY = 72
    SMALL_SLIDER = 10
    WIDE_SLIDER = 16
    CARGO_GUN_CONTROLLER = 200

    CONTROLLER_DIAL = 78
    LOGICAL_MUX = 134
    FOUR_BIT_SWITCH = 42
    FOUR_TOGGLE_SWITCH = 126
    GAS_SENSOR = 44
    SWITCH_BANK_LONG = 40
    BIT_SWITCH_1 = 215
    HORIZONTAL_AXIS_JOYSTICK = 73
    VERTICAL_AXIS_JOYSTICK = 74
    TWO_AXIS_JOYSTICK = 9
    THROTTLE = 8
    LOGICAL_NOR = 26
    LOGICAL_NAND = 27  # RE-confirmed 2026-03-22; LogicalNandGate registered 2026-03-29
    LOGICAL_XNOR = 29

    BINARY_LIGHT_ARRAY = 122
    BINARY_MUX = 135
    SPEAKER = 37
    BINARY_OR = 119
    REGISTER = 128
    MULTIPLY = 111
    CHANNEL_MERGER = 67
    LARGE_DATA_NETWORK = 4
    WIDE_CONDUIT = 17
    TALL_CONDUIT = 18
    SMALL_POWER_SPLITTER = 23
    SMALL_ENERGY_CELL = 38
    LINEAR_LIGHT_ARRAY = 39
    LARGE_POWER_SPLITTER = 12
    POWER_NETWORK = 3
    LARGE_POWER_NETWORK = 2
    #7/1
    LONG_POWER_SPLITTER = 63
    QUANTUM_CHANNEL_A = 30
    QUANTUM_CHANNEL_B = 31
    QUANTUM_CHANNEL_C = 113
    QUANTUM_CHANNEL_D = 114
    BOOLEAN_LIGHT = 214
    LOGICAL_NOT = 133
    LOOP_BREAK = 130
    EQUALITY = 132
    BINARY_SHIFT = 123
    CHANNEL_SPLITTER = 62
    VECTOR_MULTIPLEX_MERGER   = 150
    VECTOR_MULTIPLEX_SPLITTER = 149
    LARGE_LOOP_BREAK = 131
    ADD = 22
    MINUS = 110
    LERP = 196
    PERCENT_MULTIPLY = 101
    SIGNAL_INEQUALITIES = 102
    DIVIDE = 112
    BINARY_SPLITTER = 116
    BINARY_MERGER = 115
    LARGE_SWITCHED = 127
    SMALL_SWITCHED = 34
    COUNTER_DISPLAY = 45
    MULTIPLEX_SPLITTER = 124
    FLIGHT_SPLITTER = 66
    LARGE_CONDUIT = 64
    LARGE_CONDUIT_STUB = 70
    WIRELESS_TRANSMITTER = 212
    WIRELESS_RECEIVER = 213
    BINARY_AND = 118  # RE-confirmed 2026-03-23
    BINARY_XOR = 120  # inferred from neighbor direction analysis 2026-03-29; same 3-port keys as AND/OR




class DeviceClasses(Enum):
    BUTTON_SINGLE = ButtonSingle  # Unit tests written
    FOUR_BUTTON_BANK = FourButtonBank  # type 47 - RE-confirmed 2026-03-24
    LOGICAL_AND = LogicalAndGate  # Unit tests written; circuit coverage via majority voter
    DATA_NETWORK = NetworkNode
    SWITCH_SINGLE = SwitchSingle  # Unit tests written
    LOGICAL_OR = LogicalOrGate  # Unit tests written; circuit coverage via majority voter
    SINGLE_CHANNEL_SPLITTER = SingleChannelSplitter  # unit tests written
    VALUE_DISPLAY = ValueDisplay  # unit tests written
    ELEMENT_DISPLAY = ElementDisplay  # type 72 - passthrough element display
    CONTROLLER_DIAL = ControllerDial  # unit tests written
    CARGO_GUN_CONTROLLER = CargoGunController  # port IDs confirmed from save 102d6094
    BINARY_LIGHT_ARRAY = BinaryLightArray  # circuit test written
    LINEAR_LIGHT_ARRAY = LinearLightArray  # passthrough linear light array (type 39)
    FOUR_BIT_SWITCH = FourBitSwitch  # unit tests written
    FOUR_TOGGLE_SWITCH = FourToggleSwitch  # type 126 - RE-confirmed 2026-03-24
    SWITCH_BANK_LONG = EightBitSwitch  # port IDs confirmed 2026-03-22
    BIT_SWITCH_1 = OneBitSwitch           # port IDs confirmed 2026-03-22
    HORIZONTAL_AXIS_JOYSTICK = HorizontalAxisJoystick  # port IDs confirmed 2026-03-22
    VERTICAL_AXIS_JOYSTICK = VerticalAxisJoystick      # port IDs confirmed 2026-03-22
    TWO_AXIS_JOYSTICK = TwoAxisJoystick                # port IDs confirmed 2026-03-22
    THROTTLE = Throttle                                # port IDs confirmed 2026-03-22
    LOGICAL_NAND = LogicalNandGate  # type 27; port IDs confirmed 2026-03-22
    LOGICAL_XOR = LogicalXorGate  # type 214; port IDs confirmed 2026-03-22
    LOGICAL_XNOR = LogicalXnorGate  # type 29; port IDs confirmed 2026-03-23
    LOGICAL_NOR = LogicalNorGate  # Unit tests written; circuit coverage via SR latch
    BINARY_MUX = BinaryMux  # port IDs RE-confirmed 2026-03-30 (TRUE=2034020425, SEL=563576145, FALSE=1173709222)
    BINARY_OR = BinaryOrGate  # unit tests written; circuit test written
    BINARY_AND = BinaryAndGate  # type 118 - RE-confirmed 2026-03-23
    BINARY_XOR = BinaryXorGate  # type 120 - inferred from neighbor direction analysis 2026-03-29
    SPEAKER = Speaker  # unit tests written
    REGISTER = Register  # unit tests written; circuit test written
    MULTIPLY = ArithmeticMultiply  # unit tests written; circuit test written
    CHANNEL_MERGER = ChannelMerger  # circuit test written
    LARGE_DATA_NETWORK = LargeNetworkNode  # wire node (no logic); no circuit test needed
    POWER_NETWORK = NetworkPowerNode  # wire node (no logic); no circuit test needed
    LARGE_POWER_NETWORK = NetworkPowerNode  # wire node (no logic); no circuit test needed
    QUANTUM_CHANNEL_A = QuantumChannelA  # seed-based in-game generator; skip (untestable offline)
    QUANTUM_CHANNEL_B = QuantumChannelB  # random per tick; skip deterministic tests
    QUANTUM_CHANNEL_C = QuantumChannelC  # random per tick; skip deterministic tests
    QUANTUM_CHANNEL_D = QuantumChannelD  # random per tick; skip deterministic tests
    BOOLEAN_LIGHT = BooleanLight  # display only; no output
    LOGICAL_NOT = LogicalNotGate  # circuit test written
    LOGICAL_MUX = LogicalMux  # port IDs confirmed from save 102d6094, 2026-03-23
    LOOP_BREAK = SmallLoopBreak  # circuit coverage via TestCircuitCounter
    EQUALITY = Equality  # circuit test written
    BINARY_SHIFT = BinaryShift  # Unit tests written; circuit test written
    CHANNEL_SPLITTER = ChannelSplitter  # circuit test written
    LARGE_LOOP_BREAK = LargeLoopBreak  # circuit test written
    ADD = Add  # Unit tests written
    MINUS = Minus  # Unit tests written
    LERP = Lerp  # Unit tests written
    PERCENT_MULTIPLY = PercentMultiply  # Unit tests written
    SIGNAL_INEQUALITIES = SignalInequalities  # port IDs confirmed 2026-03-22
    GAS_SENSOR = GasSensor  # port IDs confirmed 2026-03-23
    COUNTER_DISPLAY = CounterDisplay  # Unit tests written
    DIVIDE = Divide  # Unit tests written; circuit test written
    BINARY_SPLITTER = BinarySplitter  # circuit test written
    WIDE_CONDUIT = WideConduit  # circuit test written
    TALL_CONDUIT = TallConduit
    BINARY_MERGER = BinaryMerger  # circuit test written
    LONG_POWER_SPLITTER = LongPowerSplitter  # circuit test written
    SMALL_POWER_SPLITTER = SmallPowerSplitter  # circuit test written
    SMALL_ENERGY_CELL = SmallEnergyCell  # port IDs confirmed from save 102d6094
    LARGE_POWER_SPLITTER = LargePowerSplitter  # circuit test written
    SMALL_SLIDER = SmallSlider  # circuit test written
    WIDE_SLIDER = WideSlider  # port IDs confirmed from save 102d6094
    OSCILLOSCOPE = Oscilloscope  # circuit test written
    LARGE_SWITCHED = LargeSwitched  # Unit tests written; circuit-style regression written
    SMALL_SWITCHED = SmallSwitchedPower  # port IDs confirmed from save 102d6094
    MEMORY_BAY_SIGNAL = MemoryBaySignal           # empty bay shell (type 141); port IDs tentative
    MEMORY_BAY_WITH_DRIVE_A = MemoryBaySignal     # bay + Drive A (type 153); all port IDs confirmed
    MEMORY_BAY_VECTOR_EMPTY = MemoryBayVector     # empty vector bay (type 143); same port keys as 154 (RE-confirmed 2026-03-26)
    MEMORY_BAY_VECTOR = MemoryBayVector           # vector bay (type 154); port IDs confirmed 2026-03-24
    DRIVE_A = DriveCartridge                        # passive cartridge (type 139); I/O handled by parent bay
    DRIVE_B = DriveCartridge                        # passive cartridge (type 156); I/O handled by parent bay
    DRIVE_C = DriveCartridge                        # passive cartridge (type 157); I/O handled by parent bay
    DRIVE_D = DriveCartridge                        # passive cartridge (type 158); I/O handled by parent bay
    DRIVE_E = DriveCartridge                        # passive cartridge (type 159); I/O handled by parent bay
    MULTIPLEX_SPLITTER = MultiplexSplitter         # port IDs confirmed from save 102d6094
    FLIGHT_SPLITTER = FlightSplitter               # channel index mapping TODO: needs verification
    LARGE_CONDUIT = LargeConduit                   # port IDs confirmed from save 102d6094
    LARGE_CONDUIT_STUB = LargeConduitStub          # type 70 - no ports observed; stub
    WIRELESS_TRANSMITTER = WirelessTransmitter     # port IDs confirmed from save 102d6094
    WIRELESS_RECEIVER = WirelessReceiver           # TODO: port keys not yet confirmed


@dataclass
class DiscoveredBridge:
    source_room: str
    source_device: str     # UUID of source device
    source_wire: str       # wire UUID
    target_room: str
    target_device: str     # UUID of target device
    target_wire: str       # wire UUID
    kind: str              # 'large_data' | 'data' | 'power'
    auto_bridged: bool     # True if a forwarding listener was registered


# Declarative cross-room bridge mapping.  Each entry maps a source wire UUID
# prefix (output from one room) to a target wire UUID prefix (input in another).
# Add new entries here as cross-room cable pairing RE is confirmed.
_BRIDGE_MAP = [
    # ---- Life Support internal loop-back ----
    {
        'source_prefix': '0e935799',   # LS ChannelMerger 56816edd output
        'target_prefix': '60b2e319',   # LS ChannelSplitter 457a8e44 input
        'source_room':   'LIFE_SUPPORT',
        'target_room':   'LIFE_SUPPORT',
        'source_device': '56816edd',
        'target_device': '457a8e44',
        'kind':          'large_data',
        'label':         'LS internal command loop',
    },
    # ---- Engine Room → Utility Room (large data, right cable) ----
    # Confirmed 2026-04-05: ER frame 5ec0da90 port 61220091 OUT →
    # UR frame d002848a port -794641120 IN (cable 464f1309).
    {
        'source_prefix': 'dba83026',   # ER 5ec0da90 large data OUT wire
        'target_prefix': '464f1309',   # UR d002848a right cable (IN side)
        'source_room':   'ENGINROOM',
        'target_room':   'DAMPENERS_SHILDING',
        'source_device': '5ec0da90',
        'target_device': 'd002848a',
        'kind':          'large_data',
        'label':         'ER Data OUT → UR Right Cable IN',
    },
    # ---- Utility Room → Engine Room (large data, left cable) ----
    # Confirmed 2026-04-05: UR frame d002848a port -71024863 OUT →
    # ER frame 5ec0da90 port 1369963593 IN (wire 33e8ae10).
    {
        'source_prefix': 'c6d4f4a5',   # UR d002848a left cable (OUT side)
        'target_prefix': '33e8ae10',   # ER 5ec0da90 large data IN wire
        'source_room':   'DAMPENERS_SHILDING',
        'target_room':   'ENGINROOM',
        'source_device': 'd002848a',
        'target_device': '5ec0da90',
        'kind':          'large_data',
        'label':         'UR Left Cable OUT → ER Data IN',
    },
    # ---- Engine Room → Utility Room door power ----
    # ER frame 3a10ba9e port 578436441 OUT → UR frame d002848a port -620460395 IN.
    {
        'source_prefix': '8cd3d616',   # ER 3a10ba9e small power wire (UR Door)
        'target_prefix': 'c2f67a7c',   # UR d002848a Engine Room Door Power
        'source_room':   'ENGINROOM',
        'target_room':   'DAMPENERS_SHILDING',
        'source_device': '3a10ba9e',
        'target_device': 'd002848a',
        'kind':          'power',
        'label':         'ER → UR Door Power',
    },
    # ---- Engine Room → Utility Room door override ----
    # ER frame 3a10ba9e port 89895364 OUT → UR frame d002848a port 1153892811 OUT.
    # Note: UR port direction is 'out' (Engine Door Override is sent from UR side);
    # this bridge carries the ER override signal to the UR wire where it is read.
    {
        'source_prefix': 'c88c9352',   # ER 3a10ba9e small data wire (UR Door Override)
        'target_prefix': '6e3c3755',   # UR d002848a Engine Door Override
        'source_room':   'ENGINROOM',
        'target_room':   'DAMPENERS_SHILDING',
        'source_device': '3a10ba9e',
        'target_device': 'd002848a',
        'kind':          'small_data',
        'label':         'ER → UR Door Override',
    },
]


class ComponentLocation(Enum):
    LIFE_SUPPORT = 4
    DAMPENERS_SHILDING = 3
    ENGINROOM = 1
    CENTRAL_HUB = 2
    HELM = 7

class Simulator:

    def __init__(self):
        self.component_room = defaultdict(lambda: defaultdict(lambda: 0))

        self.components = list()

        self.remove_if_empty = ['payload', 'indexedDeviceData', 'storedPower']
        self.data_network = DataNetworkManager()
        self.found_devices = defaultdict(lambda: list())
        self.already_processed = list()
        self.node_filter = list()
        self.tick = 0
        self.capture = defaultdict(lambda: defaultdict(lambda: list()))
        self.set_data_uuid = str(uuid.uuid4())
        self.game_tick_listeners = list()
        self._label_registry = LabelRegistry()
        self._on_tick_callbacks = list()

    def set_tick(self, tick: int):
        self.tick = tick
        self.data_network.set_tick(tick=tick)
        for cb in self._on_tick_callbacks:
            cb(tick)

    def get_capture(self) -> Dict[int, Dict[str,List]]:
        return {tick: dict(values) for tick, values in self.capture.items()}

    def inject_data_into_node(self, u: str, value: int):
        self.data_network.get_network(u).update_source(self.set_data_uuid, value)

    def capture_uuid(self, u: str):
        network = self.data_network.get_network(u)

        def listener_func(u:str, value: int):
            # if self.tick:
            self.capture[self.tick][u].append(value)
        network.register_listener(listener_func)

    def set_node_filter(self, uuids: List[str]):
        self.node_filter = uuids

    def backtrace_wire(self, wire_prefix: str, max_depth: int = 20) -> 'TraceNode':
        """Return ancestor trace tree of the first wire matching wire_prefix."""
        return _backtrace_wire_fn(self, wire_prefix, max_depth,
                                  label_registry=self._label_registry)

    def print_backtrace(self, wire_prefix: str, max_depth: int = 20) -> None:
        """Print ancestor trace tree of the first wire matching wire_prefix."""
        _print_backtrace_fn(self, wire_prefix, max_depth, label_registry=self._label_registry)

    def forwardtrace_wire(self, wire_prefix: str, max_depth: int = 20) -> 'TraceNode':
        """Return downstream consumer trace tree of the first wire matching wire_prefix."""
        return _forwardtrace_wire_fn(self, wire_prefix, max_depth,
                                     label_registry=self._label_registry)

    def print_forwardtrace(self, wire_prefix: str, max_depth: int = 20) -> None:
        """Print downstream consumer trace tree of the first wire matching wire_prefix."""
        _print_forwardtrace_fn(self, wire_prefix, max_depth, label_registry=self._label_registry)

    def find_signal_path(
        self,
        source_prefix: str,
        target_prefix: str,
        max_depth: int = 50,
    ):
        """BFS path between two wire prefixes; returns list of (kind, uuid, label) hops or None."""
        return _find_signal_path_fn(self, source_prefix, target_prefix, max_depth,
                                    label_registry=self._label_registry)

    # ------------------------------------------------------------------
    # Label registry public API
    # ------------------------------------------------------------------

    def set_wire_label(self, uuid_prefix: str, label: str) -> None:
        """Attach a human-readable *label* to *uuid_prefix* (wire)."""
        self._label_registry.set(uuid_prefix, label)

    def set_device_label(self, uuid_prefix: str, label: str) -> None:
        """Attach a human-readable *label* to *uuid_prefix* (device)."""
        self._label_registry.set(uuid_prefix, label)

    def get_label(self, uuid_prefix_or_uuid: str):
        """Return the label for *uuid_prefix_or_uuid*, or None.

        Raises AmbiguousLabelError when the supplied prefix matches multiple
        stored entries that resolve to different label strings.
        """
        return self._label_registry.get(uuid_prefix_or_uuid)

    def save_labels(self, path: str) -> None:
        """Persist the label registry to a JSON file at *path*."""
        self._label_registry.save(path)

    def load_labels(self, path: str) -> None:
        """Load labels from a JSON file, merging into the current registry."""
        self._label_registry.load(path)

    # ------------------------------------------------------------------
    # Phase 6: Wire diff
    # ------------------------------------------------------------------

    def snapshot_wire_values(self) -> Dict[str, int]:
        """Return a copy of every tracked wire UUID mapped to its current value.

        Call this before and after a stimulus, then pass both results to
        ``diff_wires`` to see which wires changed.
        """
        return {uid: net.value for uid, net in self.data_network.networks.items()}

    def diff_wires(
        self,
        before: Dict[str, int],
        after: Dict[str, int],
    ) -> List[WireDiff]:
        """Return list of :class:`WireDiff` for every wire whose value changed.

        Wires present in *before* but absent in *after* are reported with
        ``after=0``.  Wires absent in *before* but present in *after* are
        reported with ``before=0``.  The result is sorted by UUID for
        deterministic output.

        Labels from the Simulator's label registry are attached when available.
        """
        result: List[WireDiff] = []
        for uid in sorted(set(before) | set(after)):
            v_before = before.get(uid, 0)
            v_after = after.get(uid, 0)
            if v_before != v_after:
                label = self._label_registry.get(uid)
                result.append(WireDiff(uuid=uid, before=v_before, after=v_after, label=label))
        return result

    # ------------------------------------------------------------------
    # Wire patching — post-load circuit modification
    # ------------------------------------------------------------------

    def find_network(self, wire_prefix: str) -> 'DataNetwork':
        """Return the DataNetwork whose UUID starts with *wire_prefix*.

        Raises KeyError if no match is found, ValueError if multiple matches.
        """
        matches = [(uid, net) for uid, net in self.data_network.networks.items()
                    if uid.startswith(wire_prefix)]
        if not matches:
            raise KeyError(f'No wire matching prefix {wire_prefix!r}')
        if len(matches) > 1:
            raise ValueError(
                f'Ambiguous prefix {wire_prefix!r}: '
                f'{[m[0][:12] for m in matches]}')
        return matches[0][1]

    def patch_wire(self, wire_prefix: str, value: int) -> str:
        """Force a wire to a constant value. Returns the full wire UUID."""
        net = self.find_network(wire_prefix)
        net.set_override(value)
        return net.uuid

    def unpatch_wire(self, wire_prefix: str) -> str:
        """Remove a wire override, restore source-driven behaviour. Returns UUID."""
        net = self.find_network(wire_prefix)
        net.clear_override()
        return net.uuid

    # ------------------------------------------------------------------
    # Phase 7: Unknown-device inventory
    # ------------------------------------------------------------------

    def list_unknown_devices(self) -> List[UnknownDeviceEntry]:
        """Return a flat list of all UnknownDevice instances, excluding type-1 room frames.

        Each entry carries ``type_id``, ``uuid``, and ``room`` (the
        :class:`ComponentLocation` enum name, or the raw integer as a string
        when the location is not in the enum).

        Type-1 entries are room-frame containers, not functional devices, and
        are always excluded.  Use ``inventory_unknown_devices()`` for a
        type-grouped view.
        """
        result: List[UnknownDeviceEntry] = []
        for room, devices in self.found_devices.items():
            for device in devices:
                if isinstance(device, UnknownDevice):
                    type_id = device.data.get('type', 0)
                    if type_id == 1:
                        continue
                    result.append(UnknownDeviceEntry(
                        type_id=type_id,
                        uuid=device.uuid,
                        room=str(room),
                    ))
        return result

    def inventory_unknown_devices(self) -> Dict[int, List[UnknownDeviceEntry]]:
        """Group unknown devices by type_id, excluding type-1 room frames.

        Returns a plain ``dict`` mapping ``type_id -> List[UnknownDeviceEntry]``.
        An empty dict is returned when no unknown devices are present.
        """
        grouped: Dict[int, List[UnknownDeviceEntry]] = {}
        for entry in self.list_unknown_devices():
            if entry.type_id not in grouped:
                grouped[entry.type_id] = []
            grouped[entry.type_id].append(entry)
        return grouped

    # ------------------------------------------------------------------
    # Phase 7b: Room-port inventory
    # ------------------------------------------------------------------

    def list_room_ports(
        self,
        room_uuid: Optional[str] = None,
    ) -> List[RoomPortEntry]:
        """Enumerate room-boundary ports from all type-1 room frames.

        Parameters
        ----------
        room_uuid:
            Optional UUID or prefix to filter results to a single room frame.
            Matching uses ``str.startswith``, so the 8-character short prefix
            (e.g. ``'71bf00a3'``) or the full UUID both work.  When *None*
            (default) all room frames are enumerated.

        Returns
        -------
        A fresh list of :class:`RoomPortEntry`, one per indexed-child port.
        Kind is inferred from the child node's network type (4/5/2/3 →
        large_data / small_data / large_power / power).  Direction comes from
        hardcoded metadata for Life Support (UUID prefix ``71bf00a3``);
        all other rooms report ``'unknown'`` direction.  Rooms with an empty
        ``indexedChildren`` contribute nothing to the result.
        """
        result: List[RoomPortEntry] = []
        for room_name, devices in self.found_devices.items():
            for device in devices:
                if not isinstance(device, UnknownDevice):
                    continue
                if device.data.get('type', 0) != 1:
                    continue
                frame_uuid: str = device.uuid
                if room_uuid is not None and not frame_uuid.startswith(room_uuid):
                    continue
                # Resolve port metadata for this specific room frame.
                port_meta: Dict[str, _PortMeta] = {}
                for prefix, meta in _ROOM_PORT_META.items():
                    if frame_uuid.startswith(prefix):
                        port_meta = meta
                        break
                for port_id, child in device.data.get('indexedChildren', {}).items():
                    if child is None:
                        continue
                    child_type = child.get('type')
                    wire_uuid = child.get('uuid')
                    kind = _NET_TYPE_TO_KIND.get(child_type, 'unknown')
                    pm = port_meta.get(str(port_id))
                    direction = pm.direction if pm else 'unknown'
                    label = pm.label if pm else None
                    result.append(RoomPortEntry(
                        room_uuid=frame_uuid,
                        room_name=str(room_name),
                        port_id=str(port_id),
                        wire_uuid=wire_uuid,
                        kind=kind,
                        direction=direction,
                        label=label,
                    ))
        return result

    def room_port_summary(self) -> Dict[str, List[RoomPortEntry]]:
        """Aggregate room-boundary ports grouped by room name.

        Calls :meth:`list_room_ports` and groups results by
        ``entry.room_name``.  Returns a plain ``dict``; an empty dict is
        returned when no room frames have ports.
        """
        summary: Dict[str, List[RoomPortEntry]] = {}
        for entry in self.list_room_ports():
            if entry.room_name not in summary:
                summary[entry.room_name] = []
            summary[entry.room_name].append(entry)
        return summary

    # ------------------------------------------------------------------
    # Phase 7c: Cross-save connectivity diff
    # ------------------------------------------------------------------

    @staticmethod
    def diff_simulators(
        sim_before: 'Simulator',
        sim_after:  'Simulator',
        room_filters: Optional[List[str]] = None,
    ) -> 'SaveDiff':
        """Compare two already-loaded Simulator instances and return a :class:`SaveDiff`.

        Parameters
        ----------
        sim_before:
            Simulator loaded from the *before* save.
        sim_after:
            Simulator loaded from the *after* save.
        room_filters:
            Optional list of room_name strings (e.g. ``['LIFE_SUPPORT']``).
            When given, only ports and device-count deltas from those rooms are
            included.  ``None`` (default) includes all rooms.

        Returns a :class:`SaveDiff` with three fields:

        * ``room_port_diffs`` — per-port changes (added / removed / rewired /
          kind_changed).  Unchanged ports are omitted.
        * ``unknown_device_deltas`` — ``{type_id: delta}`` for unknown-device
          counts that changed.  Type-1 room frames follow the same exclusion
          rule as :meth:`list_unknown_devices`.
        * ``device_count_deltas`` — ``{class_name: delta}`` for any device
          class whose instance count changed across the filtered rooms.
        """
        _filters: Optional[set] = set(room_filters) if room_filters else None

        def _room_ok(room_name: str) -> bool:
            return _filters is None or room_name in _filters

        # --- Room-port diff ---
        def _index_ports(sim: 'Simulator') -> Dict[tuple, 'RoomPortEntry']:
            result: Dict[tuple, 'RoomPortEntry'] = {}
            for entry in sim.list_room_ports():
                if not _room_ok(entry.room_name):
                    continue
                result[(entry.room_uuid, entry.port_id)] = entry
            return result

        before_ports = _index_ports(sim_before)
        after_ports  = _index_ports(sim_after)

        room_port_diffs: List[RoomPortDiff] = []
        for key in sorted(set(before_ports) | set(after_ports)):
            b = before_ports.get(key)
            a = after_ports.get(key)
            if b is None:
                # Port exists only in after → added
                room_port_diffs.append(RoomPortDiff(
                    room_uuid=a.room_uuid, room_name=a.room_name, port_id=a.port_id,
                    wire_before=None, wire_after=a.wire_uuid,
                    kind_before=None, kind_after=a.kind,
                    direction=a.direction, change='added',
                ))
            elif a is None:
                # Port exists only in before → removed
                room_port_diffs.append(RoomPortDiff(
                    room_uuid=b.room_uuid, room_name=b.room_name, port_id=b.port_id,
                    wire_before=b.wire_uuid, wire_after=None,
                    kind_before=b.kind, kind_after=None,
                    direction=b.direction, change='removed',
                ))
            else:
                # Port present in both — check for wire or kind change
                if b.wire_uuid != a.wire_uuid:
                    room_port_diffs.append(RoomPortDiff(
                        room_uuid=b.room_uuid, room_name=b.room_name, port_id=b.port_id,
                        wire_before=b.wire_uuid, wire_after=a.wire_uuid,
                        kind_before=b.kind, kind_after=a.kind,
                        direction=b.direction, change='rewired',
                    ))
                elif b.kind != a.kind:
                    room_port_diffs.append(RoomPortDiff(
                        room_uuid=b.room_uuid, room_name=b.room_name, port_id=b.port_id,
                        wire_before=b.wire_uuid, wire_after=a.wire_uuid,
                        kind_before=b.kind, kind_after=a.kind,
                        direction=b.direction, change='kind_changed',
                    ))
                # else: no change — omit from results

        # --- Unknown-device deltas ---
        def _unknown_by_type(sim: 'Simulator') -> Dict[int, int]:
            grouped: Dict[int, int] = {}
            for entry in sim.list_unknown_devices():
                if not _room_ok(entry.room):
                    continue
                grouped[entry.type_id] = grouped.get(entry.type_id, 0) + 1
            return grouped

        counts_unk_before = _unknown_by_type(sim_before)
        counts_unk_after  = _unknown_by_type(sim_after)
        unknown_device_deltas: Dict[int, int] = {}
        for type_id in set(counts_unk_before) | set(counts_unk_after):
            delta = counts_unk_after.get(type_id, 0) - counts_unk_before.get(type_id, 0)
            if delta != 0:
                unknown_device_deltas[type_id] = delta

        # --- Device-count deltas (by Python class name, filtered by room) ---
        def _device_counts(sim: 'Simulator') -> Dict[str, int]:
            counts: Dict[str, int] = {}
            for room_name, devices in sim.found_devices.items():
                if not _room_ok(str(room_name)):
                    continue
                for device in devices:
                    name = type(device).__name__
                    counts[name] = counts.get(name, 0) + 1
            return counts

        dev_before = _device_counts(sim_before)
        dev_after  = _device_counts(sim_after)
        device_count_deltas: Dict[str, int] = {}
        for name in set(dev_before) | set(dev_after):
            delta = dev_after.get(name, 0) - dev_before.get(name, 0)
            if delta != 0:
                device_count_deltas[name] = delta

        return SaveDiff(
            room_port_diffs=room_port_diffs,
            unknown_device_deltas=unknown_device_deltas,
            device_count_deltas=device_count_deltas,
        )

    @staticmethod
    def diff_saves(
        path_before: str,
        path_after:  str,
        room_filters: Optional[List[str]] = None,
    ) -> 'SaveDiff':
        """Load two save files by path and return a :class:`SaveDiff`.

        Each path is opened read-only; the calling Simulator's state is not
        modified.  Delegates to :meth:`diff_simulators` after loading.

        Parameters
        ----------
        path_before:
            Filesystem path to the *before* save JSON file.
        path_after:
            Filesystem path to the *after* save JSON file.
        room_filters:
            Forwarded to :meth:`diff_simulators`; see that method for details.
        """
        sim_before = Simulator()
        with open(path_before, encoding='utf-8') as fh:
            sim_before.load_from_file(fh)
        sim_after = Simulator()
        with open(path_after, encoding='utf-8') as fh:
            sim_after.load_from_file(fh)
        return Simulator.diff_simulators(sim_before, sim_after, room_filters=room_filters)

    def remove_orphened_networks(self):
        reduced = dict()
        for room,  room_device_list in self.found_devices.items():
            reduced[room] = list(filter(self._filter_ignore_orphaned_nodes, room_device_list))
        self.found_devices = reduced

    def _filter_ignore_orphaned_nodes(self, device) -> bool:
        if type(device) is NetworkNode:
            if hasattr(device, 'do_not_prune') and device.do_not_prune:
                return True
            if self.data_network.does_network_exists(device.uuid):
                network = self.data_network.get_network(device.uuid)
                # -1 because Network_node listens to it's own network
                if len(network.sources) + len(network.listener_functions) - 1 > 0:
                    return True
                else:
                    return False
        else:
            return True
        return False

    def load_from_list(self, data: List[Dict]):
        for d in data:
            if d['type'] not in [5]:
                self._process_component(d)
        self._generate_missing_connections()
        self._bridge_corridor_cables()
        self._correct_stale_counter_flags()

    def load_from_file(self, file: TextIO):
        raw = file.readline()
        ship = json.loads(raw)['ship']

        for component in [*ship['rooms'], *ship['floating']]:
            self._process_component(component)
        self._generate_missing_connections()
        self._bridge_corridor_cables()
        self._correct_stale_counter_flags()

    def _correct_stale_counter_flags(self):
        """Correct stale COUNT_ANY flags loaded from save data.

        The save file may have ``count_any=True`` for CounterDisplay devices —
        a stale artefact from when the save was created with turbo mode enabled.
        The game currently runs COUNT_TRUE (counter increments only on 0→non-zero
        rising edge).  This method sets ``_count_any = False`` on all loaded
        CounterDisplay instances so the simulator matches the game's actual
        operating mode.
        """
        for devs in self.found_devices.values():
            for d in devs:
                if isinstance(d, CounterDisplay):
                    d._count_any = False

    def _find_large_net_by_prefix(self, prefix: str):
        """Return the first LargeDataNetwork whose UUID starts with *prefix*, or None."""
        for uuid, net in self.data_network.large_networks.items():
            if uuid.startswith(prefix):
                return net
        return None

    def _find_net_by_prefix(self, prefix: str):
        """Return the first DataNetwork (small data) whose UUID starts with *prefix*, or None."""
        for uuid, net in self.data_network.networks.items():
            if uuid.startswith(prefix):
                return net
        return None

    def _find_power_net_by_prefix(self, prefix: str):
        """Return the first power DataNetwork whose UUID starts with *prefix*, or None."""
        for uuid, net in self.data_network.power_networks.items():
            if uuid.startswith(prefix):
                return net
        return None

    def _find_any_net_by_kind(self, prefix: str, kind: str):
        """Find a network by UUID prefix, selecting the registry based on *kind*."""
        if kind == 'large_data':
            return self._find_large_net_by_prefix(prefix)
        elif kind == 'small_data':
            return self._find_net_by_prefix(prefix)
        elif kind in ('power', 'large_power'):
            return self._find_power_net_by_prefix(prefix)
        return None

    def _bridge_corridor_cables(self):
        """Connect room-boundary corridor cables using the declarative _BRIDGE_MAP.

        Physical cables that run through corridors between rooms are not stored
        in device indexedChildren and therefore have no source in the simulator.
        This method registers forwarding listeners for every entry in _BRIDGE_MAP.
        Supports large_data, small_data, power, and large_power bridge kinds.
        """
        self._active_bridges: list[DiscoveredBridge] = []
        for entry in _BRIDGE_MAP:
            kind = entry['kind']
            src_net = self._find_any_net_by_kind(entry['source_prefix'], kind)
            tgt_net = self._find_any_net_by_kind(entry['target_prefix'], kind)
            bridged = False
            if src_net is not None and tgt_net is not None:
                bridge_id = f"corridor_bridge_{entry['source_prefix']}"
                def _make_forward(tgt, bid):
                    def _forward(uuid, value):
                        tgt.update_source(bid, value)
                    return _forward
                src_net.register_listener(_make_forward(tgt_net, bridge_id))
                bridged = True
            self._active_bridges.append(DiscoveredBridge(
                source_room=entry['source_room'],
                source_device=entry['source_device'],
                source_wire=entry['source_prefix'],
                target_room=entry['target_room'],
                target_device=entry['target_device'],
                target_wire=entry['target_prefix'],
                kind=kind,
                auto_bridged=bridged,
            ))

    def discover_corridor_bridges(self) -> list[DiscoveredBridge]:
        """Return the list of corridor bridges (active and inactive)."""
        return list(getattr(self, '_active_bridges', []))

    def print_corridor_bridges(self, file=None) -> None:
        """Print a formatted corridor bridge report."""
        import sys
        out = file if file is not None else sys.stdout
        bridges = self.discover_corridor_bridges()
        print(f"Corridor Bridges: {len(bridges)} configured", file=out)
        for b in bridges:
            status = "ACTIVE" if b.auto_bridged else "INACTIVE"
            print(f"  [{status}] {b.source_room} {b.source_wire[:8]} → "
                  f"{b.target_room} {b.target_wire[:8]}  ({b.kind})", file=out)


    def extract_data(self) -> List[Dict]:
        to_return = list()
        for room, devices in self.found_devices.items():
            #if len(room_filters) == 0 or room in room_filters:
            for device in devices:
                to_return.append(device.data)

        return to_return


    def debug_print_components_by_type(self):
        for n in range(0, 300):
            for component in self.components:
                if component['type'] == n:
                    pass
                    # print(component)

    def print_component_counts(self, room_filters: List[str]):
        for room_id, frequency in self.component_room.items():
            if len(room_filters) == 0 or room_id in room_filters:
                print(f'__ Room {room_id} __')
                for type, count in sorted(frequency.items(), key=lambda item: item[1]):
                    print(f'  Type: {type}, Count: {count}')

    def _add_node(self, g: Network, device):
        label = device.name
        title = device.uuid
        if hasattr(device, 'title'):
            title = device.title()
        if hasattr(device, 'label'):
            label = device.label()
        else:
            if hasattr(device, 'value'):
                value = device.value
                if hasattr(device, 'to_string'):
                    value = device.to_string()
                label = f'{label} ({value})'
        size = 10
        if hasattr(device, 'size'):
            size = device.size
        if hasattr(device, 'image'):
            g.add_node(n_id=device.uuid, title=title, label=label, shape='image', image=device.image, size=size)
        else:
            g.add_node(n_id=device.uuid, title=title, label=label, color=device.color, size=size)

    def _generate_nodes_if_missing(self, node_uuids: List, uuids: List[str], location):
        if isinstance(location, str):
            location = ComponentLocation[location].value
        for u in uuids:
            if u not in node_uuids:
                node_uuids.append(u)
                self._process_component(
                    {'type': ComponentType.DATA_NETWORK.value,
                     'location': location,
                     'uuid': u,
                     'color': 'grey',
                     'indexedChildren': dict()})

    def _generate_large_nodes_if_missing(self, node_uuids: List, uuids: List[str], location):
        if isinstance(location, str):
            location = ComponentLocation[location].value
        for u in uuids:
            if u not in node_uuids:
                node_uuids.append(u)
                self._process_component(
                    {'type': ComponentType.LARGE_DATA_NETWORK.value,
                     'location': location,
                     'uuid': u,
                     'color': 'grey',
                     'indexedChildren': dict()})

    def _generate_power_nodes_if_missing(self, node_uuids: List, uuids: List[str], location):
        if isinstance(location, str):
            location = ComponentLocation[location].value
        for u in uuids:
            if u not in node_uuids:
                node_uuids.append(u)
                self._process_component(
                    {'type': ComponentType.POWER_NETWORK.value,
                     'location': location,
                     'uuid': u,
                     'color': 'Red',
                     'indexedChildren': dict()})

    def _generate_large_power_nodes_if_missing(self, node_uuids: List, uuids: List[str], location):
        if isinstance(location, str):
            location = ComponentLocation[location].value
        for u in uuids:
            if u not in node_uuids:
                node_uuids.append(u)
                self._process_component(
                    {'type': ComponentType.LARGE_POWER_NETWORK.value,
                     'location': location,
                     'uuid': u,
                     'color': 'Red',
                     'indexedChildren': dict()})


    def _generate_missing_connections(self):
        ids_in_graph = list()
        for room, devices in self.found_devices.items():
            for device in devices:
                ids_in_graph.append(device.uuid)

        for room, devices in self.found_devices.items():
            for device in devices:
                for i, source in enumerate(device.input_networks):
                    self._generate_nodes_if_missing(node_uuids=ids_in_graph, uuids=[source,device.uuid], location=room)
                for i, dest in enumerate(device.output_networks):
                    self._generate_nodes_if_missing(node_uuids=ids_in_graph, uuids=[device.uuid, dest], location=room)

                if hasattr(device, 'large_input_networks'):
                    for i, source in enumerate(device.large_input_networks):
                        self._generate_large_nodes_if_missing(node_uuids=ids_in_graph, uuids=[source, device.uuid],
                                                        location=room)
                if hasattr(device, 'large_output_networks'):
                    for i, dest in enumerate(device.large_output_networks):
                        self._generate_large_nodes_if_missing(node_uuids=ids_in_graph, uuids=[device.uuid, dest], location=room)

                if hasattr(device, 'vector_input_networks'):
                    for i, source in enumerate(device.vector_input_networks):
                        self._generate_large_nodes_if_missing(node_uuids=ids_in_graph, uuids=[source, device.uuid], location=room)
                if hasattr(device, 'vector_output_networks'):
                    for i, dest in enumerate(device.vector_output_networks):
                        self._generate_large_nodes_if_missing(node_uuids=ids_in_graph, uuids=[device.uuid, dest], location=room)

                if hasattr(device, 'input_power_networks'):
                    for i, source in enumerate(device.input_power_networks):
                        self._generate_power_nodes_if_missing(node_uuids=ids_in_graph, uuids=[source, device.uuid],
                                                        location=room)
                if hasattr(device, 'output_power_networks'):
                    for i, dest in enumerate(device.output_power_networks):
                        self._generate_power_nodes_if_missing(node_uuids=ids_in_graph, uuids=[device.uuid, dest], location=room)

                if hasattr(device, 'large_input_power_networks'):
                    for i, source in enumerate(device.large_input_power_networks):
                        self._generate_large_power_nodes_if_missing(node_uuids=ids_in_graph, uuids=[source, device.uuid],
                                                        location=room)
                if hasattr(device, 'large_output_power_networks'):
                    for i, dest in enumerate(device.large_output_power_networks):
                        self._generate_large_power_nodes_if_missing(node_uuids=ids_in_graph, uuids=[device.uuid, dest], location=room)




    def build_graph_json(self, room_filters: List[str], show_power_wires: bool = True) -> dict:
        """Return the circuit graph as a plain dict with ``nodes`` and ``edges`` lists.

        This is an agent-readable alternative to ``build_graph_network`` / n2x.html.
        Write to disk with ``json.dump(sim.build_graph_json([]), open('graph.json','w'), indent=2)``.

        Node fields: uuid, label, type_name, location, value
        Edge fields: source, target, kind (data | large_data | power | large_power), label

        UnknownDevice edge inference: on a first pass, collect every wire that a known
        (non-UnknownDevice) device drives as an output.  When emitting edges for an
        UnknownDevice, any wire already driven by a known device is treated as an INPUT
        to the unknown device; any wire not driven by any known device is inferred to be
        an OUTPUT of the unknown device and the edge direction is flipped accordingly.
        """
        nodes: list = []
        edges: list = []
        seen_nodes: set = set()

        def _node(device, room):
            if device.uuid in seen_nodes:
                return
            seen_nodes.add(device.uuid)
            type_name = getattr(device, 'name', type(device).__name__)
            label = type_name
            if hasattr(device, 'label'):
                label = device.label()
            elif hasattr(device, 'value'):
                v = device.value
                if hasattr(device, 'to_string'):
                    v = device.to_string()
                label = f'{type_name} ({v})'
            value = getattr(device, 'value', None)
            nodes.append({
                'uuid': device.uuid,
                'label': label,
                'type_name': type_name,
                'location': str(room),
                'value': value,
            })

        def _edge(src, dst, kind, label):
            edges.append({'source': src, 'target': dst, 'kind': kind, 'label': str(label)})

        # First pass: collect every wire driven as an output by a known device so that
        # UnknownDevice connections can be inferred in the second pass.
        known_driven_wires: set = set()
        for room, devices in self.found_devices.items():
            if len(room_filters) == 0 or room in room_filters:
                for device in devices:
                    if isinstance(device, UnknownDevice):
                        continue
                    for wire in device.output_networks:
                        known_driven_wires.add(wire)
                    if hasattr(device, 'large_output_networks'):
                        for wire in device.large_output_networks:
                            known_driven_wires.add(wire)
                    if hasattr(device, 'vector_output_networks'):
                        for wire in device.vector_output_networks:
                            known_driven_wires.add(wire)
                    if show_power_wires:
                        if hasattr(device, 'output_power_networks'):
                            for wire in device.output_power_networks:
                                known_driven_wires.add(wire)
                        if hasattr(device, 'large_output_power_networks'):
                            for wire in device.large_output_power_networks:
                                known_driven_wires.add(wire)

        for room, devices in self.found_devices.items():
            if len(room_filters) == 0 or room in room_filters:
                for device in devices:
                    _node(device, room)
                    if isinstance(device, UnknownDevice):
                        # Infer edge directions: wire driven by a known device → input;
                        # wire not driven by any known device → inferred output.
                        for i, wire in enumerate(device.input_networks):
                            if wire in known_driven_wires:
                                _edge(wire, device.uuid, 'data', f'in{i}(inferred)')
                            else:
                                _edge(device.uuid, wire, 'data', f'out{i}(inferred)')
                        continue
                    for i, source in enumerate(device.input_networks):
                        lbl = device.input_networks_labels[i] if hasattr(device, 'input_networks_labels') else i
                        _edge(source, device.uuid, 'data', lbl)
                    for i, dest in enumerate(device.output_networks):
                        lbl = device.output_networks_labels[i] if hasattr(device, 'output_networks_labels') else i
                        _edge(device.uuid, dest, 'data', lbl)
                    if hasattr(device, 'large_input_networks'):
                        for i, source in enumerate(device.large_input_networks):
                            lbl = device.large_input_networks_labels[i] if hasattr(device, 'large_input_networks_labels') else i
                            _edge(source, device.uuid, 'large_data', lbl)
                    if hasattr(device, 'large_output_networks'):
                        for i, dest in enumerate(device.large_output_networks):
                            _edge(device.uuid, dest, 'large_data', i)
                    if hasattr(device, 'vector_input_networks'):
                        for i, source in enumerate(device.vector_input_networks):
                            _edge(source, device.uuid, 'vector', i)
                    if hasattr(device, 'vector_output_networks'):
                        for i, dest in enumerate(device.vector_output_networks):
                            _edge(device.uuid, dest, 'vector', i)
                    if show_power_wires:
                        if hasattr(device, 'input_power_networks'):
                            for i, dest in enumerate(device.input_power_networks):
                                _edge(device.uuid, dest, 'power', i)
                        if hasattr(device, 'output_power_networks'):
                            for i, dest in enumerate(device.output_power_networks):
                                _edge(device.uuid, dest, 'power', i)
                        if hasattr(device, 'large_input_power_networks'):
                            for i, dest in enumerate(device.large_input_power_networks):
                                _edge(source, device.uuid, 'large_power', i)
                        if hasattr(device, 'large_output_power_networks'):
                            for i, dest in enumerate(device.large_output_power_networks):
                                _edge(device.uuid, dest, 'large_power', i)

        return {'nodes': nodes, 'edges': edges}

    def build_graph_network(self, room_filters: List[str], show_power_wires: bool = True) -> Network:
        g = Network(notebook=False, height='1200px')
        ids_in_graph = list()
        for room, devices in self.found_devices.items():
            if len(room_filters) == 0 or room in room_filters:
                for device in devices:
                    self._add_node(g, device)
                    ids_in_graph.append(device.uuid)

        for room, devices in self.found_devices.items():
            if len(room_filters) == 0 or room in room_filters:
                for device in devices:
                    for i, source in enumerate(device.input_networks):
                        try:
                            if hasattr(device, 'input_networks_labels'):
                                i = device.input_networks_labels[i]
                            g.add_edge(source=source, to=device.uuid, arrowStrikethrough=False, color='Green', title=i)

                        except Exception:
                            print(f'Device: {device}')
                            print(traceback.format_exc())
                    for i, dest in enumerate(device.output_networks):
                        try:
                            if hasattr(device, 'output_networks_labels'):
                                i = device.output_networks_labels[i]
                            g.add_edge(source=device.uuid, to=dest, arrowStrikethrough=False, color='Purple', title=i)
                        except Exception:
                            print(f'Device: {device}')
                            print(traceback.format_exc())
                    if hasattr(device, 'large_input_networks'):
                        for i, source in enumerate(device.large_input_networks):
                            try:
                                if hasattr(device, 'large_input_networks_labels'):
                                    i = device.large_input_networks_labels[i]
                                g.add_edge(source=source, to=device.uuid, arrowStrikethrough=False, color='Green', title=i, value=10)

                            except Exception:
                                print(f'Device: {device}')
                                print(traceback.format_exc())
                    if hasattr(device, 'large_output_networks'):
                        for i, dest in enumerate(device.large_output_networks):
                            try:
                                g.add_edge(source=device.uuid, to=dest, arrowStrikethrough=False, color='Purple', title=i, value=10)
                            except Exception:
                                print(f'Device: {device}')
                                print(traceback.format_exc())
                    if hasattr(device, 'vector_input_networks'):
                        for i, source in enumerate(device.vector_input_networks):
                            try:
                                g.add_edge(source=source, to=device.uuid, arrowStrikethrough=False, color='#add8e6', title=i, value=10)
                            except Exception:
                                print(f'Device: {device}')
                                print(traceback.format_exc())
                    if hasattr(device, 'vector_output_networks'):
                        for i, dest in enumerate(device.vector_output_networks):
                            try:
                                g.add_edge(source=device.uuid, to=dest, arrowStrikethrough=False, color='#00008b', title=i, value=10)
                            except Exception:
                                print(f'Device: {device}')
                                print(traceback.format_exc())
                    if show_power_wires:
                        if hasattr(device, 'input_power_networks'):
                            for i, dest in enumerate(device.input_power_networks):
                                try:
                                    g.add_edge(source=device.uuid, to=dest, arrowStrikethrough=False, color='Red', title=i, value=1)
                                except Exception:
                                    print(f'Device: {device}')
                                    print(traceback.format_exc())

                        if hasattr(device, 'output_power_networks'):
                            for i, dest in enumerate(device.output_power_networks):
                                try:
                                    g.add_edge(source=device.uuid, to=dest, arrowStrikethrough=False, color='Purple', title=i, value=1)
                                except Exception:
                                    print(f'Device: {device}')
                                    print(traceback.format_exc())

                        if hasattr(device, 'large_input_power_networks'):
                            for i, dest in enumerate(device.large_input_power_networks):
                                try:
                                    g.add_edge(source=device.uuid, to=dest, arrowStrikethrough=False, color='Red', title=i, value=10)
                                except Exception:
                                    print(f'Device: {device}')
                                    print(traceback.format_exc())

                        if hasattr(device, 'large_output_power_networks'):
                            for i, dest in enumerate(device.large_output_power_networks):
                                try:
                                    g.add_edge(source=device.uuid, to=dest, arrowStrikethrough=False, color='#a8327d', title=i, value=10)
                                except Exception:
                                    print(f'Device: {device}')
                                    print(traceback.format_exc())

        return g



    def _process_component(self, component: dict):
        if component['uuid'] in self.already_processed:
            return
        else:
            self.already_processed.append(component['uuid'])
        #component.pop('position', {})
        ##component.pop('rotation', {})
        #component.pop('integrity')
        self._add_component_to_room(component)
        for indexedChildren in [component['indexedChildren']]:
            if indexedChildren:
                for k, v in indexedChildren.items():
                    if v:
                        self._process_component(v)
        #component.pop('indexedChildren', {})
        #for r in self.remove_if_empty:
        #    if not component[r]:
        #        component.pop(r, {})

        self.components.append(component)

    def _add_component_to_room(self, component: Dict):
        type_id = component['type']
        _type = str(type_id)
        _room = component['location']
        uuid = component['uuid']
        try:
            # Apply Room Label to output
            _room = ComponentLocation(component['location']).name
            component['room'] = _room
        except Exception:
            pass
        try:
            _type = 'unknown'
            try:
                _type = ComponentType(type_id).name
            except Exception:
                pass
            component['dType'] = _type
            device_class = None
            if _type == 'unknown':  #  and (wire_count +large_wire_count) > 0:
                device_class = UnknownDevice
            if device_class is None:
                try:
                    device_class = DeviceClasses[_type].value
                except Exception:
                    return
                    #device_class = UnknownDevice

            found = False
            if len(self.node_filter) > 0:
                if type_id in [ComponentType.DATA_NETWORK.value,
                               ComponentType.POWER_NETWORK.value]:  # node reduced later
                    found = True
                else:
                    for filter_uuid in self.node_filter:
                        if filter_uuid in uuid:
                            found = True
            else:
                found = True

            def fill_in_missing_wires(device):
                """
                Concept here is that if there is an issue with a device missing wires, it will show up as an input data or power wire

                :param device:
                :return:
                """
                # component_data = device.data
                # output_networks: List[str] = []
                # if hasattr(device, 'output_networks'):
                #     output_networks = device.output_networks
                # device.input_networks =  [item for item in get_connections_uuids_of_type(component_data, 5) if item not in output_networks]
                #
                # input_power_networks: List[str] = []
                # if hasattr(device, 'input_power_networks'):
                #     input_power_networks = device.input_power_networks
                # device.input_power_networks = [item for item in get_connections_uuids_of_type(component_data, 3) if item not in input_power_networks]
                #
                #
                # large_output_networks: List[str] = []
                # if hasattr(device, 'large_output_networks'):
                #     large_output_networks = device.large_output_networks
                # device.large_input_networks = [item for item in get_connections_uuids_of_type(component_data, 4) if item not in large_output_networks]
                #
                # large_input_power_networks: List[str] = []
                # if hasattr(device, 'large_input_power_networks'):
                #     large_input_power_networks = device.large_input_power_networks
                # device.large_input_power_networks = [item for item in get_connections_uuids_of_type(component_data, 2) if item not in large_input_power_networks]

                return device

            try:
                if found:
                    self.found_devices[_room].append(fill_in_missing_wires(device_class(self.data_network, component)))
            except Exception:
                self.found_devices[_room].append(UnknownDevice(self.data_network, component))
                print(f'Device in error: {component}')
                print(traceback.format_exc())
        except Exception:
            print(f'Device in error: {component}')
            print(traceback.format_exc())

        component_fequency = self.component_room[_room]
        count = component_fequency[_type]
        component_fequency[_type] = count + 1

