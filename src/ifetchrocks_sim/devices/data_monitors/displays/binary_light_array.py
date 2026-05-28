from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class BinaryLightArray:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Binary Light Array'
        self.color = 'blue'
        self.type = 122
        self.image = 'http://ifetch.rocks/manual/images/SmallBinaryLightArray.png'
        self.uuid = data['uuid']

        self.value = data['signalValue']

        # Small data
        self.network_in_0 = get_connection_uuid_by_id(data, '832364048')
        # Small power
        self.network_in_1 = get_connection_uuid_by_id(data, '-1831826590')

        # Small Output 0
        self.network_out_0 = get_connection_uuid_by_id(data, '-1186727754')

        self.value = 0
        self.network_manager = network_manager
        self.output_networks = [self.network_out_0]
        self.input_networks = [self.network_in_0]
        self.input_power_networks = [self.network_in_1]
        self.output_power_networks = []
        self.large_input_power_networks = []
        self.large_output_power_networks = []

        network_manager.get_network(self.network_in_0).register_listener(self.update_in_0)

    def update_in_0(self, uuid: str, value: int):
        if self.value != value:
            self.value = value
            self.network_manager.get_network(self.network_out_0).update_source(self.uuid, self.value)

