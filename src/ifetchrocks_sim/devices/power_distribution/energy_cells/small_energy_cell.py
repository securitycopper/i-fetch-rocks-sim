"""
SmallEnergyCell type 38

/POWER_DISTRIBUTION/ENERGY_CELLS/SMALL_CELL

Stores power and discharges it via the output power port.
The data port outputs the charge amount as a percent (0–65535).

Port keys (confirmed from save 102d6094, 2026-03-21):
  '1568832946'  → small power in  (type 3)
  '-1290612885' → small power out (type 3)
  '1941549567'  → data out        (type 5) — charge level as percent 0-65535

Simulation note: actual charge/discharge dynamics are not modelled. The
incoming power value is used directly as the charge proxy. Data out mirrors the
power-in value; power out passes through the same value.
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class SmallEnergyCell:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'SmallEnergyCell'
        self.color = 'green'
        self.type = 38
        self.image = 'http://ifetch.rocks/manual/images/DeviceSmallEnergyCell.png'
        self.uuid = data['uuid']

        self.network_power_in  = get_connection_uuid_by_id(data, '1568832946')
        self.network_power_out = get_connection_uuid_by_id(data, '-1290612885')
        self.network_data_out  = get_connection_uuid_by_id(data, '1941549567')

        self.charge = 0
        self.network_manager = network_manager
        self.input_networks = []
        self.output_networks = [self.network_data_out]
        self.input_power_networks = [self.network_power_in]
        self.output_power_networks = [self.network_power_out]

        network_manager.get_network(self.network_power_in).register_listener(self._update_power_in)

    def _update_power_in(self, uuid: str, value: int):
        if self.charge != value:
            self.charge = value
            self._notify()

    def _notify(self):
        self.network_manager.get_network(self.network_data_out).update_source(self.uuid, self.charge)
        self.network_manager.get_network(self.network_power_out).update_source(self.uuid, self.charge)
