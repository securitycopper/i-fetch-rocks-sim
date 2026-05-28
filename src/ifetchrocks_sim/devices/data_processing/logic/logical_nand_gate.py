from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class LogicalNandGate:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Logical NAND Gate'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceLogicalNAND.png'
        self.uuid = data['uuid']
        self.network_in_1 = get_connection_uuid_by_id(data, '-108496386')
        self.network_in_2 = get_connection_uuid_by_id(data, '-1305286718')
        self.network_out = get_connection_uuid_by_id(data, '835233603')
        self.in_value_a = 0
        self.in_value_b = 0
        self.value = data['signalValue']
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1, self.network_in_2]
        self.output_networks = [self.network_out]
        network_manager.get_network(self.network_in_1).register_listener(self.update_in_1)
        network_manager.get_network(self.network_in_2).register_listener(self.update_in_2)

    def update_in_1(self, uuid: str, value: int):
        self.in_value_a = value
        self.update_and_notify()

    def update_in_2(self, uuid: str, value: int):
        self.in_value_b = value
        self.update_and_notify()

    def update_and_notify(self):
        if self.in_value_a and self.in_value_b:
            self.value = 0
        else:
            self.value = 1
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
