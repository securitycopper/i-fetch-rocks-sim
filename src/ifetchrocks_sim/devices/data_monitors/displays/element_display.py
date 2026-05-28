from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class ElementDisplay:
    """
    /DATA_MONITORS/DISPLAYS/ELEMENT_DISPLAY (type 72)

    Passthrough display: stores 16-bit value and echoes it to an output network.
    Ports:
      PORT_INPUT  = '1878156136'  # 16-bit signal input
      PORT_OUTPUT = '-1899773318' # passthrough output
      PORT_POWER  = '-1409524763' # power input (ignored)
    """

    PORT_INPUT = '1878156136'
    PORT_OUTPUT = '-1899773318'
    PORT_POWER = '-1409524763'

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 72
        self.name = 'Element Display'
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
        network_manager.get_network(self.network_in).register_listener(self._on_input)

    def _on_input(self, uuid: str, value: int):
        # keep only 16-bit value
        self.value = value & 0xFFFF
        if self.network_out:
            # echo value as a source on the output network
            self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
