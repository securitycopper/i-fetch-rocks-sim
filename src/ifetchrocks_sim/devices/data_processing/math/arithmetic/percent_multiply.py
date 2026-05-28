from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import build_network_in, build_network_out, \
    build_power_network_in, build_large_network_in, build_large_network_out, build_power_out, build_large_power_out, \
    graph_mappings, register_listeners

"""
THE PERCENT MULTIPLY MODULE MULTIPLIES THE INPUT 16-BIT VALUE BY THE SELECTED
DIAL PERCENTAGE.

  dial signal 0     → 0%   (output = 0)
  dial signal 32767 → 50%  (output ≈ input / 2)
  dial signal 65535 → 100% (output = input)

Type: 101
Port IDs confirmed via in-game placement (2026-03-21):
  input  = 1460597191
  output = 508122447
DevData key for dial percentage:
  403658653  (signal 0–65535, where 65535 = 100%)
"""

class PercentMultiply:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        self.type = 101
        self.name = 'PercentMultiply'
        self.image = 'http://ifetch.rocks/manual/images/PercentMultiplier.png'
        self.value = data['signalValue']

        # Dial percentage stored in indexedDeviceData
        idd = data.get('indexedDeviceData') or {}
        dial_entry = idd.get('403658653') or {}
        self._dial = dial_entry.get('signal', 0)

        self.network_in_data = build_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
            '1460597191': 'input',
        })
        self.large_network_in_data = build_large_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={})
        self.power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={})
        self.large_power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={})

        self.network_out_data = build_network_out(network_manager=network_manager, data=data, network_in_descriptions={
            '508122447': 'output',
        })
        self.large_network_out_data = build_large_network_out(network_manager=network_manager, data=data, network_in_descriptions={})
        self.power_out_data = build_power_out(network_manager=network_manager, data=data, network_in_descriptions={})
        self.large_power_out_data = build_large_power_out(network_manager=network_manager, data=data, network_in_descriptions={})

        register_listeners(network_manager=network_manager, network_in_data=self.network_in_data,
                           large_network_in_data=self.large_network_in_data, power_in_data=self.power_in_data,
                           large_power_in_data=self.large_power_in_data)

        graph_mappings(self)

    def change_event(self, component_id: str, value: int):
        inp = self.network_in_data['1460597191']['value']
        new_value = int(round(inp * self._dial / 65535)) % 65536 if self._dial > 0 else 0
        if self.value != new_value:
            self.value = new_value
            self.network_manager.get_network(self.network_out_data['508122447']['uuid']).update_source(self.uuid, self.value)
