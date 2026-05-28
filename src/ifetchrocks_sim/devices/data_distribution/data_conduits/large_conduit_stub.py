"""
LargeConduitStub type 70

Placed in the room as a large cable extender but observed with no connected
ports across all tested saves (2026-03-21). Treated as a no-op stub until
port keys can be confirmed via a wired placement test.

Likely corresponds to a second large conduit form-factor
(LARGE_CONDUIT → DeviceLongLargeDataSplitter.md).
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class LargeConduitStub:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.type = 70
        self.name = 'Large Conduit (stub)'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceLongLargeDataSplitter.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager
        self.input_networks = []
        self.output_networks = []
