from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class BinaryMerger:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Binary Merger'
        self.color = 'blue'
        self.type = 115
        self.image = 'http://ifetch.rocks/manual/images/DeviceBinaryMergerLong.png'
        self.uuid = data['uuid']
        #indexed_children = list(data['indexedChildren'].values())
        self.network_in_0 = get_connection_uuid_by_id(data, '1771747123')
        self.network_in_1 = get_connection_uuid_by_id(data, '-600569250')
        self.network_in_2 = get_connection_uuid_by_id(data, '-1706500463')
        self.network_in_3 = get_connection_uuid_by_id(data, '574344766')
        self.network_in_4 = get_connection_uuid_by_id(data, '38987481')
        self.network_in_5 = get_connection_uuid_by_id(data, '558288065')
        self.network_in_6 = get_connection_uuid_by_id(data, '834909049')
        self.network_in_7 = get_connection_uuid_by_id(data, '1045518737')

        self.network_out_0 = get_connection_uuid_by_id(data, '1420098671')

        # self.network_out_2 = get_connection_uuid_by_id(data, '198003536')
        # self.network_out_3 = get_connection_uuid_by_id(data, '1367693113')
        #self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        self.switch = list(data['indexedDeviceData'].values())[0]['signal']
        self.value = 0
        self.network_manager = network_manager
        self.input_networks = [self.network_in_0,
                               self.network_in_1,
                               self.network_in_2,
                               self.network_in_3,
                               self.network_in_4,
                               self.network_in_5,
                               self.network_in_6,
                               self.network_in_7,

                               ]

        self.output_networks = [self.network_out_0]
        network_manager.get_network(self.input_networks[0]).register_listener(self.update_in_0)
        network_manager.get_network(self.input_networks[1]).register_listener(self.update_in_1)
        network_manager.get_network(self.input_networks[2]).register_listener(self.update_in_2)
        network_manager.get_network(self.input_networks[3]).register_listener(self.update_in_3)
        network_manager.get_network(self.input_networks[4]).register_listener(self.update_in_4)
        network_manager.get_network(self.input_networks[5]).register_listener(self.update_in_5)
        network_manager.get_network(self.input_networks[6]).register_listener(self.update_in_6)
        network_manager.get_network(self.input_networks[7]).register_listener(self.update_in_7)

    def update_output(self):
        self.network_manager.get_network(self.network_out_0).update_source(self.uuid, self.value)

    def _update_bit(self, index: int, value: int):
        # Determine the actual bit index depending on self.switch
        bit_index = index + 8 if self.switch else index
        mask = 1 << bit_index
        current_bit = (self.value >> bit_index) & 1
        new_bit = 1 if value > 0 else 0

        if current_bit != new_bit:
            if new_bit:
                self.value |= mask  # Set the bit
            else:
                self.value &= ~mask  # Clear the bit
            self.update_output()

    def update_in_0(self, uuid: str, value: int):
        self._update_bit(0, value)

    def update_in_1(self, uuid: str, value: int):
        self._update_bit(1, value)

    def update_in_2(self, uuid: str, value: int):
        self._update_bit(2, value)

    def update_in_3(self, uuid: str, value: int):
        self._update_bit(3, value)

    def update_in_4(self, uuid: str, value: int):
        self._update_bit(4, value)

    def update_in_5(self, uuid: str, value: int):
        self._update_bit(5, value)

    def update_in_6(self, uuid: str, value: int):
        self._update_bit(6, value)

    def update_in_7(self, uuid: str, value: int):
        self._update_bit(7, value)

