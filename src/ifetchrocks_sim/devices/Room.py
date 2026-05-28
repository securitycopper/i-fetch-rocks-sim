from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id, get_device_data_by_id, build_network_in
from typing import Any, List

class Room:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.type = 1
        self.data = data
        self.name = 'Channel Merger'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceLargePacketMerger.png'
        self.uuid = data['uuid']
        self.size = 20
        #self.network_in_0 = get_connection_uuid_by_id(data, '1674968089')
       # self.network_in_1 = get_connection_uuid_by_id(data, '-952892077')

        self.input_networks = [
        ]
        self.input_networks_labels = [
        ]
        ######### LARGE DATA NETWORKS ##############
        # See docs/room-port-map.md for full cross-room topology and RE status.
        # WARNING: Room.py names are INVERTED vs data-flow direction.
        #   _out_ fields below are actually data flowing INTO the room (room is consumer).
        #   _in_  fields below are actually data flowing OUT of the room (room is producer).

        # port -325482860 | cable 60b2e319 | data flows INTO room → ChannelSplitter 457a8e44 (instruction bus)
        # HYPOTHESIS: paired with Helm 3de44b84 output cable
        self.large_network_out_0_left_front_to_back  = get_connection_uuid_by_id(data, '-325482860')

        # port 1207760765 | cable e935db8d | data flows OUT of room ← ChannelSplitter 457a8e44 (decoded cmds)
        # HYPOTHESIS: paired with Helm 3de44b84 input cable 11d4df6a
        self.large_network_in_0_left_front_to_back = get_connection_uuid_by_id(data, '1207760765')

        # port 789320731 | cable ffb0b67f | data flows INTO room → ChannelMerger 56816edd (large input)
        # HYPOTHESIS: paired with hub room 3cd1e5ba output
        self.large_network_out_1_right = get_connection_uuid_by_id(data, '789320731')

        # port -1631889157 | cable 0e935799 | data flows OUT of room ← ChannelMerger 56816edd (output)
        # HYPOTHESIS: paired with hub room 3cd1e5ba input
        self.large_network_in_1_right = get_connection_uuid_by_id(data, '-1631889157')

        ######### LARGE POWER NETWORKS ############
        #Life Support Power: 65878718, 80e6d7ca-cb24-464f-ac05-1ff370662eb3
        self.large_power_network_in_0_life_support_power = get_connection_uuid_by_id(data, '65878718')

        # Power Larger Cable In Left (back to front, ), -633974235, a09ff2a9-93f9-41e7-95c0-3ec82cdc2c4e
        self.large_power_network_out_0_bottom_left = get_connection_uuid_by_id(data, '-633974235')

        ######## SMALL DATA NETWORKS ############
        #Life Support Data Out, 31010700, 872cee52-ce8e-4ce4-84f6-313e08d97ecd
        self.network_out_0 = get_connection_uuid_by_id(data, '31010700')
        self.network_out_data = list()
        self.network_out_descriptions = {
            '31010700': 'Life Support Data Out'
        }

        def change_event(connection_id: str, value: Any) -> None:
            pass

        ######## SMALL POWER NETWORKS ######

        self.network_in_descriptions = {
            '1186959326': 'Light', #  f6444d0c-4202-48d0-9c43-defc85532949
        }
        self.network_in_data = build_network_in(network_manager=network_manager, data=data, change_event=change_event,
                                                network_in_descriptions=self.network_in_descriptions)

        self.large_output_networks = []
        self.large_input_networks = []

        #self.network_out_1 = get_connection_uuid_by_id(data, '-1790705161')
        self.large_in_value_data = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
        self.in_value_data = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
        self.offset_switch = get_device_data_by_id(data, '547817599')['signal'] > 0
        self.value = get_device_data_by_id(data, '547817599')['signal']
        self.network_manager = network_manager

        self.output_networks = []

        if self.large_input_networks:
            network = network_manager.get_large_network(self.large_input_networks[0])
            network.register_listener(self.update_large_in_0)

    # def to_string(self):
    #         return str({k:v for (k,v) in enumerate(self.value)})

    def update_large_in_0(self, uuid: str, value: List[int]):
        self.large_in_value_data = value
        self.update_and_notify()

    def update_and_notify(self):
        # binary or in_value_data with large in value data, then send
        # account for bit shift
        value = [ self.large_in_value_data[i] | x for i, x in enumerate(self.in_value_data)]
        # in_value_data
        if self.large_output_networks:
            self.network_manager.get_large_network(self.large_output_networks[0]).update_source(self.uuid, value)
        pass
        #self.value = self.in_value_a * self.in_value_b
        #self.network_manager.get_network(self.network_out_1).update_source(self.uuid, self.value)
