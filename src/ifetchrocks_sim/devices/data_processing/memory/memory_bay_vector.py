from typing import List

from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class MemoryBayVector:
    """
    /DATA_PROCESSING/MEMORY/MEMORY_BAY_VECTOR

    The Vector Memory Bay stores up to 65536 8-channel vectors on an inserted
    Memory Drive.  Each address holds 8 × 16-bit values.

    Save-file type ID:
        154  — bay with any drive variant inserted (FUNCTIONAL). All port keys
               below are confirmed via controlled probe-component
               reverse-engineering (save file 102d6094, VectorMerger wiring
               confirmation, 2026-03-24).

    Ports for type 154:
        PORT_W_INDEX   ( 937671010)  — write address 0–65535  [IN_0, confirmed]
        PORT_WRITE     (1266942261)  — write trigger (nonzero→write) [IN_1, confirmed]
        PORT_O_INDEX   (-1305286718) — read address 0–65535   [IN_2, confirmed]
        PORT_VECTOR_IN (1246405330)  — 8-channel vector input  (type-142 vector cable)
        PORT_VECTOR_OUT(-1078517178) — 8-channel vector output (type-142 vector cable;
                                       confirmed by connecting to VectorMerger input)

    Additional children (type 154):
        DRIVE_SLOT (-606208362)  — any drive variant (A–E); same key as MemoryBaySignal.
        POWER_PORT (1096989087)  — type-3 power input.

    Drive write-protect switch (IDD key 1376775829, shared by all drive variants):
        signal == 0   → write-enabled (switch LEFT  / default position)
        signal != 0   → read-only     (switch RIGHT / write-protected, e.g. 65535)

    Vector I/O uses the large-data-network bus (get_large_network).  Although
    LargeDataNetwork internally carries 32-element lists, MemoryBayVector stores
    only the first VECTOR_WIDTH(=8) channels per address and pads outputs to 32
    elements when emitting (channels 8–31 set to 0).
    """

    DRIVE_SLOT        = '-606208362'   # any drive variant (139/156/157/158/159)
    POWER_PORT        = '1096989087'   # type-3 power input; not used in simulation logic

    PORT_W_INDEX      = '937671010'    # write address
    PORT_WRITE        = '1266942261'   # write trigger
    PORT_O_INDEX      = '-1305286718'  # read address
    PORT_VECTOR_IN    = '1246405330'   # 8-channel vector cable input
    PORT_VECTOR_OUT   = '-1078517178'  # 8-channel vector cable output

    # IDD key shared by all drive variants (A=139, B=156, C=157, D=158, E=159).
    # signal==0  → write-enabled (switch LEFT  / default position).
    # signal!=0  → read-only    (switch RIGHT / write-protected, e.g. 65535).
    IDD_WRITE_SWITCH  = '1376775829'

    VECTOR_WIDTH      = 8              # channels per address
    _LARGE_NET_WIDTH  = 32             # LargeDataNetwork always uses 32-element lists

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.uuid = data['uuid']
        self.network_manager = network_manager

        # Internal store: 65536 addresses, each holding VECTOR_WIDTH 16-bit values.
        self._memory: List[List[int]] = [[0] * self.VECTOR_WIDTH for _ in range(65536)]

        drive_child = data.get('indexedChildren', {}).get(self.DRIVE_SLOT)

        # Read write-protect state from the inserted drive's IDD switch.
        self._read_only = True
        if drive_child:
            idd = drive_child.get('indexedDeviceData') or {}
            switch = idd.get(self.IDD_WRITE_SWITCH) or {}
            self._read_only = (switch.get('signal', 0) != 0)

        self._in_vector  = [0] * self.VECTOR_WIDTH
        self._in_w_index = 0
        self._in_write   = 0
        self._in_o_index = 0

        # Scalar inputs (shared port IDs with MemoryBaySignal)
        self.network_w_index = get_connection_uuid_by_id(data, self.PORT_W_INDEX)
        self.network_write   = get_connection_uuid_by_id(data, self.PORT_WRITE)
        self.network_o_index = get_connection_uuid_by_id(data, self.PORT_O_INDEX)

        # Large-network I/O (type-142 vector cables)
        self.large_network_in_uuid  = get_connection_uuid_by_id(data, self.PORT_VECTOR_IN)
        self.large_network_out_uuid = get_connection_uuid_by_id(data, self.PORT_VECTOR_OUT)

        # Power port (type-3 power cable; not used in simulation logic but
        # exposed so _generate_missing_connections can build the graph node).
        # get_connection_uuid_by_id always returns a UUID (auto-generated if absent)
        # so these lists always have exactly one element each.
        self.input_networks        = [
            self.network_w_index,
            self.network_write,
            self.network_o_index,
        ]
        self.output_networks       = []
        self.vector_input_networks  = [self.large_network_in_uuid]
        self.vector_output_networks = [self.large_network_out_uuid]
        self.input_power_networks  = [get_connection_uuid_by_id(data, self.POWER_PORT)]

        if self.network_w_index:
            network_manager.get_network(self.network_w_index).register_listener(self._on_w_index)
        if self.network_write:
            network_manager.get_network(self.network_write).register_listener(self._on_write)
        if self.network_o_index:
            network_manager.get_network(self.network_o_index).register_listener(self._on_o_index)

        if self.large_network_in_uuid:
            network_manager.get_large_network(self.large_network_in_uuid).register_listener(
                self._on_vector_in
            )
        if self.large_network_out_uuid:
            network_manager.get_large_network(self.large_network_out_uuid).register_source(
                self.uuid
            )

    # ------------------------------------------------------------------
    # Listeners
    # ------------------------------------------------------------------

    def _on_vector_in(self, uuid: str, value: List[int]):
        self._in_vector = [value[i] if i < len(value) else 0
                           for i in range(self.VECTOR_WIDTH)]

    def _on_w_index(self, uuid: str, value: int):
        self._in_w_index = value & 0xFFFF

    def _on_write(self, uuid: str, value: int):
        if value and not self._read_only:
            self._memory[self._in_w_index] = list(self._in_vector)
        self.update_and_notify()

    def _on_o_index(self, uuid: str, value: int):
        self._in_o_index = value & 0xFFFF
        self.update_and_notify()

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def update_and_notify(self):
        out = self._memory[self._in_o_index]
        if self.large_network_out_uuid:
            # Pad to 32 elements so LargeDataNetwork can OR with other sources safely.
            padded = out + [0] * (self._LARGE_NET_WIDTH - self.VECTOR_WIDTH)
            self.network_manager.get_large_network(self.large_network_out_uuid).update_source(
                self.uuid, padded
            )
