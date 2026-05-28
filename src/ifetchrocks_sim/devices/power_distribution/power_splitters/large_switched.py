"""
Long Power splitter type 63

http://ifetch.rocks/manual/images/DeviceLongLargePowerSplitter.png

"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

"""
{
                        "indexedChildren": {
                            "1336288955": {
                                "indexedChildren": {
                                },
                                "indexedDeviceData": {
                                },
                                "integrity": 1.0,
                                "location": 4,
                                "payload": "{\"x\":0.5133441090583801,\"y\":1.0389268398284913,\"z\":2.353861093521118}",
                                "position": {
                                    "x": 5.08,
                                    "y": 0.0,
                                    "z": 0.0
                                },
                                "rotation": {
                                    "w": 0.7071068,
                                    "x": 0.0,
                                    "y": 0.7071068,
                                    "z": 0.0
                                },
                                "signalValue": 0,
                                "storedPower": {
                                },
                                "type": 2,
                                "uuid": "f4bdbd9f-3f68-4464-bd91-60540c260fc2"
                            },
                            "1779774388": {
                                "indexedChildren": {
                                },
                                "indexedDeviceData": {
                                },
                                "integrity": 1.0,
                                "location": 4,
                                "payload": "",
                                "position": {
                                    "x": 5.08,
                                    "y": 0.0,
                                    "z": 0.0
                                },
                                "rotation": {
                                    "w": 0.7071068,
                                    "x": 0.0,
                                    "y": 0.7071068,
                                    "z": 0.0
                                },
                                "signalValue": 0,
                                "storedPower": {
                                },
                                "type": 2,
                                "uuid": "69a6efba-a007-4dcf-962c-73231c5eb781"
                            },
                            "-221728388": {
                                "indexedChildren": {
                                },
                                "indexedDeviceData": {
                                },
                                "integrity": 1.0,
                                "location": 4,
                                "payload": null,
                                "position": {
                                    "x": 5.08,
                                    "y": 0.0,
                                    "z": 0.0
                                },
                                "rotation": {
                                    "w": 0.7071068,
                                    "x": 0.0,
                                    "y": 0.7071068,
                                    "z": 0.0
                                },
                                "signalValue": 0,
                                "storedPower": {
                                },
                                "type": 5,
                                "uuid": "2397a23a-cc8e-455a-9e66-5065a433b012"
                            }
                        },
                        "indexedDeviceData": {
                        },
                        "integrity": 1.0,
                        "location": 4,
                        "payload": "",
                        "position": {
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "rotation": {
                            "w": 1.0,
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "signalValue": 0,
                        "storedPower": {
                            "1748735741": 0.0,
                            "-1911346121": 0.0
                        },
                        "type": 127,
                        "uuid": "2d80455f-d254-415c-b423-3e6c75713bd0"
                    }
"""

class LargeSwitched:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'LargeSwitched'
        self.color = 'red'
        self.type = 127
        self.image = 'https://ifetch.rocks/manual/images/LargeSwitchedPower.png'
        self.uuid = data['uuid']

        # Large Power In
        self.network_in_0 = get_connection_uuid_by_id(data, '1779774388')
        # Small Data In
        self.network_in_1 = get_connection_uuid_by_id(data, '-221728388')

        # Large Power Out
        self.network_out_0 = get_connection_uuid_by_id(data, '1336288955')


        self.value = [0, 0, 0]
        self.network_manager = network_manager
        self.output_networks = []
        self.input_networks = [self.network_in_1]
        self.input_power_networks = []
        self.output_power_networks = []
        self.large_input_power_networks = [self.network_in_0]
        self.large_output_power_networks = [self.network_out_0]

        network_manager.get_network(self.network_in_0).register_listener(self.update_in_0)
        network_manager.get_network(self.network_in_1).register_listener(self.update_in_1)



    def update_in_0(self, uuid: str, value: int):
        if self.value[0] != value:
            self.value[0] = value
            self.output()

    def update_in_1(self, uuid: str, value: int):
        if self.value[1] != value:
            self.value[1] = value
            self.output()

    def output(self):
        target_power = 0
        if self.value[1]:
            target_power = self.value[0]
        if self.value[2] != target_power:
            self.value[2] = target_power
            self.network_manager.get_network(self.network_out_0).update_source(self.uuid, target_power)
