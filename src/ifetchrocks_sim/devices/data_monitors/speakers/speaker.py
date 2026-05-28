from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class Speaker:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 37
        self.name = 'Speaker'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceSpeakerSmall.png'
        self.uuid = data['uuid']
        self.network_in_1 = get_connection_uuid_by_id(data, '-1006544213')
        self.network_in_2 = get_connection_uuid_by_id(data, '-953607294')
        # Power
        self.network_in_3 = get_connection_uuid_by_id(data, '225736748')

        self.in_value_a = 0
        self.in_value_b = 0
        self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        # Store full 16-bit tone inputs (frequency/wavelength) per device spec
        self.frequency = 0
        self.wavelength = 0
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1, self.network_in_2]
        self.input_networks_labels = ['Height', 'Width']
        self.output_networks = []
        self.input_power_networks = [self.network_in_3]
        network_manager.get_network(self.input_networks[0]).register_listener(self.update_in_1)
        network_manager.get_network(self.input_networks[1]).register_listener(self.update_in_2)

    def update_in_1(self, uuid: str, value: int):
        self.in_value_a = value
        self.update_and_notify()

    def update_in_2(self, uuid: str, value: int):
        self.in_value_b = value
        self.update_and_notify()

    def update_and_notify(self):
        # Preserve the raw 16-bit input values for frequency and wavelength
        self.frequency = self.in_value_a
        self.wavelength = self.in_value_b
        #self.network_manager.get_network(self.network_out_1).update_source(self.uuid, self.current_value)
