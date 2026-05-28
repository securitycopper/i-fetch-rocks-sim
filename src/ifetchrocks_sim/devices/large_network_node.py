from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from typing import List


class LargeNetworkNode:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = ' '
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
        self.size = 20
        self.uuid = data['uuid']
        self.input_networks = []
        self.output_networks = []
        self.large_output_networks = []
        self.large_input_networks = []
        self.value = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
        network_manager.get_large_network(self.uuid).register_listener(self.update_value)

    def to_string(self):
        to_return = ''
        for (k,v) in enumerate(self.value):
            if k == 0:
                to_return = f'{k}:{v}'
            else:
                to_return = f'{to_return}\n{k}:{v}'
        return to_return

    def label(self):
        return 'Large Data'

    def title(self):
        return f'{self.uuid}\n{self.to_string()}'

    def update_value(self, uuid: str, value: List[int]):
        self.value = value
