from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class BinarySplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Binary Splitter'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceBinarySplitterLong.png'
        self.uuid = data['uuid']
        #indexed_children = list(data['indexedChildren'].values())
        self.network_in_1 = get_connection_uuid_by_id(data, '341887910')

        self.network_out_0 = get_connection_uuid_by_id(data, '602871336')
        self.network_out_1 = get_connection_uuid_by_id(data, '769250077')
        self.network_out_2 = get_connection_uuid_by_id(data, '-1430310076')
        self.network_out_3 = get_connection_uuid_by_id(data, '200650803')
        self.network_out_4 = get_connection_uuid_by_id(data, '895086378')
        self.network_out_5 = get_connection_uuid_by_id(data, '1672227797')
        self.network_out_6 = get_connection_uuid_by_id(data, '2147204989')
        self.network_out_7 = get_connection_uuid_by_id(data, '1274432150')

        # self.network_out_2 = get_connection_uuid_by_id(data, '198003536')
        # self.network_out_3 = get_connection_uuid_by_id(data, '1367693113')
        #self.value = data['signalValue']  # list(data['indexedDeviceData'].values())[0]['signal']
        self.switch = list(data['indexedDeviceData'].values())[0]['signal']
        self.value = 0
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1]
        self.output_networks = []
        self.output_networks = [self.network_out_0,
                                self.network_out_1,
                                self.network_out_2,
                                self.network_out_3,
                                self.network_out_4,
                                self.network_out_5,
                                self.network_out_6,
                                self.network_out_7
                                ]
        network_manager.get_network(self.network_in_1).register_listener(self.update_in_1)

    def update_in_1(self, uuid: str, value: int):
        if self.value != value:
            self.value = value
            self.update_and_notify()

    def update_and_notify(self):
        use_upper = self.switch

        # Extract the relevant 8 bits
        if use_upper:
            bits = (self.value >> 8) & 0xFF  # Upper 8 bits
        else:
            bits = self.value & 0xFF  # Lower 8 bits

        # Process the 8 bits and create variables (LSB-first: output_networks[0]=bit0, ..., [7]=bit7)
        variables = []
        for i in range(8):
            bit = (bits >> i) & 1
            variables.append(65535 if bit else 0)

        # # Optionally assign to named vars
        # var0, var1, var2, var3, var4, var5, var6, var7 = variables

        # Debug output
        #print(f"vars: {variables}")

        for output_network_uuid, value in zip(self.output_networks, variables):
            self.network_manager.get_network(output_network_uuid).update_source(self.uuid, value)

