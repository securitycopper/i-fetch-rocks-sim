from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import (
    build_large_network_in, build_large_network_out,
    build_network_in, build_network_out,
    build_power_network_in, build_power_out, build_large_power_out,
    build_vector_network_in,
    graph_mappings, register_listeners,
)

PORT_VM_1 = '540409561'
PORT_VM_2 = '-2110735685'
PORT_VM_3 = '514493837'
PORT_VM_4 = '-1143678734'
PORT_VMO = '329536179'

VECTOR_WIDTH = 8


class PacketVectorMerger:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        self.type = 150
        self.name = 'Packet Vector Merger'
        self.image = 'http://ifetch.rocks/manual/images/PacketVectorMerger.png'

        self._in = [[0] * VECTOR_WIDTH for _ in range(4)]

        self.network_in_data = build_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={})

        self.large_network_in_data = build_large_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={})

        self.vector_in_data = build_vector_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={
                PORT_VM_1: 'VM_1',
                PORT_VM_2: 'VM_2',
                PORT_VM_3: 'VM_3',
                PORT_VM_4: 'VM_4',
            })

        self.power_in_data = build_power_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={})

        self.large_power_in_data = build_power_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={})

        self.network_out_data = build_network_out(
            network_manager=network_manager, data=data,
            network_in_descriptions={})

        self.large_network_out_data = build_large_network_out(
            network_manager=network_manager, data=data,
            network_in_descriptions={PORT_VMO: 'VMO'})

        self.power_out_data = build_power_out(
            network_manager=network_manager, data=data,
            network_in_descriptions={})

        self.large_power_out_data = build_large_power_out(
            network_manager=network_manager, data=data,
            network_in_descriptions={})

        register_listeners(
            network_manager=network_manager,
            network_in_data=self.network_in_data,
            large_network_in_data=self.large_network_in_data,
            power_in_data=self.power_in_data,
            large_power_in_data=self.large_power_in_data,
            vector_in_data=self.vector_in_data,
        )

        graph_mappings(self)

    def change_event(self, component_id: str, large_data_in):
        slot = {PORT_VM_1: 0, PORT_VM_2: 1, PORT_VM_3: 2, PORT_VM_4: 3}.get(component_id)
        if slot is None:
            return
        self._in[slot] = list(large_data_in[:VECTOR_WIDTH])
        self._emit()

    def _emit(self):
        out = []
        for slot in range(4):
            out.extend(self._in[slot])
        # ensure 32 length
        out = out + [0] * (32 - len(out))
        self.network_manager.get_large_network(
            self.large_network_out_data[PORT_VMO]['uuid']
        ).update_source(self.uuid, out)
