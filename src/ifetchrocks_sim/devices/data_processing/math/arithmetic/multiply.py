from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id, get_device_data_by_id


class ArithmeticMultiply:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Multiply'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceArithmeticMultiply.png'
        self.uuid = data['uuid']
        self.network_in_1 = get_connection_uuid_by_id(data, '1173709222')
        self.network_in_2 = get_connection_uuid_by_id(data, '2034020425')
        self.network_out_1 = get_connection_uuid_by_id(data, '-1790705161')

        self.in_value_a = 0
        self.in_value_b = 0
        self.value = get_device_data_by_id(data, '-2139921001')['signal']
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1, self.network_in_2]
        self.output_networks = [self.network_out_1]
        network_manager.get_network(self.input_networks[0]).register_listener(self.update_in_1)
        network_manager.get_network(self.input_networks[1]).register_listener(self.update_in_2)

    def update_in_1(self, uuid: str, value: int):
        self.in_value_a = value
        self.update_and_notify()

    def update_in_2(self, uuid: str, value: int):
        self.in_value_b = value
        self.update_and_notify()

    def update_and_notify(self):
        self.value = (self.in_value_a * self.in_value_b) % 65536
        self.network_manager.get_network(self.network_out_1).update_source(self.uuid, self.value)
