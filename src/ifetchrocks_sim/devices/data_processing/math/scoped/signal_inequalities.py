from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import build_network_in, build_network_out, \
    build_power_network_in, build_large_network_in, build_large_network_out, build_power_out, \
    build_large_power_out, graph_mappings, register_listeners

"""
THE INEQUALITIES EVALUATES THE INPUT SIGNAL AS GREATER THAN (>) OR LESS THAN (<) THE 16-BIT VALUE
BEING RECEIVED THROUGH THE RESPECTIVE PORT AND OUTPUTS A BOOLEAN (TRUE/FALSE) BINARY VALUE.

Output = 65535 (TRUE) if min(thresh_a, thresh_b) < signal < max(thresh_a, thresh_b), else 0.
The two threshold ports are interchangeable (symmetric bounds).

Port keys confirmed 2026-03-22 via FBS probe in RE save 102d6094:
  PORT_SIGNAL      = '1000035408'  signal input
  PORT_THRESHOLD_A = '1286147805'  first threshold  (interchangeable with B)
  PORT_THRESHOLD_B = '101010795'   second threshold (interchangeable with A)
  PORT_OUTPUT      = '-411018612'  boolean output

Test: signal=5,  a=3, b=7 → 65535  (3 < 5 < 7)
Test: signal=8,  a=3, b=7 → 0      (8 not in range)
Test: signal=3,  a=3, b=7 → 0      (strict lower bound)
Test: signal=7,  a=3, b=7 → 0      (strict upper bound)
Test: signal=5,  a=7, b=3 → 65535  (symmetric: min=3, 3 < 5 < 7)
"""

MAX_VALUE = 65535


class SignalInequalities:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        self.type = 102
        self.name = 'Signal Inequalities'
        self.image = 'http://ifetch.rocks/manual/images/SignalInequalities.png'
        self.value = data['signalValue']

        self.network_in_data = build_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event,
            network_in_descriptions={
                '1000035408': 'signal',
                '1286147805': 'lower_bound',
                '101010795':  'upper_bound',
            }
        )
        self.large_network_in_data = build_large_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={})
        self.power_in_data = build_power_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={})
        self.large_power_in_data = build_power_network_in(
            network_manager=network_manager, data=data,
            change_event=self.change_event, network_in_descriptions={})

        self.network_out_data = build_network_out(
            network_manager=network_manager, data=data,
            network_in_descriptions={'-411018612': 'output'})
        self.large_network_out_data = build_large_network_out(
            network_manager=network_manager, data=data, network_in_descriptions={})
        self.power_out_data = build_power_out(
            network_manager=network_manager, data=data, network_in_descriptions={})
        self.large_power_out_data = build_large_power_out(
            network_manager=network_manager, data=data, network_in_descriptions={})

        register_listeners(
            network_manager=network_manager,
            network_in_data=self.network_in_data,
            large_network_in_data=self.large_network_in_data,
            power_in_data=self.power_in_data,
            large_power_in_data=self.large_power_in_data,
        )
        graph_mappings(self)

    def change_event(self, component_id: str, value: int):
        signal  = self.network_in_data['1000035408']['value']
        thresh_a = self.network_in_data['1286147805']['value']
        thresh_b = self.network_in_data['101010795']['value']
        lower, upper = (thresh_a, thresh_b) if thresh_a <= thresh_b else (thresh_b, thresh_a)
        new_value = MAX_VALUE if (lower < signal < upper) else 0
        if self.value != new_value:
            self.value = new_value
            out_uuid = self.network_out_data['-411018612']['uuid']
            if out_uuid:
                self.network_manager.get_network(out_uuid).update_source(self.uuid, self.value)
