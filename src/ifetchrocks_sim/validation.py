"""Simulator structural validation (FR-28 / FR-31).

FR-28 — Wire Direction Validator:
- no_source / multi_source / no_listener / self_loop anomalies

FR-31 — Port-Map Cross-Validator:
- missing_in_code: save has a wire port the device doesn't handle
- missing_in_save: device references a UUID not in the save (fabricated)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ifetchrocks_sim.simulator import Simulator


@dataclass
class WireAnomaly:
    kind: str          # 'no_source' | 'multi_source' | 'no_listener' | 'self_loop'
    severity: str      # 'error' | 'warning'
    wire_uuid: str
    wire_type: str     # 'data' | 'large_data' | 'power'
    devices: list[str] = field(default_factory=list)
    message: str = ''


@dataclass
class WireDirectionReport:
    total_wires: int = 0
    wires_with_no_source: int = 0
    wires_with_multi_source: int = 0
    wires_with_no_listener: int = 0
    self_loops: int = 0
    anomalies: list[WireAnomaly] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f'Total wires scanned: {self.total_wires}',
            f'  no_source:    {self.wires_with_no_source}',
            f'  multi_source: {self.wires_with_multi_source}',
            f'  no_listener:  {self.wires_with_no_listener}',
            f'  self_loop:    {self.self_loops}',
        ]
        return '\n'.join(lines)


# Device classes whose self-listener on their own UUID should be ignored
# when counting listeners. These are wire-representation nodes, not real consumers.
_PASSTHROUGH_TYPE_NAMES = frozenset({
    'NetworkNode', 'LargeNetworkNode', 'NetworkPowerNode',
})


def _is_passthrough(device) -> bool:
    return type(device).__name__ in _PASSTHROUGH_TYPE_NAMES


def _build_wire_device_map(sim: 'Simulator'):
    """Build uuid→set(device_uuid) maps for input and output classifications."""
    wire_to_input_devs: dict[str, set[str]] = {}
    wire_to_output_devs: dict[str, set[str]] = {}

    for room_devs in sim.found_devices.values():
        for dev in room_devs:
            dev_uuid = getattr(dev, 'uuid', None)
            if dev_uuid is None:
                continue

            # Collect all wires this device declares as inputs
            for attr in ('input_networks', 'large_input_networks', 'input_power_networks'):
                for wire_uuid in getattr(dev, attr, []):
                    wire_to_input_devs.setdefault(wire_uuid, set()).add(dev_uuid)

            # Collect all wires this device declares as outputs
            for attr in ('output_networks', 'large_output_networks', 'power_output_networks'):
                for wire_uuid in getattr(dev, attr, []):
                    wire_to_output_devs.setdefault(wire_uuid, set()).add(dev_uuid)

    return wire_to_input_devs, wire_to_output_devs


def _collect_passthrough_uuids(sim: 'Simulator') -> set[str]:
    """Collect UUIDs of all pass-through network node devices."""
    result = set()
    for room_devs in sim.found_devices.values():
        for dev in room_devs:
            if _is_passthrough(dev):
                result.add(dev.uuid)
    return result


def validate_wire_directions(sim: 'Simulator', *, ignore_power: bool = False) -> WireDirectionReport:
    """Scan all wires in *sim* and return a WireDirectionReport."""
    report = WireDirectionReport()
    wire_to_input_devs, wire_to_output_devs = _build_wire_device_map(sim)
    passthrough_uuids = _collect_passthrough_uuids(sim)

    dnm = sim.data_network

    # Collect all wires to scan: (uuid, network_obj, wire_type)
    wires_to_scan: list[tuple[str, object, str]] = []

    for uuid, net in dnm.networks.items():
        wires_to_scan.append((uuid, net, 'data'))

    for uuid, net in dnm.large_networks.items():
        wires_to_scan.append((uuid, net, 'large_data'))

    if not ignore_power:
        for uuid, net in dnm.power_networks.items():
            wires_to_scan.append((uuid, net, 'power'))

    report.total_wires = len(wires_to_scan)

    for wire_uuid, net, wire_type in wires_to_scan:
        num_sources = len(net.sources)

        # Count real listeners, excluding pass-through nodes listening
        # on their own UUID (they are wire representations, not consumers).
        real_listener_count = len(net.listener_functions)
        if wire_uuid in passthrough_uuids:
            # The node registers exactly one listener on its own UUID
            real_listener_count = max(0, real_listener_count - 1)

        # --- no_source ---
        if num_sources == 0 and real_listener_count > 0:
            report.wires_with_no_source += 1
            report.anomalies.append(WireAnomaly(
                kind='no_source',
                severity='error',
                wire_uuid=wire_uuid,
                wire_type=wire_type,
                message=f'Wire {wire_uuid} has {real_listener_count} listener(s) but no source',
            ))

        # --- multi_source (data/large_data only) ---
        if num_sources > 1 and wire_type in ('data', 'large_data'):
            report.wires_with_multi_source += 1
            source_devs = list(net.sources.keys())
            report.anomalies.append(WireAnomaly(
                kind='multi_source',
                severity='warning',
                wire_uuid=wire_uuid,
                wire_type=wire_type,
                devices=source_devs,
                message=f'Wire {wire_uuid} has {num_sources} sources: {source_devs}',
            ))

        # --- no_listener ---
        if num_sources > 0 and real_listener_count == 0:
            report.wires_with_no_listener += 1
            report.anomalies.append(WireAnomaly(
                kind='no_listener',
                severity='warning',
                wire_uuid=wire_uuid,
                wire_type=wire_type,
                message=f'Wire {wire_uuid} has {num_sources} source(s) but no listeners',
            ))

        # --- self_loop ---
        in_devs = wire_to_input_devs.get(wire_uuid, set())
        out_devs = wire_to_output_devs.get(wire_uuid, set())
        overlap = in_devs & out_devs
        if overlap:
            report.self_loops += len(overlap)
            for dev_uuid in overlap:
                report.anomalies.append(WireAnomaly(
                    kind='self_loop',
                    severity='error',
                    wire_uuid=wire_uuid,
                    wire_type=wire_type,
                    devices=[dev_uuid],
                    message=f'Device {dev_uuid} has wire {wire_uuid} in both input and output',
                ))

    return report


# ---------------------------------------------------------------------------
# FR-31: Port-Map Cross-Validator
# ---------------------------------------------------------------------------

# Wire port type IDs in the save JSON (indexedChildren entries).
_WIRE_TYPE_IDS = frozenset({2, 3, 4, 5})

# Device class names excluded from audit (wire-representation or placeholder).
_AUDIT_SKIP_CLASSES = _PASSTHROUGH_TYPE_NAMES | frozenset({'UnknownDevice'})


@dataclass
class PortMismatch:
    device_uuid: str
    type_id: int
    type_name: str
    kind: str        # 'missing_in_code' | 'missing_in_save'
    port_key: str
    detail: str


@dataclass
class PortAuditReport:
    mismatches: list[PortMismatch] = field(default_factory=list)
    devices_audited: int = 0
    devices_clean: int = 0
    devices_with_issues: int = 0

    def summary(self) -> str:
        lines = [
            f'Devices audited: {self.devices_audited}',
            f'  clean:  {self.devices_clean}',
            f'  issues: {self.devices_with_issues}',
            f'  mismatches: {len(self.mismatches)}',
        ]
        return '\n'.join(lines)


def _get_save_wire_ports(data: dict) -> dict[str, str]:
    """Return {port_key: uuid} for every wire-type child in indexedChildren."""
    result: dict[str, str] = {}
    for key, child in data.get('indexedChildren', {}).items():
        if child is None:
            continue
        if child.get('type') in _WIRE_TYPE_IDS:
            result[key] = child['uuid']
    return result


def _get_device_used_uuids(dev) -> set[str]:
    """Collect all wire UUIDs the device claims to use."""
    uuids: set[str] = set()
    for attr in (
        'input_networks', 'output_networks',
        'large_input_networks', 'large_output_networks',
        'input_power_networks', 'power_output_networks',
        'large_input_power_networks', 'large_power_output_networks',
    ):
        for u in getattr(dev, attr, []):
            if u is not None:
                uuids.add(u)
    return uuids


def audit_port_maps(sim: 'Simulator') -> PortAuditReport:
    """FR-31: Compare device port usage against save data for every device."""
    report = PortAuditReport()

    for room_devs in sim.found_devices.values():
        for dev in room_devs:
            cls_name = type(dev).__name__
            if cls_name in _AUDIT_SKIP_CLASSES:
                continue

            data = getattr(dev, 'data', None)
            if data is None:
                continue

            report.devices_audited += 1
            type_id = data.get('type', -1)

            save_ports = _get_save_wire_ports(data)
            save_uuids = set(save_ports.values())
            device_uuids = _get_device_used_uuids(dev)

            has_issue = False

            # Ports in save but not used by device → missing_in_code
            for port_key, wire_uuid in save_ports.items():
                if wire_uuid not in device_uuids:
                    has_issue = True
                    report.mismatches.append(PortMismatch(
                        device_uuid=dev.uuid,
                        type_id=type_id,
                        type_name=cls_name,
                        kind='missing_in_code',
                        port_key=port_key,
                        detail=f'Save port {port_key} (wire {wire_uuid}) not used by {cls_name}',
                    ))

            # UUIDs used by device but not in save → missing_in_save (fabricated)
            fabricated = device_uuids - save_uuids
            for fab_uuid in fabricated:
                has_issue = True
                report.mismatches.append(PortMismatch(
                    device_uuid=dev.uuid,
                    type_id=type_id,
                    type_name=cls_name,
                    kind='missing_in_save',
                    port_key='',
                    detail=f'Device uses wire {fab_uuid} not present in save',
                ))

            if has_issue:
                report.devices_with_issues += 1
            else:
                report.devices_clean += 1

    return report


# ---------------------------------------------------------------------------
# FR-33: Device Port Audit Report (per-device drill-down of FR-31)
# ---------------------------------------------------------------------------

@dataclass
class DevicePortReport:
    uuid: str
    type_id: int
    type_name: str
    expected_input_ports: dict[str, str]   # port_key -> description
    expected_output_ports: dict[str, str]
    save_port_keys: set[str]
    matched: set[str]
    missing_from_code: set[str]
    missing_from_save: set[str]
    has_todo_ports: bool


def _find_device_by_prefix(sim: 'Simulator', prefix: str):
    for room_devs in sim.found_devices.values():
        for dev in room_devs:
            if getattr(dev, 'uuid', '').startswith(prefix):
                return dev
    raise KeyError(f"No device with UUID prefix '{prefix}' found")


def _extract_port_descriptions(dev, attr: str) -> dict[str, str]:
    """Extract {port_key: description} from a network_*_descriptions dict."""
    return dict(getattr(dev, attr, {}))


def audit_device_ports(sim: 'Simulator', uuid_prefix: str) -> DevicePortReport:
    """FR-33: Per-device port audit comparing save data against device class."""
    dev = _find_device_by_prefix(sim, uuid_prefix)
    data = getattr(dev, 'data', {})
    type_id = data.get('type', -1) if isinstance(data, dict) else -1
    cls_name = type(dev).__name__

    save_ports = _get_save_wire_ports(data) if isinstance(data, dict) else {}
    save_uuids = set(save_ports.values())
    device_uuids = _get_device_used_uuids(dev)

    in_desc = _extract_port_descriptions(dev, 'network_in_descriptions')
    out_desc = _extract_port_descriptions(dev, 'network_out_descriptions')

    save_keys = set(save_ports.keys())
    code_keys = set(in_desc.keys()) | set(out_desc.keys())

    matched = set()
    missing_from_code = set()
    for port_key, wire_uuid in save_ports.items():
        if wire_uuid in device_uuids:
            matched.add(port_key)
        else:
            missing_from_code.add(port_key)

    missing_from_save = device_uuids - save_uuids

    has_todo = any('TODO' in str(k) or 'todo' in str(k) for k in
                   list(in_desc.keys()) + list(out_desc.keys()) +
                   list(in_desc.values()) + list(out_desc.values()))

    return DevicePortReport(
        uuid=dev.uuid,
        type_id=type_id,
        type_name=cls_name,
        expected_input_ports=in_desc,
        expected_output_ports=out_desc,
        save_port_keys=save_keys,
        matched=matched,
        missing_from_code=missing_from_code,
        missing_from_save=missing_from_save,
        has_todo_ports=has_todo,
    )


def print_device_port_report(report: DevicePortReport, file=None) -> None:
    """Print a formatted per-device port audit report."""
    import sys
    out = file if file is not None else sys.stdout
    print(f"Device: {report.type_name} [{report.uuid}]  type={report.type_id}", file=out)
    print(f"  Save ports:         {len(report.save_port_keys)}", file=out)
    print(f"  Matched:            {len(report.matched)}", file=out)
    print(f"  Missing from code:  {len(report.missing_from_code)}", file=out)
    print(f"  Missing from save:  {len(report.missing_from_save)}", file=out)
    print(f"  Has TODO ports:     {report.has_todo_ports}", file=out)
    if report.missing_from_code:
        print("  Missing from code:", file=out)
        for k in sorted(report.missing_from_code):
            print(f"    port {k}", file=out)
    if report.missing_from_save:
        print("  Missing from save (fabricated):", file=out)
        for u in sorted(report.missing_from_save):
            print(f"    wire {u[:8]}", file=out)


# ---------------------------------------------------------------------------
# FR-30: Unknown Device Census & Classification
# ---------------------------------------------------------------------------

@dataclass
class UnknownDeviceClassification:
    uuid: str
    type_id: int
    impact: str   # 'blocking' | 'source_side' | 'sink_side' | 'isolated'
    input_wire_count: int
    output_wire_count: int
    known_sources: list[str] = field(default_factory=list)
    known_consumers: list[str] = field(default_factory=list)


@dataclass
class UnknownDeviceReport:
    devices: list[UnknownDeviceClassification] = field(default_factory=list)
    blocking_count: int = 0
    source_side_count: int = 0
    sink_side_count: int = 0
    isolated_count: int = 0

    def summary(self) -> str:
        total = len(self.devices)
        return (
            f'{total} UnknownDevice instances — '
            f'{self.blocking_count} blocking, '
            f'{self.source_side_count} source-side, '
            f'{self.sink_side_count} sink-side, '
            f'{self.isolated_count} isolated'
        )


def classify_unknown_devices(sim: 'Simulator') -> UnknownDeviceReport:
    """FR-30: Classify every UnknownDevice by signal impact."""
    report = UnknownDeviceReport()

    # Build lookup: wire_uuid → set of device UUIDs that use it (known devices only)
    wire_to_known_sources: dict[str, set[str]] = {}
    wire_to_known_consumers: dict[str, set[str]] = {}

    for room_devs in sim.found_devices.values():
        for dev in room_devs:
            cls_name = type(dev).__name__
            if cls_name == 'UnknownDevice':
                continue
            dev_uuid = getattr(dev, 'uuid', None)
            if dev_uuid is None:
                continue

            # This device's outputs → it is a source for those wires
            for attr in ('output_networks', 'large_output_networks', 'power_output_networks'):
                for wire_uuid in getattr(dev, attr, []):
                    wire_to_known_sources.setdefault(wire_uuid, set()).add(dev_uuid)

            # This device's inputs → it is a consumer of those wires
            for attr in ('input_networks', 'large_input_networks', 'input_power_networks'):
                for wire_uuid in getattr(dev, attr, []):
                    wire_to_known_consumers.setdefault(wire_uuid, set()).add(dev_uuid)

    # Now classify each UnknownDevice
    for room_devs in sim.found_devices.values():
        for dev in room_devs:
            if type(dev).__name__ != 'UnknownDevice':
                continue

            unk_wires = set()
            for attr in ('input_networks', 'large_input_networks', 'input_power_networks'):
                unk_wires.update(getattr(dev, attr, []))

            known_sources: list[str] = []
            known_consumers: list[str] = []

            for wire_uuid in unk_wires:
                # Known devices that drive this wire → they are upstream of the unknown
                for src in wire_to_known_sources.get(wire_uuid, set()):
                    if src not in known_sources:
                        known_sources.append(src)
                # Known devices that listen on this wire → they are downstream
                for con in wire_to_known_consumers.get(wire_uuid, set()):
                    if con not in known_consumers:
                        known_consumers.append(con)

            has_known_src = len(known_sources) > 0
            has_known_con = len(known_consumers) > 0

            if has_known_src and has_known_con:
                impact = 'blocking'
                report.blocking_count += 1
            elif has_known_con:
                impact = 'source_side'
                report.source_side_count += 1
            elif has_known_src:
                impact = 'sink_side'
                report.sink_side_count += 1
            else:
                impact = 'isolated'
                report.isolated_count += 1

            report.devices.append(UnknownDeviceClassification(
                uuid=dev.uuid,
                type_id=getattr(dev, 'data', {}).get('type', -1),
                impact=impact,
                input_wire_count=len(unk_wires),
                output_wire_count=0,  # UnknownDevice never has output_networks
                known_sources=known_sources,
                known_consumers=known_consumers,
            ))

    return report


# ---------------------------------------------------------------------------
# FR-29: Post-Load Circuit Health Check
# ---------------------------------------------------------------------------

@dataclass
class HealthReport:
    wire_direction: WireDirectionReport = field(default_factory=WireDirectionReport)
    unknown_devices: UnknownDeviceReport = field(default_factory=UnknownDeviceReport)
    port_audit: PortAuditReport = field(default_factory=PortAuditReport)

    @property
    def error_count(self) -> int:
        count = 0
        for a in self.wire_direction.anomalies:
            if a.severity == 'error':
                count += 1
        count += self.wire_direction.self_loops
        return count

    @property
    def warning_count(self) -> int:
        count = 0
        for a in self.wire_direction.anomalies:
            if a.severity == 'warning':
                count += 1
        count += len(self.port_audit.mismatches)
        return count

    def summary(self) -> str:
        lines = [
            '=== Circuit Health Check ===',
            f'Wire direction:   {self.wire_direction.wires_with_no_source} errors, '
            f'{self.wire_direction.wires_with_multi_source} multi-source warnings '
            f'(of {self.wire_direction.total_wires} wires)',
            f'Unknown devices:  {self.unknown_devices.blocking_count} blocking '
            f'(of {len(self.unknown_devices.devices)} total unknown)',
            f'Port audit:       {self.port_audit.devices_with_issues} devices with issues '
            f'(of {self.port_audit.devices_audited} audited)',
            f'Total: {self.error_count} errors, {self.warning_count} warnings',
        ]
        return '\n'.join(lines)


def health_check(sim: 'Simulator', *, ignore_power: bool = True) -> HealthReport:
    """FR-29: Run all structural validators and return a consolidated report."""
    report = HealthReport()
    report.wire_direction = validate_wire_directions(sim, ignore_power=ignore_power)
    report.unknown_devices = classify_unknown_devices(sim)
    report.port_audit = audit_port_maps(sim)
    return report


# ---------------------------------------------------------------------------
# FR-34: Dead Wire Detection
# ---------------------------------------------------------------------------

@dataclass
class DeadWireInfo:
    wire_uuid: str
    label: str | None
    source_count: int
    listener_count: int
    upstream_has_unknown: bool


@dataclass
class DeadWireReport:
    dead_wires: list[DeadWireInfo]
    total_wires: int
    active_wires: int
    dead_percentage: float


def detect_dead_wires(sim: 'Simulator',
                      warmup_ticks: int = 10,
                      wire_type: str = 'data') -> DeadWireReport:
    """FR-34: Identify wires that have sources and listeners but value stuck at 0."""
    # Run warmup ticks
    for t in range(1, warmup_ticks + 1):
        sim.set_tick(t)

    # Select which network dict to scan
    if wire_type == 'data':
        nets = sim.data_network.networks
    elif wire_type == 'large':
        nets = sim.data_network.large_networks
    elif wire_type == 'power':
        nets = sim.data_network.power_networks
    else:  # 'all'
        nets = {**sim.data_network.networks}

    dead = []
    active_count = 0
    total = 0

    for uuid, net in nets.items():
        src_count = len(net.sources)
        listener_count = len(net.listener_functions)
        # Skip wires with no sources (FR-28 territory)
        if src_count == 0:
            continue
        # Skip wires with no listeners (not useful)
        if listener_count == 0:
            continue
        total += 1
        if net.value == 0:
            dead.append(DeadWireInfo(
                wire_uuid=uuid,
                label=None,
                source_count=src_count,
                listener_count=listener_count,
                upstream_has_unknown=False,
            ))
        else:
            active_count += 1

    pct = (len(dead) / total * 100.0) if total > 0 else 0.0
    return DeadWireReport(
        dead_wires=dead,
        total_wires=total,
        active_wires=active_count,
        dead_percentage=pct,
    )


def print_dead_wire_report(report: DeadWireReport, file=None) -> None:
    """Print a formatted dead wire report."""
    import sys
    out = file if file is not None else sys.stdout
    print(f"Dead Wire Report: {len(report.dead_wires)} dead / "
          f"{report.total_wires} total ({report.dead_percentage:.1f}%)", file=out)
    print(f"  Active: {report.active_wires}", file=out)
    if report.dead_wires:
        print("  Dead wires:", file=out)
        for info in report.dead_wires[:20]:  # limit output
            print(f"    {info.wire_uuid[:12]}  sources={info.source_count}  "
                  f"listeners={info.listener_count}", file=out)
        if len(report.dead_wires) > 20:
            print(f"    ... and {len(report.dead_wires) - 20} more", file=out)


# ---------------------------------------------------------------------------
# FR-35: Runtime Wire Anomaly Monitor
# ---------------------------------------------------------------------------

@dataclass
class WireAnomalyEvent:
    tick: int
    wire_uuid: str
    kind: str         # 'overflow' | 'type_error' | 'multi_driver_conflict' | 'oscillation'
    detail: str
    source_uuid: str | None = None


class WireAnomalyMonitor:
    """Wraps DataNetwork.update_source to catch runtime anomalies."""

    def __init__(self, sim: 'Simulator', *,
                 max_value_changes_per_tick: int = 100,
                 max_events: int = 10_000):
        self._sim = sim
        self._max_changes = max_value_changes_per_tick
        self._max_events = max_events
        self._events: list[WireAnomalyEvent] = []
        self._enabled = False
        self._patched: dict[str, object] = {}  # wire_uuid → original update_source
        self._change_counts: dict[str, int] = {}  # wire_uuid → changes this tick

    def enable(self) -> None:
        if self._enabled:
            return
        self._enabled = True
        for uuid, net in self._sim.data_network.networks.items():
            self._patch_network(uuid, net)

    def disable(self) -> None:
        if not self._enabled:
            return
        self._enabled = False
        for uuid, original in self._patched.items():
            net = self._sim.data_network.networks.get(uuid)
            if net is not None:
                net.update_source = original
        self._patched.clear()
        self._change_counts.clear()

    def get_events(self) -> list[WireAnomalyEvent]:
        return list(self._events)

    @property
    def event_count(self) -> int:
        return len(self._events)

    def reset_tick_counters(self) -> None:
        self._change_counts.clear()

    def _add_event(self, event: WireAnomalyEvent) -> None:
        if len(self._events) < self._max_events:
            self._events.append(event)

    def _patch_network(self, wire_uuid: str, net) -> None:
        original = net.update_source
        self._patched[wire_uuid] = original
        monitor = self

        def wrapped_update_source(source_uuid: str, value, _orig=original,
                                  _uuid=wire_uuid, _mon=monitor):
            if _mon._validate_write(_uuid, source_uuid, value, net):
                return _orig(source_uuid, value)

        net.update_source = wrapped_update_source

    def _validate_write(self, wire_uuid: str, source_uuid: str, value, net) -> bool:
        """Validate a write. Returns True if the value should be forwarded."""
        tick = 0  # could be retrieved from sim if available

        # Type check
        if not isinstance(value, int):
            self._add_event(WireAnomalyEvent(
                tick=tick, wire_uuid=wire_uuid, kind='type_error',
                detail=f'Non-int value {type(value).__name__}: {value!r}',
                source_uuid=source_uuid,
            ))
            return False  # don't forward invalid type

        # Overflow check
        if value < 0 or value > 65535:
            self._add_event(WireAnomalyEvent(
                tick=tick, wire_uuid=wire_uuid, kind='overflow',
                detail=f'Value {value} out of 16-bit range',
                source_uuid=source_uuid,
            ))

        # Multi-driver conflict: different non-zero values from different sources
        if len(net.sources) > 1:
            other_values = {v for k, v in net.sources.items()
                           if k != source_uuid and v != 0}
            if other_values and value != 0:
                for ov in other_values:
                    if ov != value:
                        self._add_event(WireAnomalyEvent(
                            tick=tick, wire_uuid=wire_uuid,
                            kind='multi_driver_conflict',
                            detail=f'{source_uuid} writes {value} but other source(s) have {other_values}',
                            source_uuid=source_uuid,
                        ))
                        break

        # Oscillation check
        count = self._change_counts.get(wire_uuid, 0) + 1
        self._change_counts[wire_uuid] = count
        if count == self._max_changes + 1:  # fire once at threshold
            self._add_event(WireAnomalyEvent(
                tick=tick, wire_uuid=wire_uuid, kind='oscillation',
                detail=f'Wire changed {count} times (threshold {self._max_changes})',
                source_uuid=source_uuid,
            ))

        return True
