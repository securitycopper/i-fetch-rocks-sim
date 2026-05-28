from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

"""
LogicalMux (type 134)
/DATA_PROCESSING/LOGIC/MUX_GATE

Selects between IN_TRUE and IN_FALSE based on the MUX signal.
If MUX > 0 (true), output = 1 if IN_TRUE > 0 else 0.
If MUX == 0 (false), output = 1 if IN_FALSE > 0 else 0.
Output is always 0 or 1.

Port IDs confirmed from save 102d6094, 2026-03-23:
  IN_TRUE  = '-1305286718'  (index 0, FBS probe A stored=0)
  IN_MUX   = '-108496386'   (index 1, FBS probe C stored=1)
  IN_FALSE = '-1907579157'  (index 2, FBS probe B stored=2)
  OUT      =  '835233603'   (index 3, ValueDisplay shows 0)
  Verification: mux=1 (true) → selects in_true=0 → output=0 ✓
"""

PORT_IN_TRUE  = '-1305286718'
PORT_IN_MUX   = '-108496386'
PORT_IN_FALSE = '-1907579157'
PORT_OUT      = '835233603'


class LogicalMux:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 134
        self.name = 'Logical Mux Gate'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/LogicalMux.png'
        self.uuid = data['uuid']

        self.network_in_true  = get_connection_uuid_by_id(data, PORT_IN_TRUE)
        self.network_in_mux   = get_connection_uuid_by_id(data, PORT_IN_MUX)
        self.network_in_false = get_connection_uuid_by_id(data, PORT_IN_FALSE)
        self.network_out      = get_connection_uuid_by_id(data, PORT_OUT)

        self.in_true  = 0
        self.in_mux   = 0
        self.in_false = 0
        self.value = data['signalValue']

        self.network_manager = network_manager
        self.input_networks  = [self.network_in_true, self.network_in_mux, self.network_in_false]
        self.output_networks = [self.network_out]

        network_manager.get_network(self.network_in_true).register_listener(self._update_in_true)
        network_manager.get_network(self.network_in_mux).register_listener(self._update_in_mux)
        network_manager.get_network(self.network_in_false).register_listener(self._update_in_false)

    def _update_in_true(self, uuid: str, value: int):
        self.in_true = value
        self._compute()

    def _update_in_mux(self, uuid: str, value: int):
        self.in_mux = value
        self._compute()

    def _update_in_false(self, uuid: str, value: int):
        self.in_false = value
        self._compute()

    def _compute(self):
        selected = self.in_true if self.in_mux else self.in_false
        self.value = 1 if selected else 0
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
