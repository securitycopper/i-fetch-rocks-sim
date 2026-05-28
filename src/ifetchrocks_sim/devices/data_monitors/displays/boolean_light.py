from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class BooleanLight:
    """
    /DATA_MONITORS/DISPLAYS/BOOLEAN_LIGHT (type 214)

    Status light — activates when input signal is non-zero (true).
    Input port:  '373576006'
    Power port:  '-1270701682' (ignored in simulation)
    """

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 214
        self.name = 'Boolean Light'
        self.color = 'yellow'
        self.image = 'http://ifetch.rocks/manual/images/BasicLight.png'
        self.uuid = data['uuid']
        self.network_in = get_connection_uuid_by_id(data, '373576006')
        self.value = 0
        self.network_manager = network_manager
        self.input_networks = [self.network_in]
        self.output_networks = []
        self.input_power_networks = [get_connection_uuid_by_id(data, '-1270701682')]
        self.output_power_networks = []

        network_manager.get_network(self.network_in).register_listener(self._update)

    def _update(self, uuid: str, value: int):
        self.value = value
