from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

class TallConduit:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        # T18
        self.data = data
        self.name = 'Tall Conduit'
        self.color = 'blue'
        self.type = 18
        self.image = 'http://ifetch.rocks/manual/images/DeviceLongDataRun.png'
        self.uuid = data['uuid']

        # Channel A
        self.network_in_a = get_connection_uuid_by_id(data, '-1316151547')
        self.network_out_a = get_connection_uuid_by_id(data, '-2040321929')

        # Channel B
        self.network_in_b = get_connection_uuid_by_id(data, '329364927')
        self.network_out_b = get_connection_uuid_by_id(data, '772311218')

        # Channel C
        self.network_in_c = get_connection_uuid_by_id(data, '228941609')
        self.network_out_c = get_connection_uuid_by_id(data, '9499664')

        self.value = [0, 0, 0]
        self.network_manager = network_manager
        self.input_networks = [self.network_in_a, self.network_in_b, self.network_in_c]
        self.output_networks = [self.network_out_a, self.network_out_b, self.network_out_c]

        if self.network_in_a:
            network_manager.get_network(self.network_in_a).register_listener(self.input_a)
        if self.network_in_b:
            network_manager.get_network(self.network_in_b).register_listener(self.input_b)
        if self.network_in_c:
            network_manager.get_network(self.network_in_c).register_listener(self.input_c)

    def _set_bit(self, bit_index: int, state_value: int, output_network: str):
        if self.value[bit_index] != state_value:
            self.value[bit_index] = state_value
            if output_network:
                self.network_manager.get_network(output_network).update_source(self.uuid, self.value[bit_index])

    def input_a(self, uuid: str, value: int):
        self._set_bit(0, value, self.network_out_a)

    def input_b(self, uuid: str, value: int):
        self._set_bit(1, value, self.network_out_b)

    def input_c(self, uuid: str, value: int):
        self._set_bit(2, value, self.network_out_c)
