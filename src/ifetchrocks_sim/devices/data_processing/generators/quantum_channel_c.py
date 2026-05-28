import random

from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class QuantumChannelC:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 113
        self.name = 'Quantum Channel C'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceSignalChannelC.png'
        self.uuid = data['uuid']
        self.network_out = get_connection_uuid_by_id(data, '-762024798')
        self.value = data['signalValue']
        self.network_manager = network_manager
        self.input_networks = []
        self.output_networks = [self.network_out]
        network_manager.register_start_of_tick_listener(self._on_tick)
        self.notify()

    def _on_tick(self):
        self.value = random.randint(0, 65535)
        self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
