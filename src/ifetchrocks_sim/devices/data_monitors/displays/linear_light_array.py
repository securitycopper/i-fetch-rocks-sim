from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class LinearLightArray:
    """
    /DATA_MONITORS/DISPLAYS/LINEAR_LIGHT_ARRAY (type 39)

    Passthrough display: stores 16-bit value and echoes it to an output network.
    Ports (confirmed 2026-03-23):
      PORT_INPUT  = '832364048'   # 16-bit signal input
      PORT_OUTPUT = '-1186727754' # passthrough output
      PORT_POWER  = '-1831826590' # power input (ignored)
    """

    PORT_INPUT = '832364048'
    PORT_OUTPUT = '-1186727754'
    PORT_POWER = '-1831826590'

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 39
        self.name = 'Linear Light Array'
        self.uuid = data['uuid']
        self.value = 0
        self.network_manager = network_manager

        self.network_in = get_connection_uuid_by_id(data, self.PORT_INPUT)
        self.network_out = get_connection_uuid_by_id(data, self.PORT_OUTPUT)

        self.input_networks = [self.network_in]
        self.output_networks = [self.network_out]
        self.input_power_networks = [get_connection_uuid_by_id(data, self.PORT_POWER)]
        self.output_power_networks = []

        # Register listener on input network (register_listener calls immediately)
        if self.network_in:
            network_manager.get_network(self.network_in).register_listener(self._on_input)

    def _on_input(self, uuid: str, value: int):
        # keep only 16-bit value
        self.value = value & 0xFFFF
        if self.network_out:
            # echo value as a source on the output network
            self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class LinearLightArray:
    """
    /DATA_MONITORS/DISPLAYS/LINEAR_LIGHT_ARRAY (type 39)

    Passthrough display: stores 16-bit value and echoes it to an output
    network. Behaviour: display a 16-bit value as a percentage of LEDs
    in the real device; in simulation it simply echoes the input value.
    """

    PORT_INPUT = '832364048'
    PORT_OUTPUT = '-1186727754'
    PORT_POWER = '-1831826590'

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 39
        self.name = 'Linear Light Array'
        self.uuid = data['uuid']
        self.value = 0
        self.network_manager = network_manager

        self.network_in = get_connection_uuid_by_id(data, self.PORT_INPUT)
        self.network_out = get_connection_uuid_by_id(data, self.PORT_OUTPUT)

        self.input_networks = [self.network_in]
        self.output_networks = [self.network_out]
        self.input_power_networks = [get_connection_uuid_by_id(data, self.PORT_POWER)]
        self.output_power_networks = []

        # Register listener on input network (register_listener calls immediately)
        if self.network_in:
            network_manager.get_network(self.network_in).register_listener(self._on_input)

    def _on_input(self, uuid: str, value: int):
        # keep only 16-bit value
        self.value = value & 0xFFFF
        if self.network_out:
            # echo value as a source on the output network
            self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
