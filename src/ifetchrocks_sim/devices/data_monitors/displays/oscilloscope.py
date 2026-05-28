from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class Oscilloscope:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Oscilloscope'
        self.color = 'blue'
        self.image = 'https://ifetch.rocks/manual/images/DeviceOscilloscopeSmall1.png'
        self.uuid = data['uuid']
        #connections = get_connections_uuids_of_type(data,5)
        self.network_in_1 = get_connection_uuid_by_id(data, '-1081620509')

        self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1]
        self.output_networks = []
        self.input_power_networks = [get_connection_uuid_by_id(data, '320224663')]
        self.output_power_networks = []

        network_manager.get_network(self.network_in_1).register_listener(self.update_in_1)
        self.update_and_notify()

    def update_in_1(self, uuid: str, value: int):
        if self.value != value:
            self.value = value
            self.update_and_notify()

    def update_and_notify(self):
        pass  # Oscilloscope is capture-only; no output wires
