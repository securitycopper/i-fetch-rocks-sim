"""
LargeConduit type 64

/DATA_DISTRIBUTION/DATA_CONDUITS/LARGE_CONDUIT  (DeviceLongLargeDataSplitter.md)

"THE LARGE CONDUIT IS FOR LARGE DATA CABLES. IT ALLOWS LARGE DATA CABLES TO BE
EXTENDED BEYOND THEIR MAXIMUM LENGTH."

Simple large-cable pass-through.

Port keys (confirmed from save 102d6094, 2026-03-21):
  '1744147728'  → large data IN  (type 4)
  '151064311'   → large data OUT (type 4)
"""
from typing import List
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class LargeConduit:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 64
        self.name = 'Large Conduit'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceLongLargeDataSplitter.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self.large_in  = get_connection_uuid_by_id(data, '1744147728')
        self.large_out = get_connection_uuid_by_id(data, '151064311')

        self.value: List[int] = [0] * 32
        self.input_networks = []
        self.output_networks = []

        network_manager.get_large_network(self.large_in).register_listener(self._update)

    def _update(self, uuid: str, value: List[int]):
        if self.value != value:
            self.value = list(value)
            self.network_manager.get_large_network(self.large_out).update_source(self.uuid, self.value)
