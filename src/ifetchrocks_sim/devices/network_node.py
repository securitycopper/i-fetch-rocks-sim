from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class NetworkNode:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Small Data'
        self.color = ['#97c2fc',
                      '#fcba03',
                      '#b1fc03',
                      '#66fc03',
                      '#17fc03',
                      '#03a5fc',
                      '#0352fc',
                      '#3903fc',
                      '#8403fc',
                      '#c203fc',
                      '#fc03be',
                      '#516616',
                      '#256616',
                      '#164b66',
                      '#162a66'][data['location']]
        if 'color' in data:
            self.color = data['color']
            if self.color == 'gray':
                self.do_not_prune = True
        self.uuid = data['uuid']
        self.input_networks = []
        self.output_networks = []
        self.value = 0
        network_manager.get_network(self.uuid).register_listener(self.update_value)

    def update_value(self, uuid: str, value: int):
        self.value = value
