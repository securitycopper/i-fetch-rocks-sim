from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class SingleChannelSplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Single Channel Splitter'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceSmallDataSplitter1.png'
        self.uuid = data['uuid']
        #indexed_children = list(data['indexedChildren'].values())
        self.network_in_1 = get_connection_uuid_by_id(data, '-502982437')
        self.network_out_1 = get_connection_uuid_by_id(data, '-1408653082')
        self.network_out_2 = get_connection_uuid_by_id(data, '198003536')
        self.network_out_3 = get_connection_uuid_by_id(data, '1367693113')
        self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1]
        self.output_networks = [self.network_out_1, self.network_out_2, self.network_out_3]
        network_manager.get_network(self.network_in_1).register_listener(self.update_in_1)

    def update_in_1(self, uuid: str, value: int):
        if self.value != value:
            self.value = value
            self.update_and_notify()

    def update_and_notify(self):
        for uuid in self.output_networks:
            self.network_manager.get_network(uuid).update_source(self.uuid, self.value)
