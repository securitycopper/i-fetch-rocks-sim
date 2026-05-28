from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class WideConduit:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        # T17
        self.data = data
        self.name = 'Wide Conduit'
        self.color = 'blue'
        self.type = 17
        self.image = 'http://ifetch.rocks/manual/images/DeviceLongDataRun.png'
        self.uuid = data['uuid']
        #indexed_children = list(data['indexedChildren'].values())
        self.network_in_0 = get_connection_uuid_by_id(data, '753767426')
        self.network_in_1 = get_connection_uuid_by_id(data, '428061559')
        self.network_in_2 = get_connection_uuid_by_id(data, '-1962081887')

        self.network_out_0 = get_connection_uuid_by_id(data, '591740751')
        self.network_out_1 = get_connection_uuid_by_id(data, '-734831681')
        self.network_out_2 = get_connection_uuid_by_id(data, '-157943722')

        # self.network_out_2 = get_connection_uuid_by_id(data, '198003536')
        # self.network_out_3 = get_connection_uuid_by_id(data, '1367693113')
        #self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        #self.switch = list(data['indexedDeviceData'].values())[0]['signal']
        self.value = [0,0,0]
        self.network_manager = network_manager
        self.input_networks = [self.network_in_0,
                               self.network_in_1,
                               self.network_in_2,

                               ]
        self.output_networks = [self.network_out_0,
                                self.network_out_1,
                                self.network_out_2
                                ]
        network_manager.get_network(self.network_in_0).register_listener(self.input0)
        network_manager.get_network(self.network_in_1).register_listener(self.input1)
        network_manager.get_network(self.network_in_2).register_listener(self.input2)

    # Generic bit-setting function
    def _set_bit(self, bit_index: int, state_value: int):
        if self.value[bit_index] != state_value:
            self.value[bit_index] = state_value
            self.network_manager.get_network(self.output_networks[bit_index]).update_source(self.uuid, self.value[bit_index])

    # Public functions to set input0, input1, input2
    def input0(self, uuid: str, value: int):
        self._set_bit(0, value)

    def input1(self, uuid: str, value: int):
        self._set_bit(1, value)

    def input2(self, uuid: str, value: int):
        self._set_bit(2, value)

