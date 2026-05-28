from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import build_network_in, build_network_out, \
    build_power_network_in, build_large_network_in, build_large_network_out, build_power_out, build_large_power_out, \
    graph_mappings, register_listeners


class LargeLoopBreak:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        # ----- Non Changing -----
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        # ----- Set for the device -----
        self.type = 131
        self.name = 'Loop Break'
        self.image = 'http://ifetch.rocks/manual/images/LargeLoopBreak.png'
        self.value = [0 for x in range(16)]#  data['signalValue']

        # ----- Inputs -----
        self.network_in_data = build_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        self.large_network_in_data = build_large_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
            '-144486197': 'IN'
        })
        self.power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        self.large_power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        # ----- Outputs -----
        self.network_out_data = build_network_out(network_manager=network_manager, data=data, network_in_descriptions={
        })
        self.large_network_out_data = build_large_network_out(network_manager=network_manager, data=data, network_in_descriptions={
            '1767847113': 'OUT'
        })
        self.power_out_data = build_power_out(network_manager=network_manager, data=data, network_in_descriptions={
        })
        self.large_power_out_data = build_large_power_out(network_manager=network_manager, data=data, network_in_descriptions={
        })
        register_listeners(network_manager=network_manager, network_in_data=self.network_in_data,
                           large_network_in_data=self.large_network_in_data, power_in_data=self.power_in_data,
                           large_power_in_data=self.large_power_in_data)
        self.value_buffer = self.value
        self.next_value = self.value
        network_manager.register_start_of_tick_listener(self.start_of_tick)
        network_manager.register_end_of_tick_listener(self.end_of_tick)
        # ----- Graph Mappings -----
        graph_mappings(self)

    def change_event(self, component_id: str, value):
        self.value_buffer = value

    def end_of_tick(self):
        self.next_value = self.value_buffer

    def start_of_tick(self):
        if self.value != self.next_value:
            self.value = self.next_value
            net = self.network_manager.get_large_network(self.large_network_out_data['1767847113']['uuid'])
            net.sources[self.uuid] = self.value
            calculated_value = [0] * 32
            for v in net.sources.values():
                calculated_value = [calculated_value[i] | x for i, x in enumerate(v)]
            if calculated_value != net.value:
                net.value = calculated_value
                self.network_manager.queue_notify(net)