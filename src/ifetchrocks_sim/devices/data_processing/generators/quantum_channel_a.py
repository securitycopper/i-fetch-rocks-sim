from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class QuantumChannelA:
    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 30
        self.name = 'Quantum Channel A'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceSignalChannelA.png'
        self.uuid = data['uuid']
        self.network_out = get_connection_uuid_by_id(data, '317431772')
        self.value = data['signalValue']
        self.network_manager = network_manager
        self.notify()
        self.input_networks = []
        self.output_networks = [self.network_out]
        network_manager.register_start_of_tick_listener(self._start_of_tick)

    def _start_of_tick(self):
        """Toggle output each tick to produce a clock signal."""
        self.value = 0 if self.value else 65535
        self.notify()

    def press_with_value(self, value: int):
        if self.value == value:
            pass
        else:
            self.value = value
            self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
