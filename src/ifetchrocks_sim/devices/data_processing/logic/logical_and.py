from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class LogicalAndGate:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Logical AND Gate'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceLogicalAND.png'
        self.uuid = data['uuid']
        indexed_children = list(data['indexedChildren'].values())
        self.network_in_1 = indexed_children[0]['uuid']
        self.network_in_2 = indexed_children[1]['uuid']
        self.network_out = indexed_children[2]['uuid']
        self.in_value_a = 0
        self.in_value_b = 0
        self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1, self.network_in_2]
        self.output_networks = [self.network_out]
        network_manager.get_network(self.network_in_1).register_listener(self.update_in_1)
        network_manager.get_network(self.network_in_2).register_listener(self.update_in_2)

    def update_in_1(self, uuid: str, value: int):
        self.in_value_a = value
        self.update_and_notify()

    def update_in_2(self, uuid: str, value: int):
        self.in_value_b = value
        self.update_and_notify()

    def update_and_notify(self):
        if self.in_value_a and self.in_value_b:
            self.value = 1
        else:
            self.value = 0
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
