"""
CargoGunController type 200

/CONTROLLERS/SPECIAL/CARGO_GUN_CONTROLLER

Remote control for the Cargo Unit Mailing Gun.
- Power input activates the propulsion rails and catchment net.
- Fire input (port 0) activates all propulsion rails to deliver payload.
- Target input (port 1) aligns the gun to the target direction.
- Vector cable output is a special cable type (not a data network port).

Port keys (confirmed from save 102d6094, 2026-03-21):
  '1369211778'   → power in     (type 3)
  '976786033'    → fire input   (type 5) — port 0
  '-409896587'   → target input (type 5) — port 1
  '-1831628104'  → vector cable out (type 142 when unconnected; special cable)

Simulation note: this is a sink device — inputs are received but there are no
data-network outputs to propagate.
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class CargoGunController:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'CargoGunController'
        self.color = 'orange'
        self.type = 200
        self.image = 'http://ifetch.rocks/manual/images/CUMBox.png'
        self.uuid = data['uuid']

        self.network_power_in = get_connection_uuid_by_id(data, '1369211778')
        self.network_fire_in  = get_connection_uuid_by_id(data, '976786033')
        self.network_target_in = get_connection_uuid_by_id(data, '-409896587')

        self.fire = 0
        self.target = 0

        self.network_manager = network_manager
        self.input_networks = [self.network_fire_in, self.network_target_in]
        self.output_networks = []
        self.input_power_networks = [self.network_power_in]
        self.output_power_networks = []

        network_manager.get_network(self.network_fire_in).register_listener(self._update_fire)
        network_manager.get_network(self.network_target_in).register_listener(self._update_target)

    def _update_fire(self, uuid: str, value: int):
        self.fire = value

    def _update_target(self, uuid: str, value: int):
        self.target = value
