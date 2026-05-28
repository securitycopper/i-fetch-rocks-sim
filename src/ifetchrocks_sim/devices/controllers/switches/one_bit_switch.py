from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_device_data_by_id, get_connection_uuid_by_id

PORT_OUTPUT = '245567209'   # confirmed 2026-03-22: type=215 → VD data input port

# Single idd key encoding the toggle state.
# rotation.y > 0  →  switch ON  →  output 1
# rotation.y ≤ 0  →  switch OFF →  output 0
# OFF state: rot.y = -0.258819,  signal = 0      (confirmed 2026-03-22)
# ON  state: rot.y = +0.258819,  signal = 65535  (confirmed 2026-03-22)
_IDD_KEY = '-1426717297'


class OneBitSwitch:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = '1 Bit Switch'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/BitSwitch1.png'
        self.uuid = data['uuid']
        self.network_out = get_connection_uuid_by_id(data, PORT_OUTPUT)
        self.network_manager = network_manager

        idd = get_device_data_by_id(data, _IDD_KEY)
        self.value = 1 if idd.get('rotation', {}).get('y', 0) > 0 else 0

        self.notify()
        self.input_networks = []
        self.output_networks = [self.network_out]

    def set_value(self, value: int):
        if self.value != value:
            self.value = value
            self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
