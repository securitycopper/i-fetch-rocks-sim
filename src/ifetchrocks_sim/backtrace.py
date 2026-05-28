"""
Wire ancestor backtrace diagnostic.

Usage::

    from ifetchrocks_sim.backtrace import backtrace_wire, print_backtrace
    root = backtrace_wire(sim, '03dfbb16')
    print_backtrace(sim, '03dfbb16')

Or via the Simulator convenience methods::

    root = sim.backtrace_wire('03dfbb16')
    sim.print_backtrace('03dfbb16')
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ifetchrocks_sim.simulator import Simulator
    from ifetchrocks_sim.labels import LabelRegistry

from ifetchrocks_sim.devices.data_processing.memory.small_loop_break import SmallLoopBreak
from ifetchrocks_sim.devices.data_processing.memory.large_loop_break import LargeLoopBreak
from ifetchrocks_sim.devices.unknown_device import UnknownDevice


@dataclass
class TraceNode:
    kind: str                          # 'wire' or 'device'
    uuid: str                          # full UUID (or prefix for not-found wires)
    label: str                         # human-readable description
    type_id: Optional[int] = None      # device type integer; None for wires
    type_name: str = ''                # Python class name; empty for wires
    is_unknown: bool = False           # True if UnknownDevice
    is_loop_break: bool = False        # True → children is empty (leaf)
    wire_value: Optional[int] = None   # current wire value; None for devices
    is_cycle: bool = False             # True when cycle or max_depth guard hit
    children: list = field(default_factory=list)  # list[TraceNode]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_wire_label(wire_uuid: str, label_registry: Optional['LabelRegistry']) -> str:
    """Return a human label for *wire_uuid* if the registry has one, else the default."""
    if label_registry is not None:
        try:
            user_label = label_registry.get(wire_uuid)
            if user_label:
                return f'{user_label} [wire:{wire_uuid[:8]}]'
        except Exception:
            pass
    return f'wire:{wire_uuid[:8]}'


def _resolve_device_label(
    dev_uuid: str,
    type_name: str,
    type_id: Optional[int],
    label_registry: Optional['LabelRegistry'],
) -> str:
    """Return a human label for *dev_uuid* if the registry has one, else the default."""
    if label_registry is not None:
        try:
            user_label = label_registry.get(dev_uuid)
            if user_label:
                return f'{user_label} [{type_name}:{dev_uuid[:8]}]'
        except Exception:
            pass
    return f'{type_name}[{dev_uuid[:8]}] type={type_id}'


def _find_wire(sim: 'Simulator', prefix: str) -> Optional[str]:
    """Return the first wire UUID in sim.data_network.networks that starts with prefix."""
    for key in sim.data_network.networks:
        if key.startswith(prefix):
            return key
    return None


def _backtrace(
    sim: 'Simulator',
    wire_uuid: str,
    uuid_to_device: dict,
    structural_output_map: dict,
    visited: frozenset,
    depth: int,
    max_depth: int,
    label_registry: Optional['LabelRegistry'] = None,
) -> TraceNode:
    # Guard: cycle
    if wire_uuid in visited:
        return TraceNode(
            kind='wire',
            uuid=wire_uuid,
            label=f'wire:{wire_uuid[:8]} [CYCLE]',
            is_cycle=True,
        )
    # Guard: depth limit
    if depth > max_depth:
        return TraceNode(
            kind='wire',
            uuid=wire_uuid,
            label=f'wire:{wire_uuid[:8]} [MAX_DEPTH]',
            is_cycle=True,
        )

    # Immutable update so siblings do NOT share visited state
    visited = visited | {wire_uuid}

    net = sim.data_network.networks.get(wire_uuid)
    wire_value = net.value if net is not None else None
    wire_node = TraceNode(
        kind='wire',
        uuid=wire_uuid,
        label=_resolve_wire_label(wire_uuid, label_registry),
        wire_value=wire_value,
    )

    # Collect driver device UUIDs: union of runtime sources + structural claims
    driver_uuids: set = set()
    if net is not None:
        driver_uuids.update(net.sources.keys())
    for dev in structural_output_map.get(wire_uuid, []):
        driver_uuids.add(dev.uuid)

    for dev_uuid in driver_uuids:
        device = uuid_to_device.get(dev_uuid)
        if device is None:
            # UUID in net.sources but not in found_devices → placeholder
            wire_node.children.append(TraceNode(
                kind='device',
                uuid=dev_uuid,
                label=f'DEVICE_NOT_FOUND[{dev_uuid[:8]}]',
                is_unknown=True,
            ))
            continue

        is_lb = isinstance(device, (SmallLoopBreak, LargeLoopBreak))
        is_unk = isinstance(device, UnknownDevice)
        type_id = (
            device.data.get('type')
            if hasattr(device, 'data') and isinstance(device.data, dict)
            else None
        )
        type_name = type(device).__name__

        dev_node = TraceNode(
            kind='device',
            uuid=dev_uuid,
            label=_resolve_device_label(dev_uuid, type_name, type_id, label_registry),
            type_id=type_id,
            type_name=type_name,
            is_unknown=is_unk,
            is_loop_break=is_lb,
        )
        wire_node.children.append(dev_node)

        if is_lb:
            continue  # LEAF — do not recurse into loop-break inputs

        # Collect all input wires of this device
        input_wires: list = []
        for w in getattr(device, 'input_networks', []):
            if w and w not in input_wires:
                input_wires.append(w)
        for w in getattr(device, 'large_input_networks', []):
            if w and w not in input_wires:
                input_wires.append(w)

        for in_wire_uuid in input_wires:
            child = _backtrace(
                sim, in_wire_uuid,
                uuid_to_device, structural_output_map,
                visited, depth + 1, max_depth,
                label_registry,
            )
            dev_node.children.append(child)

    return wire_node


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def backtrace_wire(
    sim: 'Simulator',
    wire_prefix: str,
    max_depth: int = 20,
    label_registry: Optional['LabelRegistry'] = None,
) -> TraceNode:
    """
    Trace all ancestors of the first wire matching wire_prefix.

    Returns a TraceNode tree rooted at the wire.
    SmallLoopBreak / LargeLoopBreak are included as leaf device nodes
    (no recursion into their inputs).
    UnknownDevice instances are flagged with is_unknown=True.
    """
    # Build UUID → device map
    uuid_to_device: dict = {}
    for device_list in sim.found_devices.values():
        for device in device_list:
            uuid_to_device[device.uuid] = device

    # Build wire UUID → list[device] structural output map
    structural_output_map: dict = defaultdict(list)
    for device_list in sim.found_devices.values():
        for device in device_list:
            for w in getattr(device, 'output_networks', []):
                if w:
                    structural_output_map[w].append(device)
            for w in getattr(device, 'large_output_networks', []):
                if w:
                    structural_output_map[w].append(device)

    wire_uuid = _find_wire(sim, wire_prefix)
    if wire_uuid is None:
        # Return a placeholder node when the wire doesn't exist
        return TraceNode(
            kind='wire',
            uuid=wire_prefix,
            label=f'wire:{wire_prefix[:8]} [NOT FOUND]',
        )

    return _backtrace(
        sim, wire_uuid,
        uuid_to_device, structural_output_map,
        frozenset(), 0, max_depth,
        label_registry,
    )


def print_backtrace(
    sim: 'Simulator',
    wire_prefix: str,
    max_depth: int = 20,
    label_registry: Optional['LabelRegistry'] = None,
) -> None:
    """Print the ancestor tree to stdout."""
    root = backtrace_wire(sim, wire_prefix, max_depth, label_registry=label_registry)
    _print_node(root, indent=0)


def _print_node(node: TraceNode, indent: int) -> None:
    pad = '  ' * indent
    if node.kind == 'wire':
        flags = ''
        if node.is_cycle:
            flags = f' [{("CYCLE" if "CYCLE" in node.label else "MAX_DEPTH")}]'
        value_str = f' [value={node.wire_value}]' if node.wire_value is not None else ''
        print(f'{pad}{node.label}{value_str}{flags}')
    else:
        flags = ''
        if node.is_loop_break:
            flags += ' [LOOP_BREAK leaf]'
        if node.is_unknown:
            flags += ' [UNKNOWN]'
        if node.is_cycle:
            flags += ' [CYCLE]'
        print(f'{pad}\u2190 {node.label}{flags}')
    for child in node.children:
        _print_node(child, indent + 1)


# ---------------------------------------------------------------------------
# Forward trace — downstream consumers
# ---------------------------------------------------------------------------

def _forwardtrace(
    sim: 'Simulator',
    wire_uuid: str,
    structural_input_map: dict,
    visited: frozenset,
    depth: int,
    max_depth: int,
    label_registry: Optional['LabelRegistry'] = None,
) -> TraceNode:
    """Recursive forward-trace kernel (wire → consuming devices → output wires)."""
    if wire_uuid in visited:
        return TraceNode(
            kind='wire',
            uuid=wire_uuid,
            label=f'wire:{wire_uuid[:8]} [CYCLE]',
            is_cycle=True,
        )
    if depth > max_depth:
        return TraceNode(
            kind='wire',
            uuid=wire_uuid,
            label=f'wire:{wire_uuid[:8]} [MAX_DEPTH]',
            is_cycle=True,
        )

    visited = visited | {wire_uuid}

    net = sim.data_network.networks.get(wire_uuid)
    wire_value = net.value if net is not None else None
    wire_node = TraceNode(
        kind='wire',
        uuid=wire_uuid,
        label=_resolve_wire_label(wire_uuid, label_registry),
        wire_value=wire_value,
    )

    for device in structural_input_map.get(wire_uuid, []):
        is_lb = isinstance(device, (SmallLoopBreak, LargeLoopBreak))
        is_unk = isinstance(device, UnknownDevice)
        type_id = (
            device.data.get('type')
            if hasattr(device, 'data') and isinstance(device.data, dict)
            else None
        )
        type_name = type(device).__name__

        dev_node = TraceNode(
            kind='device',
            uuid=device.uuid,
            label=_resolve_device_label(device.uuid, type_name, type_id, label_registry),
            type_id=type_id,
            type_name=type_name,
            is_unknown=is_unk,
            is_loop_break=is_lb,
        )
        wire_node.children.append(dev_node)

        if is_lb:
            continue  # LEAF — loop-break output is a next-tick boundary

        output_wires: list = []
        for w in getattr(device, 'output_networks', []):
            if w and w not in output_wires:
                output_wires.append(w)
        for w in getattr(device, 'large_output_networks', []):
            if w and w not in output_wires:
                output_wires.append(w)

        for out_wire_uuid in output_wires:
            child = _forwardtrace(
                sim, out_wire_uuid,
                structural_input_map,
                visited, depth + 1, max_depth,
                label_registry,
            )
            dev_node.children.append(child)

    return wire_node


def forwardtrace_wire(
    sim: 'Simulator',
    wire_prefix: str,
    max_depth: int = 20,
    label_registry: Optional['LabelRegistry'] = None,
) -> TraceNode:
    """
    Trace all downstream consumers of the first wire matching wire_prefix.

    Returns a TraceNode tree rooted at the wire.
    SmallLoopBreak / LargeLoopBreak are included as leaf device nodes
    (no recursion into their outputs — they are a tick boundary).
    UnknownDevice instances are flagged with is_unknown=True.
    """
    # Build wire UUID → list[device] structural consumer map
    structural_input_map: dict = defaultdict(list)
    for device_list in sim.found_devices.values():
        for device in device_list:
            for w in getattr(device, 'input_networks', []):
                if w:
                    structural_input_map[w].append(device)
            for w in getattr(device, 'large_input_networks', []):
                if w:
                    structural_input_map[w].append(device)

    wire_uuid = _find_wire(sim, wire_prefix)
    if wire_uuid is None:
        return TraceNode(
            kind='wire',
            uuid=wire_prefix,
            label=f'wire:{wire_prefix[:8]} [NOT FOUND]',
        )

    return _forwardtrace(
        sim, wire_uuid,
        structural_input_map,
        frozenset(), 0, max_depth,
        label_registry,
    )


def print_forwardtrace(
    sim: 'Simulator',
    wire_prefix: str,
    max_depth: int = 20,
    label_registry: Optional['LabelRegistry'] = None,
) -> None:
    """Print the downstream consumer tree to stdout."""
    root = forwardtrace_wire(sim, wire_prefix, max_depth, label_registry=label_registry)
    _print_forward_node(root, indent=0)


def _print_forward_node(node: TraceNode, indent: int) -> None:
    pad = '  ' * indent
    if node.kind == 'wire':
        flags = ''
        if node.is_cycle:
            flags = f' [{("CYCLE" if "CYCLE" in node.label else "MAX_DEPTH")}]'
        value_str = f' [value={node.wire_value}]' if node.wire_value is not None else ''
        print(f'{pad}{node.label}{value_str}{flags}')
    else:
        flags = ''
        if node.is_loop_break:
            flags += ' [LOOP_BREAK leaf]'
        if node.is_unknown:
            flags += ' [UNKNOWN]'
        if node.is_cycle:
            flags += ' [CYCLE]'
        print(f'{pad}\u2192 {node.label}{flags}')
    for child in node.children:
        _print_forward_node(child, indent + 1)


# ---------------------------------------------------------------------------
# Signal path finder — BFS from source wire to target wire
# ---------------------------------------------------------------------------

def find_signal_path(
    sim: 'Simulator',
    source_prefix: str,
    target_prefix: str,
    max_depth: int = 50,
    label_registry: Optional['LabelRegistry'] = None,
) -> Optional[list]:
    """
    BFS from the first wire matching source_prefix to any wire matching
    target_prefix, walking forward through consuming devices.

    Returns a list of 3-tuples alternating 'wire' and 'device' hops::

        [
            ('wire',   '897d1b80', 'wire:897d1b80'),
            ('device', '49bb870a', 'Register[49bb870a] type=128'),
            ('wire',   '03dfbb16', 'wire:03dfbb16'),
        ]

    Returns None when:
    - source_prefix has no matching wire
    - no path to target_prefix exists within max_depth hops
    """
    source_uuid = _find_wire(sim, source_prefix)
    if source_uuid is None:
        return None

    # Build wire UUID → list[device] structural consumer map
    structural_input_map: dict = defaultdict(list)
    for device_list in sim.found_devices.values():
        for device in device_list:
            for w in getattr(device, 'input_networks', []):
                if w:
                    structural_input_map[w].append(device)
            for w in getattr(device, 'large_input_networks', []):
                if w:
                    structural_input_map[w].append(device)

    def _wire_hop(uuid: str) -> tuple:
        label = None
        if label_registry is not None:
            try:
                label = label_registry.get(uuid)
            except Exception:
                pass
        return ('wire', uuid[:8], label if label else f'wire:{uuid[:8]}')

    def _device_hop(device, type_name: str, type_id) -> tuple:
        label = None
        if label_registry is not None:
            try:
                label = label_registry.get(device.uuid)
            except Exception:
                pass
        if label:
            label_str = f'{label} [{type_name}:{device.uuid[:8]}]'
        else:
            label_str = f'{type_name}[{device.uuid[:8]}] type={type_id}'
        return ('device', device.uuid[:8], label_str)

    visited: set = set()
    start_hop = _wire_hop(source_uuid)
    # Queue items: (wire_uuid, path_so_far, depth)
    queue: deque = deque([(source_uuid, [start_hop], 0)])

    while queue:
        wire_uuid, path, depth = queue.popleft()

        if wire_uuid in visited:
            continue
        visited.add(wire_uuid)

        # Check whether this wire satisfies the target
        if wire_uuid.startswith(target_prefix):
            return path

        if depth >= max_depth:
            continue  # depth limit — do not explore further from here

        for device in structural_input_map.get(wire_uuid, []):
            # Unknown devices: outputs are not known structurally — cannot traverse
            if isinstance(device, UnknownDevice):
                continue

            type_id = (
                device.data.get('type')
                if hasattr(device, 'data') and isinstance(device.data, dict)
                else None
            )
            type_name = type(device).__name__
            dev_hop = _device_hop(device, type_name, type_id)

            output_wires: list = []
            for w in getattr(device, 'output_networks', []):
                if w and w not in output_wires:
                    output_wires.append(w)
            for w in getattr(device, 'large_output_networks', []):
                if w and w not in output_wires:
                    output_wires.append(w)

            for out_uuid in output_wires:
                if out_uuid not in visited:
                    queue.append((out_uuid, path + [dev_hop, _wire_hop(out_uuid)], depth + 1))

    return None
