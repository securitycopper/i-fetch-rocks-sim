from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

"""

"""


class SmallSlider:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Small Slider'
        self.color = 'blue'
        self.image = 'https://ifetch.rocks/manual/images/DeviceSliderSmall1.png'
        self.uuid = data['uuid']
        self.network_out_0 = get_connection_uuid_by_id(data, '-368547900')
        self.value = list(data['indexedDeviceData'].values())[0]['signal']
        self.network_manager = network_manager
        self.notify()
        self.input_networks = []
        self.output_networks = [self.network_out_0]

    def set_value(self, value: int):
        if self.value == value:
            pass
        else:
            self.value = value
            self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_out_0).update_source(self.uuid, self.value)
