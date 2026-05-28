from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import build_network_in, build_network_out, \
    build_power_network_in, build_large_network_in, build_large_network_out, build_power_out, build_large_power_out, \
    graph_mappings, register_listeners

"""
THE ADD MODULE TAKES TWO 16-BIT VALUES, ADDS THEM TOGETHER AND OUTPUTS THEM AS A SINGLE 16-BIT VALUE.

E.G 1 + 1 = 2

IF THE RESULT IS GREATER THE MAXIMUM VALUE SUPPORTED OF 65535, THE RESULT WILL WRAP AROUND FROM 0.

E.G. 65535 + 1 = 0
E.G. 65535 + 2 = 1
"""

class Add:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        # ----- Non Changing -----
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        # ----- Set for the device -----
        self.type = 110
        self.name = 'Add'
        self.image = 'http://ifetch.rocks/manual/images/DeviceArithmeticAdd.png'
        self.value = data['signalValue']

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
        new_value = (self.network_in_data['2034020425']['value'] + self.network_in_data['1173709222']['value']) % 65536
        if self.value != new_value:
            self.value = new_value
            self.network_manager.get_network(self.network_out_data['-1790705161']['uuid']).update_source(self.uuid, self.value)


