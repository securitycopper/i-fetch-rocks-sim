from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class DriveCartridge:
    """Passive drive cartridge inserted into a MemoryBaySignal or MemoryBayVector.

    Save-file type IDs:
        139 — Drive A (microcode ROM: control signals)
        156 — Drive B (ALU signals ROM)
        157 — Drive C (program ROM)
        158 — Drive D (general purpose)
        159 — Drive E (general purpose)

    Drives have **no wire ports** of their own — all I/O is handled by the
    parent bay (type 153/154) which reads the drive's binary payload via
    the DRIVE_SLOT key.  This class exists so drives appear in the simulator
    device graph instead of being silently dropped during load.
    """

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self.input_networks = []
        self.output_networks = []
        self.input_power_networks = []
        self.large_input_networks = []
        self.large_input_power_networks = []

        self.payload_uuid = data.get('payload')
        self.value = data.get('signalValue', 0)
