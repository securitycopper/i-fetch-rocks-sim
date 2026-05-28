from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager

class LargePowerSplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Large Power Splitter'
        self.color = 'red'
        self.type = 12
        self.image = 'https://ifetch.rocks/manual/images/DevicePowerSplitterLarge1.png'
        self.uuid = data['uuid']
        #indexed_children = list(data['indexedChildren'].values())
        self.network_in_0 = get_connection_uuid_by_id(data, '-685701939')

        # # Small Output 0
        self.network_out_0 = get_connection_uuid_by_id(data, '1835965805')
        # # Small Output 1
        self.network_out_1 = get_connection_uuid_by_id(data, '-2038134035')
        # # Small output 2
        self.network_out_2 = get_connection_uuid_by_id(data, '472048673')
        # # Small output 3
        #self.network_out_3 = get_connection_uuid_by_id(data, '')

        # Large Outputs
        self.network_out_4 = get_connection_uuid_by_id(data, '1337601985')
        self.network_out_5 = get_connection_uuid_by_id(data, '1754219019')
        #.network_out_6 = get_connection_uuid_by_id(data, '') #TODO: Missing

        self.value = 0
        self.network_manager = network_manager
        self.output_networks = []
        self.input_networks = []
        self.input_power_networks = []
        self.output_power_networks = [self.network_out_0, self.network_out_1, self.network_out_2]#, self.network_out_3]
        self.large_input_power_networks = [self.network_in_0]
        self.large_output_power_networks = [self.network_out_4, self.network_out_5]#, self.network_out_6]

        network_manager.get_network(self.network_in_0).register_listener(self.update_in_0)

    def update_in_0(self, uuid: str, value: int):
        if self.value != value:
            self.value = value
            self.network_manager.get_network(self.network_out_0).update_source(self.uuid, self.value)
            self.network_manager.get_network(self.network_out_1).update_source(self.uuid, self.value)
            self.network_manager.get_network(self.network_out_2).update_source(self.uuid, self.value)
            #self.network_manager.get_network(self.network_out_3).update_source(self.uuid, self.value)
            self.network_manager.get_network(self.network_out_4).update_source(self.uuid, self.value)
            self.network_manager.get_network(self.network_out_5).update_source(self.uuid, self.value)
            #self.network_manager.get_network(self.network_out_6).update_source(self.uuid, self.value)

