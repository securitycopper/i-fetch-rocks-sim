from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

"""

"""

class SmallLoopBreak:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 130
        self.name = 'Small Loop Break'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/SmallLoopBreak.png'
        self.uuid = data['uuid']
        self.network_in_1 = get_connection_uuid_by_id(data, '-723312417')
        self.network_out_1 = get_connection_uuid_by_id(data, '1892577010')
        self.value = data['signalValue']
        self.value_buffer = self.value
        self.next_value = self.value
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1]
        self.output_networks = [self.network_out_1]
        network_manager.get_network(self.input_networks[0]).register_listener(self.update_in_1)
        network_manager.register_start_of_tick_listener(self.start_of_tick)
        network_manager.register_end_of_tick_listener(self.end_of_tick)

    def update_in_1(self, uuid: str, value: int):
        self.value_buffer = value

    def end_of_tick(self):
        self.next_value = self.value_buffer

    def start_of_tick(self):
        if self.value != self.next_value:
            self.value = self.next_value
            net = self.network_manager.get_network(self.network_out_1)
            net.sources[self.uuid] = self.value
            calculated_value = 0
            for v in net.sources.values():
                calculated_value |= v
            if calculated_value != net.value:
                net.value = calculated_value
                self.network_manager.queue_notify(net)

