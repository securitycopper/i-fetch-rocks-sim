from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import build_network_in, build_network_out, \
    build_power_network_in, build_large_network_in, build_large_network_out, build_power_out, build_large_power_out, \
    graph_mappings, register_listeners

"""
THE LERP MODULE OUTPUTS A VALUE THAT IS LINEARLY INTERPOLATED BETWEEN THE INPUT
VALUES A AND B.

LERP VALUE OF 0, OUTPUT IS 'A'.
LERP VALUE OF 32767, OUTPUT IS HALF WAY BETWEEN 'A' AND 'B'.
LERP VALUE OF 65535, OUTPUT IS 'B'.

Type: 196
Port IDs confirmed via in-game placement (2026-03-21):
  A       = 2034020425
  B       = 1173709222
  lerp    = 1822231271
  out     = -1790705161
"""

class Lerp:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        self.type = 196
        self.name = 'Lerp'
        self.image = 'http://ifetch.rocks/manual/images/LinearSignalInterpolation.png'
        self.value = data['signalValue']

        self.network_in_data = build_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
            '2034020425': 'A',
            '1173709222': 'B',
            '1822231271': 'lerp',
        })
        self.large_network_in_data = build_large_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={})
        self.power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={})
        self.large_power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={})

        self.network_out_data = build_network_out(network_manager=network_manager, data=data, network_in_descriptions={
            '-1790705161': 'out',
        })
        self.large_network_out_data = build_large_network_out(network_manager=network_manager, data=data, network_in_descriptions={})
        self.power_out_data = build_power_out(network_manager=network_manager, data=data, network_in_descriptions={})
        self.large_power_out_data = build_large_power_out(network_manager=network_manager, data=data, network_in_descriptions={})

        register_listeners(network_manager=network_manager, network_in_data=self.network_in_data,
                           large_network_in_data=self.large_network_in_data, power_in_data=self.power_in_data,
                           large_power_in_data=self.large_power_in_data)

        graph_mappings(self)

    def change_event(self, component_id: str, value: int):
        a = self.network_in_data['2034020425']['value']
        b = self.network_in_data['1173709222']['value']
        t = self.network_in_data['1822231271']['value']
        new_value = int(round(a + (b - a) * t / 65535)) % 65536
        if self.value != new_value:
            self.value = new_value
            self.network_manager.get_network(self.network_out_data['-1790705161']['uuid']).update_source(self.uuid, self.value)
