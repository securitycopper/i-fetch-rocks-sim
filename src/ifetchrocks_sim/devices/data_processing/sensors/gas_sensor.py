from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import build_network_out, graph_mappings


class GasSensor:

    PORT_CO = '375148252'
    PORT_O2 = '1560142200'
    PORT_CO2 = '8765768'

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        self.name = 'Gas Sensor'
        self.image = 'http://ifetch.rocks/manual/images/DeviceGasMeter.png'

        # No inputs for this passive sensor
        self.network_in_data = {}
        self.large_network_in_data = {}
        self.power_in_data = {}
        self.large_power_in_data = {}
        self.input_networks = []
        self.input_networks_labels = []

        # Outputs: CO, O2, CO2
        self.network_out_data = build_network_out(
            network_manager=network_manager,
            data=data,
            network_in_descriptions={
                self.PORT_CO: 'CO',
                self.PORT_O2: 'O2',
                self.PORT_CO2: 'CO2',
            }
        )

        # Other out-data slots (empty)
        self.large_network_out_data = {}
        self.power_out_data = {}
        self.large_power_out_data = {}

        # Populate output_networks and labels
        graph_mappings(self)
