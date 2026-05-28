from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connections_uuids_of_type


class UnknownDevice:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = f'Unknown[T:{data['type']},R:{data['location']}]'
        self.color = 'black'
        #self.image = 'http://ifetch.rocks/manual/images/DeviceLogicalNOR.png'
        self.uuid = data['uuid']
        indexed_children = list(data['indexedChildren'].values())
        self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        self.network_manager = network_manager
        self.input_networks = get_connections_uuids_of_type(data,5)
        #self.input_power_networks = get_connections_uuids_of_type(data,3)
        self.input_power_networks = get_connections_uuids_of_type(data, 3)
        self.large_input_networks = get_connections_uuids_of_type(data, 4)
        self.output_networks = []

        # self.output_power_networks = []
        self.large_input_power_networks = get_connections_uuids_of_type(data,2)
        # self.large_output_power_networks = []

        self.shape = 'square'
        if self.large_input_networks:
            self.size = 20
        if data['type'] == 1:
            self.size = 30





