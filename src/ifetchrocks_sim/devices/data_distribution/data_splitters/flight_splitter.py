"""
FlightSplitter type 66

/DATA_DISTRIBUTION/DATA_SPLITTERS/FLIGHT_SPLITTER  (DeviceFlightPacketSplitter.md)

"THE FLIGHT SPLITTER SPLITS THE SIGNAL FROM A LARGE DATA CABLE TO MULTIPLE
SMALL CABLES (FROM CHANNELS 0 - 13)"

In practice (CPU save observation) it outputs 16 small channels. Also passes
the large cable through for daisy-chaining.

Port keys (confirmed from CPU save d88a1650, 2026-03-21):
  '895526837'    → large data IN  (type 4)
  '-914343343'   → large data chain OUT (type 4) — for daisy-chaining
  Small channel outputs (type 5) — channel→port mapping is a TODO (see below):

# TODO: The channel index assigned to each port key below is a PLACEHOLDER.
# Run a verification placement test: feed a large cable with a single known
# channel value set (e.g. channel 3 = 12345, all others 0) and observe which
# small output fires to establish the correct mapping.
"""
from typing import List
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

# Sorted by port-key integer value, assigned indices 0-15.
# *** CHANNEL ASSIGNMENT NOT VERIFIED — needs in-game placement test ***
_CHANNEL_PORT_KEYS = [
    '-1695714870',   # placeholder ch 0
    '-1315024675',   # placeholder ch 1
    '-1246123637',   # placeholder ch 2
    '-891580525',    # placeholder ch 3
    '-778304202',    # placeholder ch 4
    '-521040181',    # placeholder ch 5
    '-267220172',    # placeholder ch 6
    '-265622494',    # placeholder ch 7
    '137833267',     # placeholder ch 8
    '1201653466',    # placeholder ch 9
    '1270273247',    # placeholder ch 10
    '1522655891',    # placeholder ch 11
    '1607793870',    # placeholder ch 12
    '1666339311',    # placeholder ch 13
    '1885335009',    # placeholder ch 14
    '2109370624',    # placeholder ch 15
]


class FlightSplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 66
        self.name = 'Flight Splitter'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceFlightPacketSplitter.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self.large_in       = get_connection_uuid_by_id(data, '895526837')
        self.large_chain_out = get_connection_uuid_by_id(data, '-914343343')

        # Map port_key → (wire_uuid, channel_index)
        self._channel_outs = {}
        for ch_idx, pk in enumerate(_CHANNEL_PORT_KEYS):
            wire_uuid = get_connection_uuid_by_id(data, pk)
            self._channel_outs[pk] = (wire_uuid, ch_idx)

        self.value: List[int] = [0] * 32
        self.input_networks = []
        self.output_networks = []

        network_manager.get_large_network(self.large_in).register_listener(self._update)

    def _update(self, uuid: str, value: List[int]):
        if self.value != value:
            self.value = list(value)
            # Pass large cable through for chaining
            self.network_manager.get_large_network(self.large_chain_out).update_source(
                self.uuid, self.value
            )
            # Distribute individual channels to small outputs
            for wire_uuid, ch_idx in self._channel_outs.values():
                ch_val = self.value[ch_idx] if ch_idx < len(self.value) else 0
                self.network_manager.get_network(wire_uuid).update_source(self.uuid, ch_val)
