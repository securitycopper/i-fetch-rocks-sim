from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
"""

"""


class ControllerDial:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Dial'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DevicePrecisionDial.png'
        self.uuid = data['uuid']
        children = list(data['indexedChildren'].values())
        self.network_out = children[0]['uuid'] if children else None
        device_data = list(data['indexedDeviceData'].values())
        self.value = device_data[0]['signal'] if device_data else 0
        self.network_manager = network_manager
        if self.network_out:
            self.notify()
        self.input_networks = []
        self.output_networks = [self.network_out] if self.network_out else []

    def set_value(self, value: int):
        if self.value == value:
            pass
        else:
            self.value = value
            self.notify()

    def notify(self):
        if self.network_out:
            self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
