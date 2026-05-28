"""
SmallSwitchedPower type 34

/POWER_DISTRIBUTION/POWER_SPLITTERS/SMALL_SWITCHED

Takes in a small power cable and distributes power output to connected small
power cables. The data input port disables power throughput when zero.

Port keys (confirmed from save 102d6094, 2026-03-21):
  '1779774388'  → small power in  (type 3)
  '-221728388'  → data in         (type 5)
  '1336288955'  → small power out (type 3)
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class SmallSwitchedPower:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'SmallSwitchedPower'
        self.color = 'red'
        self.type = 34
        self.image = 'http://ifetch.rocks/manual/images/DeviceSmallSwitchedPower1.png'
        self.uuid = data['uuid']

        self.network_power_in = get_connection_uuid_by_id(data, '1779774388')
        self.network_data_in  = get_connection_uuid_by_id(data, '-221728388')
        self.network_power_out = get_connection_uuid_by_id(data, '1336288955')

        self.value = [0, 0, 0]  # [power_in, data_in, last_output]
        self.network_manager = network_manager
        self.input_networks = [self.network_data_in]
        self.output_networks = []
        self.input_power_networks = [self.network_power_in]
        self.output_power_networks = [self.network_power_out]

        network_manager.get_power_network(self.network_power_in).register_listener(self._update_power_in)
        network_manager.get_network(self.network_data_in).register_listener(self._update_data_in)

    def _update_power_in(self, uuid: str, value: int):
        if self.value[0] != value:
            self.value[0] = value
            self._output()

    def _update_data_in(self, uuid: str, value: int):
        if self.value[1] != value:
            self.value[1] = value
            self._output()

    def _output(self):
        target_power = self.value[0] if self.value[1] else 0
        if self.value[2] != target_power:
            self.value[2] = target_power
            self.network_manager.get_power_network(self.network_power_out).update_source(
                self.uuid, target_power
            )
