from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id, get_device_data_by_id
from typing import List

class ChannelMerger:

    CONNECTION_IDS = (
        '1674968089',   # in_0
        '-952892077',   # in_1
        '-1364447860',  # in_2
        '1288486929',   # in_3
        '-1345890287',  # in_4
        '-808426731',   # in_5
        '-93700751',    # in_6
        '-48530457',    # in_7
        '259959822',    # in_8
        '5987294',      # in_9
        '895659983',    # in_10
        '-2022094280',  # in_11
        '-1973271690',  # in_12
        '1839429484',   # in_13
        '109182082',    # in_14
        '-317353449',   # in_15
    )

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Channel Merger'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceLargePacketMerger.png'
        self.uuid = data['uuid']
        self.size = 20
        self.input_networks = [
            get_connection_uuid_by_id(data, cid) for cid in self.CONNECTION_IDS
        ]
        for i, net in enumerate(self.input_networks):
            setattr(self, f'network_in_{i}', net)
        self.input_networks_labels = [str(i) for i in range(16)]

        self.large_output_networks = [get_connection_uuid_by_id(data, '1604985134')]
        self.large_input_networks = [get_connection_uuid_by_id(data, '418515293')]

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
        for i in range(16):
            def make_updater(idx):
                def updater(uuid: str, value: int):
                    self.in_value_data[idx] = value
                    self.update_and_notify()
                return updater
            network_manager.get_network(self.input_networks[i]).register_listener(make_updater(i))

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
        #in_value_data
        self.network_manager.get_large_network(self.large_output_networks[0]).update_source(self.uuid, value)
        pass
        #self.value = self.in_value_a * self.in_value_b
        #self.network_manager.get_network(self.network_out_1).update_source(self.uuid, self.value)
