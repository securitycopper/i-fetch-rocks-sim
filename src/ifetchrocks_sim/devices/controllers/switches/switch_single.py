from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
"""

"""


class SwitchSingle:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Switch'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/SingleSwitchDevice.png'
        self.uuid = data['uuid']
        self.network_out = list(data['indexedChildren'].values())[0]['uuid']
        self.value = list(data['indexedDeviceData'].values())[0]['signal']
        self.network_manager = network_manager
        self.notify()
        self.input_networks = []
        self.output_networks = [self.network_out]

    def press_with_value(self, value: int):
        if self.value == value:
            pass
        else:
            self.value = value
            self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
