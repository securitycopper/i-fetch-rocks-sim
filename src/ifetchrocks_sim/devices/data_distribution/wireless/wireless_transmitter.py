"""
WirelessTransmitter type 212

/DATA_DISTRIBUTION/WIRELESS/WIRELESS_TRANSMITTER  (Transmitter.md)

"THIS WIRELESS MODULE CAN TRANSMIT 32X 16BIT VALUES AT 50HZ ON A SINGLE
FREQUENCY BAND. USE THE TOGGLE SWITCHES TO SELECT FROM 15 DIFFERENT
FREQUENCY BANDS. NOTE: SELECTING FREQUENCY BAND 0 WILL PREVENT TRANSMISSION
AS THERE IS NO FREQUENCY BAND 0"

Port keys (confirmed from save 102d6094, 2026-03-21):
  '1369211778'  → power IN  (type 3)
  '1528177475'  → large data IN  (type 4)

devData switch keys — channel selection (4 binary toggles, channel = sum of ON bits):
  '-1426717297' = bit 1   (confirmed: signal=65535 on test 8=0,4=0,2=0,1=1)
  '-74374117'   = bit 2   (confirmed: signal=65535 on test 8=0,4=0,2=1,1=0)
  '-1981437778' = bit 4   (confirmed: signal=65535 on test 8=0,4=1,2=0,1=0)
  '-1941741643' = bit 8   (confirmed: signal=65535 on test 8=1,4=0,2=0,1=0)
"""
from typing import List

from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

# devData key -> bit contribution to channel number. All 4 bits confirmed.
_SWITCH_BIT_KEYS = {
    '-1426717297': 1,   # confirmed: test 8=0,4=0,2=0,1=1
    '-74374117':   2,   # confirmed: test 8=0,4=0,2=1,1=0
    '-1981437778': 4,   # confirmed: test 8=0,4=1,2=0,1=0
    '-1941741643': 8,   # confirmed: test 8=1,4=0,2=0,1=0
}

_POWER_IN  = '1369211778'
_LARGE_IN  = '1528177475'


class WirelessTransmitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 212
        self.name = 'Wireless Transmitter'
        self.color = 'cyan'
        self.image = 'http://ifetch.rocks/manual/images/Transmitter.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self._large_in_uuid = get_connection_uuid_by_id(data, _LARGE_IN)
        self._channel_value: List[int] = [0] * 32

        self.input_networks = []
        self.output_networks = []
        self.large_input_networks = [self._large_in_uuid]
        self.large_output_networks = []
        self.input_power_networks = [get_connection_uuid_by_id(data, _POWER_IN)]

        network_manager.get_large_network(self._large_in_uuid).register_listener(self._on_large_in)
        network_manager.register_end_of_tick_listener(self._end_of_tick)

    def _get_channel(self) -> int:
        dev_data = self.data.get('indexedDeviceData') or {}
        channel = 0
        for key, bit in _SWITCH_BIT_KEYS.items():
            entry = dev_data.get(key)
            if isinstance(entry, dict) and entry.get('signal', 0):
                channel += bit
        return channel

    def _on_large_in(self, uuid: str, value: List[int]):
        self._channel_value = list(value)

    def _end_of_tick(self):
        ch = self._get_channel()
        if ch > 0:
            self.network_manager.wireless_channels[ch] = list(self._channel_value)
