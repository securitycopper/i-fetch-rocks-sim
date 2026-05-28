from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class LogicalNorGate:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Logical Nor Gate'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceLogicalNOR.png'
        self.uuid = data['uuid']
        indexed_children = list(data['indexedChildren'].values())
        self.network_out = indexed_children[len(indexed_children)-1]['uuid']
        self.in_value_a = 0
        self.in_value_b = 0
        self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        self.network_manager = network_manager
        self.input_networks = [x['uuid'] for x in indexed_children[:-1]]
        self.output_networks = [self.network_out]
        if len(self.input_networks)> 0:
            network_manager.get_network(self.input_networks[0]).register_listener(self.update_in_1)
            if len(self.input_networks) > 1:
                network_manager.get_network(self.input_networks[1]).register_listener(self.update_in_2)

    def update_in_1(self, uuid: str, value: int):
        self.in_value_a = value
        self.update_and_notify()

    def update_in_2(self, uuid: str, value: int):
        self.in_value_b = value
        self.update_and_notify()

    def update_and_notify(self):
        if self.in_value_a or self.in_value_b:
            self.value = 0
        else:
            self.value = 1
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
