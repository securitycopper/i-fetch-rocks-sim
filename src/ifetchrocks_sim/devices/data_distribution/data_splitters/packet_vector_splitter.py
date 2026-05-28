from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import (
    build_large_network_in, build_large_network_out,
    build_network_in, build_network_out,
    build_power_network_in, build_power_out, build_large_power_out,
    build_vector_network_out,
    graph_mappings, register_listeners,
)

PORT_VSI = '-1837781274'
PORT_VS_1 = '-718066353'
PORT_VS_2 = '1099708799'
PORT_VS_3 = '1657941518'
PORT_VS_4 = '38280862'

VECTOR_WIDTH = 8
LARGE_NET_WIDTH = 32


class PacketVectorSplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        self.type = 149
        self.name = 'Packet Vector Splitter'
        self.image = 'http://ifetch.rocks/manual/images/PacketVectorSplitter.png'

        self.network_in_data = build_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={})

        self.large_network_in_data = build_large_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={
                PORT_VSI: 'VSI',
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
            network_in_descriptions={})

        self.vector_out_data = build_vector_network_out(
            network_manager=network_manager, data=data,
            network_in_descriptions={
                PORT_VS_1: 'VS_1',
                PORT_VS_2: 'VS_2',
                PORT_VS_3: 'VS_3',
                PORT_VS_4: 'VS_4',
            })

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
        )

        graph_mappings(self)

    def change_event(self, component_id: str, large_data_in):
        if component_id != PORT_VSI:
            return
        slots = [PORT_VS_1, PORT_VS_2, PORT_VS_3, PORT_VS_4]
        for i, port_key in enumerate(slots):
            start = i * VECTOR_WIDTH
            vec = list(large_data_in[start:start + VECTOR_WIDTH])
            # pad to 32
            vec = vec + [0] * (LARGE_NET_WIDTH - len(vec))
            self.network_manager.get_large_network(
                self.vector_out_data[port_key]['uuid']
            ).update_source(self.uuid, vec)
