"""
WirelessReceiver type 213

/DATA_DISTRIBUTION/WIRELESS/WIRELESS_RECEIVER  (Receiver.md)

"THIS WIRELESS MODULE CAN RECIEVE 32X 16BIT VALUES AT 50HZ ON A SINGLE
FREQUENCY BAND. USE THE TOGGLE SWITCHES TO SELECT FROM 15 DIFFERENT
FREQUENCY BANDS. NOTE: SELECTING FREQUENCY BAND 0 WILL PREVENT RECEPTION
AS THERE IS NO FREQUENCY BAND 0"

Port keys:
  '1369211778'  → power IN  (type 3) — inferred from WirelessTransmitter (same family)
  '-1790705161' → large data OUT (type 4) — inferred; no wired instance in any save

  Port keys are NOT confirmed from save data.  The only career-save instance
  (407f3f05) has null indexedChildren.  Keys below are best guesses based on
  the WirelessTransmitter (same device family).

Channel selection devData keys confirmed same as WirelessTransmitter (both are
4-toggle switch boards from the same device family).

Implementation: on each start-of-tick, reads wireless_channels[channel] from
the shared DataNetworkManager bus and pushes it to the large output network.
"""
from typing import List

from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

# Same switch key → bit mapping as WirelessTransmitter.
# All 4 channel-select bits confirmed (matches WirelessTransmitter).
_SWITCH_BIT_KEYS = {
    '-1426717297': 1,   # confirmed: test 8=0,4=0,2=0,1=1
    '-74374117':   2,   # confirmed: test 8=0,4=0,2=1,1=0
    '-1981437778': 4,   # confirmed: test 8=0,4=1,2=0,1=0
    '-1941741643': 8,   # confirmed: test 8=1,4=0,2=0,1=0
}

# Receiver port keys — UNCONFIRMED (no wired instance found in any save).
# Power key assumed same as WirelessTransmitter (same device family).
_POWER_IN  = '1369211778'
_LARGE_OUT = '-1790705161'


class WirelessReceiver:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 213
        self.name = 'Wireless Receiver'
        self.color = 'cyan'
        self.image = 'http://ifetch.rocks/manual/images/Receiver.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self._large_out_uuid = get_connection_uuid_by_id(data, _LARGE_OUT)
        self.value: List[int] = [0] * 32

        self.input_networks = []
        self.output_networks = []
        self.large_input_networks = []
        self.large_output_networks = [self._large_out_uuid]
        self.input_power_networks = [get_connection_uuid_by_id(data, _POWER_IN)]

        network_manager.register_start_of_tick_listener(self._start_of_tick)

    def _get_channel(self) -> int:
        dev_data = self.data.get('indexedDeviceData') or {}
        channel = 0
        for key, bit in _SWITCH_BIT_KEYS.items():
            entry = dev_data.get(key)
            if isinstance(entry, dict) and entry.get('signal', 0):
                channel += bit
        return channel

    def _start_of_tick(self):
        ch = self._get_channel()
        if ch <= 0:
            return
        incoming = self.network_manager.wireless_channels.get(ch)
        if incoming is not None and incoming != self.value:
            self.value = list(incoming)
            self.network_manager.get_large_network(self._large_out_uuid).update_source(
                self.uuid, self.value
            )
