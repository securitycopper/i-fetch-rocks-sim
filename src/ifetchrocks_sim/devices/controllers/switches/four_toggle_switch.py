from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_device_data_by_id, get_connection_uuid_by_id

PORT_OUTPUT_0 = '245567209'   # toggle 0 → VD_0
PORT_OUTPUT_1 = '-524987108'  # toggle 1 → VD_1
PORT_OUTPUT_2 = '1831607210'  # toggle 2 → VD_2
PORT_OUTPUT_3 = '1502427632'  # toggle 3 → VD_3

# Physical order left→right: VD_3, VD_2, VD_1, VD_0 (confirmed 2026-03-24: switch "0001" → VD_0 ON)
# IDD key order matches physical right→left (index 0 = rightmost = VD_0)
_IDD_KEYS = ['-1941741643', '-1981437778', '-74374117', '-1426717297']
_OUTPUT_KEYS = [PORT_OUTPUT_0, PORT_OUTPUT_1, PORT_OUTPUT_2, PORT_OUTPUT_3]

MAX_INT = 65535


def _toggle_is_on(idd_entry: dict) -> bool:
    return idd_entry.get('rotation', {}).get('y', 0) > 0


class FourToggleSwitch:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = '4 Toggle Switch'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/SmallToggleSwitches.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        # resolve the four output network UUIDs (None-safe)
        self._networks = [get_connection_uuid_by_id(data, key) for key in _OUTPUT_KEYS]

        # compute initial values from indexedDeviceData
        self._values = [
            MAX_INT if _toggle_is_on(get_device_data_by_id(data, idd_key)) else 0
            for idd_key in _IDD_KEYS
        ]

        self.input_networks = []
        self.output_networks = list(self._networks)

        # register this device as a source on each output network
        for net in self._networks:
            self.network_manager.get_network(net).register_source(self.uuid)

        # push initial values
        self.notify()

    def set_toggle(self, index: int, on: bool):
        """Set toggle `index` (0–3) on or off. Drives output with 65535 (ON) or 0 (OFF)."""
        if index < 0 or index > 3:
            raise IndexError('toggle index out of range')
        value = MAX_INT if on else 0
        if self._values[index] != value:
            self._values[index] = value
            net = self._networks[index]
            self.network_manager.get_network(net).update_source(self.uuid, value)

    def notify(self):
        for i, (net, value) in enumerate(zip(self._networks, self._values)):
            self.network_manager.get_network(net).update_source(self.uuid, value)
