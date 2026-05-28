from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

"""
{
                "indexedChildren": {
                    "1173709222": {
                        "indexedChildren": {
                        },
                        "indexedDeviceData": {
                        },
                        "integrity": 1.0,
                        "location": 4,
                        "payload": null,
                        "position": {
                            "x": 3.02871728,
                            "y": 0.8717694,
                            "z": 0.315125227
                        },
                        "rotation": {
                            "w": -0.441929579,
                            "x": 0.351819545,
                            "y": 0.6455499,
                            "z": 0.513991
                        },
                        "signalValue": 0,
                        "storedPower": {
                        },
                        "type": 5,
                        "uuid": "4a9aba30-517f-4174-b97f-5ba191021e53"
                    },
                    "-1790705161": {
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
                        "uuid": "b0c3f6a5-752e-477c-ad9e-9fb3319f56d5"
                    },
                    "2034020425": {
                        "indexedChildren": {
                        },
                        "indexedDeviceData": {
                        },
                        "integrity": 1.0,
                        "location": 4,
                        "payload": "{\"grabPosition\":{\"x\":-0.26662495732307436,\"y\":1.9395225048065186,\"z\":3.090054988861084},\"colour\":0}",
                        "position": {
                            "x": 3.18650246,
                            "y": 1.08599532,
                            "z": 0.407592773
                        },
                        "rotation": {
                            "w": -0.442070246,
                            "x": 0.274310917,
                            "y": 0.725297034,
                            "z": 0.450856477
                        },
                        "signalValue": 0,
                        "storedPower": {
                        },
                        "type": 5,
                        "uuid": "3e37c373-3f38-4c87-8d05-dfeddb8f1844"
                    }
                },
                "indexedDeviceData": {
                    "366728027": {
                        "position": {
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "rotation": {
                            "w": 0.9659259,
                            "x": 0.0,
                            "y": -0.258819,
                            "z": 0.0
                        },
                        "signal": 0
                    }
                },
                "integrity": 1.0,
                "location": 4,
                "payload": null,
                "position": {
                    "x": 3.25816631,
                    "y": 2.21475124,
                    "z": -0.062374115
                },
                "rotation": {
                    "w": -0.46189037,
                    "x": -0.508917868,
                    "y": 0.521269,
                    "z": -0.505904
                },
                "signalValue": 0,
                "storedPower": {
                },
                "type": 123,
                "uuid": "6b888313-3784-46fb-b5d5-38ff7335c68c"
            }
"""
class BinaryShift:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        # ----- Non Changing -----
        self.data = data
        self.network_manager = network_manager
        self.uuid = data['uuid']
        # ----- Set for the device -----
        self.type = 123
        self.name = 'Binary Shift'
        self.image = 'http://ifetch.rocks/manual/images/DeviceBinaryShift.png'
        # TODO: check this swich
        self.switch = list(data['indexedDeviceData'].values())[0]['signal']

        # Small Data Input
        self.network_in_0 = get_connection_uuid_by_id(data, '2034020425')
        # Small Data Shift
        self.network_in_1 = get_connection_uuid_by_id(data, '1173709222')


        # Small Output 0
        self.network_out_0 = get_connection_uuid_by_id(data, '-1790705161')


        self.value = [0,0,0]
        self.network_manager = network_manager
        self.output_networks = [self.network_out_0]
        self.input_networks = [self.network_in_0, self.network_in_1]
        self.input_power_networks = []
        self.output_power_networks = []
        self.large_input_power_networks = []
        self.large_output_power_networks = []

        network_manager.get_network(self.network_in_0).register_listener(self.update_in_0)
        network_manager.get_network(self.network_in_1).register_listener(self.update_in_1_shift)


    def output(self):
        # TODO: This may be reversied
        target_value = self.value[0] >> self.value[1]
        if self.switch:
             target_value = self.value[0] << self.value[1]

        if self.value[2] != target_value:
            self.value[2] = target_value
            self.network_manager.get_network(self.network_out_0).update_source(self.uuid, target_value)

    def update_in_0(self, uuid: str, value: int):
        if self.value[0] != value:
            self.value[0] = value
            self.output()

    def update_in_1_shift(self, uuid: str, value: int):
        if self.value[1] != value:
            self.value[1] = value
            self.output()

