from ifetchrocks_sim import _drive_loader
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class MemoryBaySignal:
    """
    /DATA_PROCESSING/MEMORY/MEMORY_BAY_SIGNAL

    The Raw Memory Bay stores up to 65536 16-bit values on an inserted Memory
    Drive, indexed 0–65535. (Developer extended range to full 16-bit; the
    in-game manual still shows the old 1024-word limit.)

    Save-file type IDs:
        141  — empty bay (no drive inserted). Port keys for this state are
               tentative; wiring an empty bay has no functional effect.
        153  — bay with Drive A inserted (FUNCTIONAL). All port keys below
               are confirmed via controlled probe-component reverse-engineering
               (save file 102d6094, FourBitSwitch×4 probe + room ordering,
               2026-03-20).

    Ports for type 153 (all data wires, type 5 in save file):
        PORT_INPUT   (-723312417)   — data to write          [toggle 0, confirmed]
        PORT_W_INDEX (937671010)    — write address 0–65535  [toggle 1, confirmed]
        PORT_WRITE   (1266942261)   — write trigger (nonzero=write) [toggle 2, confirmed]
        PORT_O_INDEX (-1305286718)  — read address 0–65535   [toggle 3, confirmed]
        PORT_OUTPUT  (1892577010)   — drive[O-Index] output  [confirmed]

    Additional children (type 153):
        DRIVE_SLOT (-606208362)  — any drive variant (A=139/B=156/C=157/D=158/E=159);
                                    same key regardless of which drive is inserted.
        POWER_PORT (1096989087)  — type-3 power input

    Drive write-protect switch (IDD key 1376775829, same for all drive variants A–E):
        signal == 0   → write-enabled (switch LEFT  / default position)
        signal != 0   → read-only     (switch RIGHT / write-protected, e.g. 65535)

    Confirmed with Drive A (type=153 bay) and Drive D (type=158 in same type=153
    bay). Same slot key -606208362 accepts all variants.
    """

    # All port IDs confirmed for type 153 (bay + any drive variant)
    PORT_INPUT   = '-723312417'
    PORT_W_INDEX = '937671010'
    PORT_WRITE   = '1266942261'
    PORT_O_INDEX = '-1305286718'
    PORT_OUTPUT  = '1892577010'

    DRIVE_SLOT = '-606208362'  # any drive variant (139/156/157/158/159); same key for all
    POWER_PORT = '1096989087'  # type-3 power input; not used in simulation logic

    # IDD key shared by all drive variants (A=139, B=156, C=157, D=158, E=159).
    # signal==0  → write-enabled (switch LEFT  / default position).
    # signal!=0  → read-only    (switch RIGHT / write-protected, e.g. 65535).
    IDD_WRITE_SWITCH = '1376775829'

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.uuid = data['uuid']
        self.network_manager = network_manager

        # Internal 65536-word store (full 16-bit address space).
        # Initialised from the Drive A .bin file when the bay has a drive with a payload UUID.
        self._memory = [0] * 65536
        drive_a_child = data.get('indexedChildren', {}).get(self.DRIVE_SLOT)

        # Read write-protect state from the inserted drive's IDD switch.
        # signal==0 → write-enabled (left position); signal!=0 → read-only (right position).
        self._read_only = True
        if drive_a_child:
            idd = drive_a_child.get('indexedDeviceData') or {}
            switch = idd.get(self.IDD_WRITE_SWITCH) or {}
            self._read_only = (switch.get('signal', 0) != 0)
            if drive_a_child.get('payload'):
                self._load_from_drive(drive_a_child['payload'])

        self._in_data    = 0
        self._in_w_index = 0
        self._in_write   = 0
        self._in_o_index = 0

        self.network_out      = get_connection_uuid_by_id(data, self.PORT_OUTPUT)
        self.network_in_data  = get_connection_uuid_by_id(data, self.PORT_INPUT)
        self.network_w_index  = get_connection_uuid_by_id(data, self.PORT_W_INDEX)
        self.network_write    = get_connection_uuid_by_id(data, self.PORT_WRITE)
        self.network_o_index  = get_connection_uuid_by_id(data, self.PORT_O_INDEX)

        self.input_networks  = [
            self.network_in_data,
            self.network_w_index,
            self.network_write,
            self.network_o_index,
        ]
        self.output_networks = [self.network_out]

        if self.network_in_data:
            network_manager.get_network(self.network_in_data).register_listener(self._on_input)
        if self.network_w_index:
            network_manager.get_network(self.network_w_index).register_listener(self._on_w_index)
        if self.network_write:
            network_manager.get_network(self.network_write).register_listener(self._on_write)
        if self.network_o_index:
            network_manager.get_network(self.network_o_index).register_listener(self._on_o_index)

    # ------------------------------------------------------------------
    # Listeners
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Drive initialisation
    # ------------------------------------------------------------------

    def _load_from_drive(self, payload_uuid: str):
        """Load drive contents into _memory from a .bin payload UUID.

        Prefers MemDrive (from ifetchrocks.cpu) when available so that
        MemDrive.save_dir overrides (e.g. in tests) are respected.
        Falls back to _drive_loader for standalone use.
        """
        try:
            from ifetchrocks.cpu.programmer.memory_drive import MemDrive
            drive = MemDrive()
            drive.load(payload_uuid)
            self._memory = [drive.read(index=i) for i in range(65536)]
        except ImportError:
            self._memory = _drive_loader.load_drive_words(payload_uuid)

    def _on_input(self, uuid: str, value: int):
        self._in_data = value & 0xFFFF

    def _on_w_index(self, uuid: str, value: int):
        self._in_w_index = value & 0xFFFF  # 16-bit address (0–65535)

    def _on_write(self, uuid: str, value: int):
        if value and not self._read_only:
            self._memory[self._in_w_index] = self._in_data
        self.update_and_notify()

    def _on_o_index(self, uuid: str, value: int):
        self._in_o_index = value & 0xFFFF  # 16-bit address (0–65535)
        self.update_and_notify()

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def update_and_notify(self):
        out = self._memory[self._in_o_index]
        if self.network_out:
            self.network_manager.get_network(self.network_out).update_source(self.uuid, out)
