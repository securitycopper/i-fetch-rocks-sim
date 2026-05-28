"""FR-10: CircuitBuilder DSL — declarative construction of test circuits.

Build a minimal Simulator with hand-picked devices and connections without
needing a real save file.

Usage::

    sim = (CircuitBuilder()
        .add_device(128, 'reg-001')
        .add_device(14, 'scs-001')
        .connect('scs-001', '1892577010', 'reg-001', '-723312417', 'wire-data')
        .build())
"""

from __future__ import annotations

import uuid as _uuid
from typing import Any

from ifetchrocks_sim.simulator import Simulator, ComponentType, DeviceClasses


class CircuitBuilder:
    """Declarative builder for constructing minimal test circuits."""

    def __init__(self) -> None:
        self._devices: dict[str, dict[str, Any]] = {}
        self._connections: list[dict[str, Any]] = []

    def add_device(
        self,
        type_id: int,
        device_uuid: str,
        device_data: dict | None = None,
        location: int = 0,
    ) -> CircuitBuilder:
        """Register a device by type ID and UUID.

        *device_data* is an optional dict merged into ``indexedDeviceData``.
        """
        self._devices[device_uuid] = {
            'type_id': type_id,
            'uuid': device_uuid,
            'device_data': device_data or {},
            'location': location,
        }
        return self

    def connect(
        self,
        from_device: str,
        from_port: str,
        to_device: str,
        to_port: str,
        wire_uuid: str | None = None,
        wire_type: int = 5,
    ) -> CircuitBuilder:
        """Connect *from_device* output port to *to_device* input port.

        Port IDs are the string keys used in ``indexedChildren`` (e.g.
        ``'-723312417'`` for Register DATA_IN).  *wire_type* defaults to 5
        (small data); use 4 for large data, 3 for power.
        """
        if wire_uuid is None:
            wire_uuid = str(_uuid.uuid4())
        self._connections.append({
            'from_device': from_device,
            'from_port': from_port,
            'to_device': to_device,
            'to_port': to_port,
            'wire_uuid': wire_uuid,
            'wire_type': wire_type,
        })
        return self

    def connect_power(
        self,
        from_device: str,
        from_port: str,
        to_device: str,
        to_port: str,
        wire_uuid: str | None = None,
    ) -> CircuitBuilder:
        """Convenience: connect a power wire (type 3)."""
        return self.connect(from_device, from_port, to_device, to_port,
                            wire_uuid=wire_uuid, wire_type=3)

    def build(self) -> Simulator:
        """Construct a :class:`Simulator` with the declared devices & wires."""
        sim = Simulator()

        for dev_uuid, spec in self._devices.items():
            data = self._build_component(dev_uuid, spec)
            type_id = spec['type_id']
            try:
                enum_name = ComponentType(type_id).name
                device_class = DeviceClasses[enum_name].value
            except (ValueError, KeyError):
                continue  # skip unknown type IDs

            device = device_class(sim.data_network, data)
            sim.found_devices['TEST'].append(device)

        return sim

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_component(self, dev_uuid: str, spec: dict) -> dict:
        """Build the minimal ``data`` dict a device constructor expects."""
        indexed_children: dict[str, dict] = {}
        for conn in self._connections:
            if conn['from_device'] == dev_uuid:
                indexed_children[conn['from_port']] = {
                    'uuid': conn['wire_uuid'],
                    'type': conn['wire_type'],
                }
            if conn['to_device'] == dev_uuid:
                indexed_children[conn['to_port']] = {
                    'uuid': conn['wire_uuid'],
                    'type': conn['wire_type'],
                }

        indexed_device_data: dict[str, dict] = {}
        for key, value in spec['device_data'].items():
            if isinstance(value, dict):
                indexed_device_data[key] = value
            else:
                indexed_device_data[key] = {'signal': value}

        return {
            'uuid': dev_uuid,
            'type': spec['type_id'],
            'location': spec['location'],
            'signalValue': 0,
            'indexedChildren': indexed_children,
            'indexedDeviceData': indexed_device_data,
        }
