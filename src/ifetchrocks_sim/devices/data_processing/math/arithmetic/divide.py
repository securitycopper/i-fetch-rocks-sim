from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import build_network_in, build_network_out, \
    build_power_network_in, build_large_network_in, build_large_network_out, build_power_out, build_large_power_out, \
    graph_mappings, register_listeners, get_device_data_by_id

"""
THE DIVIDE MODULE TAKES TWO 16-BIT VALUES, DIVIDES THEM FROM EACH OTHER AND OUTPUTS THEM AS A SINGLE 16-BIT VALUE.

THE DEFAULT INTEGER MODE SIMPLY DIVIDES WHOLE NUMBERS.
E.G. 100 / 2 = 50

IN NORMALIZED FLOAT MODE, THE INPUTS ARE NORMALIZED TO FLOATING POINT VALUES BETWEEN 0 AND 1 AND THEN DIVIDED.
E.G. 26,214 (0.4) / 32,767 (0.5) = 52,428 (0.8)
"""
class Divide:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        # ----- Non Changing -----
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        # ----- Set for the device -----
        self.type = 112
        self.name = 'Arithmetic Divide'
        self.image = 'http://ifetch.rocks/manual/images/DeviceArithmeticDivide.png'
        self.value = data['signalValue']
        self.float = get_device_data_by_id(data, '-2139921001')['signal']

        # ----- Inputs -----
        self.network_in_data = build_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
            '2034020425': 'A',
            '1173709222': 'B'
        })
        self.large_network_in_data = build_large_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        self.power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        self.large_power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        # ----- Outputs -----
        self.network_out_data = build_network_out(network_manager=network_manager, data=data, network_in_descriptions={
            '-1790705161': 'out'
        })
        self.large_network_out_data = build_large_network_out(network_manager=network_manager, data=data, network_in_descriptions={
        })
        self.power_out_data = build_power_out(network_manager=network_manager, data=data, network_in_descriptions={
        })
        self.large_power_out_data = build_large_power_out(network_manager=network_manager, data=data, network_in_descriptions={
        })
        register_listeners(network_manager=network_manager, network_in_data=self.network_in_data,
                           large_network_in_data=self.large_network_in_data, power_in_data=self.power_in_data,
                           large_power_in_data=self.large_power_in_data)

        # ----- Graph Mappings -----
        graph_mappings(self)

    def change_event(self, component_id: str, value: int):
        if self.network_in_data['1173709222']['value'] == 0:
            return
        a = self.network_in_data['2034020425']['value']
        b = self.network_in_data['1173709222']['value']
        if self.float:  # Normalised float mode: inputs are 0–65535 mapped to 0.0–1.0
            new_value = int((a / 65535) / (b / 65535) * 65535) & 0xFFFF
        else:
            new_value = int(a / b) & 0xFFFF
        if self.value != new_value:
            self.value = new_value
            self.network_manager.get_network(self.network_out_data['-1790705161']['uuid']).update_source(self.uuid, self.value)


