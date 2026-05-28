"""
MultiplexSplitter type 124

/DATA_DISTRIBUTION/DATA_SPLITTERS/MULTIPLEX_SPLITTER  (SmallPacketSplitter.md)

"THE MULTIPLEX SPLITTER DUPLICATES THE SIGNAL FROM THE INPUT DATA PORT TO ALL
THE DATA OUTPUT PORTS."

Duplicates a large (32-channel) cable to multiple large cable outputs.

Port keys (confirmed from save 102d6094, 2026-03-21):
  '1735049622'   → large data IN  (type 4)
  '-1788018522'  → large data OUT 0 (type 4)
  '-441524197'   → large data OUT 1 (type 4)
"""
from typing import List
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class MultiplexSplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 124
        self.name = 'Multiplex Splitter'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/SmallPacketSplitter.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self.large_in   = get_connection_uuid_by_id(data, '1735049622')
        self.large_out0 = get_connection_uuid_by_id(data, '-1788018522')
        self.large_out1 = get_connection_uuid_by_id(data, '-441524197')

        self.value: List[int] = [0] * 32
        self.input_networks = []
        self.output_networks = []

        network_manager.get_large_network(self.large_in).register_listener(self._update)

    def _update(self, uuid: str, value: List[int]):
        if self.value != value:
            self.value = list(value)
            self.network_manager.get_large_network(self.large_out0).update_source(self.uuid, self.value)
            self.network_manager.get_large_network(self.large_out1).update_source(self.uuid, self.value)
