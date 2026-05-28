from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class BinaryMux:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Binary Mux'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/BinaryMux.png'
        self.uuid = data['uuid']
        # indexed_children = list(data['indexedChildren'].values())
        # self.network_in_true = indexed_children[0]['uuid']
        # self.network_in_mux = indexed_children[2]['uuid']
        # self.network_in_false = indexed_children[1]['uuid']
        # self.network_out = indexed_children[3]['uuid']
        self.network_in_true = get_connection_uuid_by_id(data, '2034020425')   # RE-confirmed 2026-03-30
        self.network_in_mux =  get_connection_uuid_by_id(data, '563576145')    # RE-confirmed 2026-03-30
        self.network_in_false = get_connection_uuid_by_id(data, '1173709222')  # RE-confirmed 2026-03-30
        self.network_out = get_connection_uuid_by_id(data, '-1790705161')
        self.in_value_true = 0
        self.in_value_false = 0
        self.in_value_mux = 0
        self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        self.network_manager = network_manager
        self.input_networks = [self.network_in_true, self.network_in_mux, self.network_in_false]
        self.input_networks_labels = ['IN TRUE', 'BINARY MUX', 'IN FALSE']
        self.output_networks = [self.network_out]
        self.suspend_updates = True
        network_manager.get_network(self.network_in_true).register_listener(self.update_in_true)
        network_manager.get_network(self.network_in_mux).register_listener(self.update_in_mux)
        network_manager.get_network(self.network_in_false).register_listener(self.update_in_false)
        self.suspend_updates = False
        self.update_and_notify()
        # Force registratin
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)

    def update_in_true(self, uuid: str, value: int):
        self.in_value_true = value
        self.update_and_notify()

    def update_in_mux(self, uuid: str, value: int):
        self.in_value_mux = value
        self.update_and_notify()

    def update_in_false(self, uuid: str, value: int):
        self.in_value_false = value
        self.update_and_notify()

    def update_and_notify(self):
        if self.suspend_updates:
            return
        new_value = 0
        if self.in_value_mux:
            new_value = self.in_value_true
        else:
            new_value = self.in_value_false
        if new_value != self.value:
            self.value = new_value
            node = self.network_manager.get_network(self.network_out)
            node.update_source(self.uuid, self.value)
