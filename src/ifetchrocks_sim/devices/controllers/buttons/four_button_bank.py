from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

# Physical order left→right: button 3 (VD_3), button 2, button 1, button 0 (VD_0)
# Confirmed 2026-03-24: all 4 outputs wired to VD_0–VD_3, buttons released (0000)
PORT_OUTPUT_0 = '508190823'    # rightmost button output — confirmed 2026-03-24
PORT_OUTPUT_1 = '-1550188168'  # 2nd from right output — confirmed 2026-03-24
PORT_OUTPUT_2 = '-703635148'   # 2nd from left output — confirmed 2026-03-24
PORT_OUTPUT_3 = '-1135664085'  # leftmost button output — confirmed 2026-03-24

_OUTPUT_KEYS = [PORT_OUTPUT_0, PORT_OUTPUT_1, PORT_OUTPUT_2, PORT_OUTPUT_3]

MAX_INT = 65535


class FourButtonBank:
    """4-button momentary bank. Each button outputs 65535 when held, 0 when released."""

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = '4 Button Bank'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceButtonBankShort.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self._networks = [
            get_connection_uuid_by_id(data, key) for key in _OUTPUT_KEYS
        ]
        # Buttons are momentary — always start at 0 regardless of save state
        self._values = [0, 0, 0, 0]

        self.input_networks = []
        self.output_networks = list(self._networks)
        self.notify()

    def press_with_value(self, index: int, value: int):
        """Drive button `index` (0=rightmost) with `value`. Use 65535 for pressed, 0 for released."""
        if self._values[index] != value:
            self._values[index] = value
            net = self._networks[index]
            self.network_manager.get_network(net).update_source(self.uuid, value)

    def notify(self):
        for net, value in zip(self._networks, self._values):
            self.network_manager.get_network(net).update_source(self.uuid, value)
