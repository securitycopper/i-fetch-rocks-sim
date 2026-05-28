from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class GeneratorPowerBus:
    """Large power cable (type 135) acting as a generator power bus.

    When a type-135 device appears as a child of a type-1 room frame, it is a
    multi-strand power cable rather than a BinaryMux.  The bus propagates a
    single power value to all 4 sub-wires (same port keys as BinaryMux but
    used as power outputs, not mux I/O).

    Port keys (shared with BinaryMux type 135):
        PORT_0 = '2034020425'
        PORT_1 = '563576145'
        PORT_2 = '1173709222'
        PORT_3 = '-1790705161'
    """

    PORT_0 = '2034020425'
    PORT_1 = '563576145'
    PORT_2 = '1173709222'
    PORT_3 = '-1790705161'

    ALL_PORT_KEYS = [PORT_0, PORT_1, PORT_2, PORT_3]

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Generator Power Bus'
        self.color = 'red'
        self.type = 135
        self.uuid = data['uuid']
        self.value = 0
        self.network_manager = network_manager

        # Collect the 4 sub-wire UUIDs from indexedChildren
        children = data.get('indexedChildren') or {}
        self.output_wires = []
        for key in self.ALL_PORT_KEYS:
            child = children.get(key)
            if isinstance(child, dict) and 'uuid' in child:
                self.output_wires.append(child['uuid'])

        self.input_networks = []
        self.output_networks = list(self.output_wires)
        self.output_power_networks = list(self.output_wires)

    def supply_power(self, value: int):
        """Drive all output wires to *value*."""
        if self.value != value:
            self.value = value
            for wire_uuid in self.output_wires:
                self.network_manager.get_network(wire_uuid).update_source(
                    self.uuid, value)
