from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class NetworkPowerNode:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = ' '
        self.color = 'red'
        self.uuid = data['uuid']
        self.input_networks = []
        self.output_networks = []
        self.value = 0
        network_manager.get_power_network(self.uuid).register_listener(self.update_value)

    def update_value(self, uuid: str, value: int):
        self.value = value
