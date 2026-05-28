from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_device_data_by_id, get_connection_uuid_by_id

PORT_OUTPUT = '1420098671'  # confirmed 2026-03-22

# idd keys in MSB-to-LSB order (bit 128 … bit 1)
# All keys confirmed individually via single-switch → ValueDisplay probe, 2026-03-22/2026-03-26
# State: signal != 0  →  switch ON (rotation.y > 0 also indicates ON)
_BIT_KEYS = [
    ('1718803965',  128),  # confirmed: switch 128 only → output 128
    ('-49703703',    64),  # confirmed: switch 64 only  → output 64
    ('1509656464',   32),  # confirmed: switch 32 only  → output 32
    ('-120397473',   16),  # confirmed: switch 16 only  → output 16
    ('1085911864',    8),  # confirmed: switch 8 only   → output 8
    ('716941455',     4),  # confirmed: switch 4 only   → output 4
    ('692338407',     2),  # confirmed: switch 2 only   → output 2
    ('55203747',      1),  # confirmed: switch 1 only   → output 1
]


class EightBitSwitch:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = '8 Bit Switch'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceSwitchBankLong.png'
        self.uuid = data['uuid']
        self.network_out = get_connection_uuid_by_id(data, PORT_OUTPUT)
        self.network_manager = network_manager

        self._bits = {
            key: bool(get_device_data_by_id(data, key).get('signal', 0))
            for key, _ in _BIT_KEYS
        }

        self.value = 0
        self.notify()
        self.input_networks = []
        self.output_networks = [self.network_out]

    def notify(self):
        value = 0
        for key, bit_value in _BIT_KEYS:
            if self._bits[key]:
                value |= bit_value
        self.value = value
        self.network_manager.get_network(self.network_out).update_source(self.uuid, value)
