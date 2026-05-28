from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import build_network_in, build_network_out, \
    build_power_network_in, build_large_network_in, build_large_network_out, build_power_out, build_large_power_out, \
    graph_mappings, register_listeners, get_device_data_by_id


class ChannelSplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        # ----- Non Changing -----
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        # ----- Set for the device -----
        self.type = 62
        self.name = 'Multiplex Channel Splitter'
        self.image = 'http://ifetch.rocks/manual/images/DeviceLargePacketSplitter.png'
        self.value = get_device_data_by_id(data, '-1990565103')['signal']

        # ----- Inputs -----
        self.network_in_data = build_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        self.large_network_in_data = build_large_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
            '-998761478': 'IN'  #093f9306
        })
        self.power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        self.large_power_in_data = build_power_network_in(network_manager=network_manager, data=data, change_event=self.change_event, network_in_descriptions={
        })
        # ----- Outputs -----
        self.network_out_data = build_network_out(network_manager=network_manager, data=data, network_in_descriptions={
            # Tested
            '-107630999': '0',
            '861042355': '1',
            '-2052235901': '2',
            '1120134717': '3',
            '301432865': '4',
            '239612162': '5',
            '-1487357048': '6',
            '340890103': '7',

            # TODO: Not tested
            '1214051645': '10',  #
            '1719862820': '9',  #
            '23686105': '8',  #
            '745001653': '11',  #
            '806554489': '12',  #
            '-843295620': '13',  #
            '1310660844': '14',  #
            '895316616': '15',  #
        })
        self.large_network_out_data = build_large_network_out(network_manager=network_manager, data=data, network_in_descriptions={
            '1240779746': 'OUT'
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

    def change_event(self, component_id: str, large_data_in):
        match component_id:
            case '-998761478':
                self.network_manager.get_large_network(self.large_network_out_data['1240779746']['uuid']).update_source(self.uuid, large_data_in)
                offset = 0
                if self.value:  # bit shift switch on
                    offset = offset + 16
                for wire_id, wire_dict in self.network_out_data.items():
                    idx = int(wire_dict['description']) + offset
                    wire_value = large_data_in[idx] if 0 <= idx < len(large_data_in) else 0
                    wire_uuid = wire_dict['uuid']
                    self.network_manager.get_network(wire_uuid).update_source(self.uuid, wire_value)


