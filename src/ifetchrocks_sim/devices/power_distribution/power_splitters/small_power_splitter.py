
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

test_data_small_power_splitter = r"""
{
                        "indexedChildren": {
                            "1350724679": {
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
                                "type": 3,
                                "uuid": "9fe46ffc-0c30-48de-b56a-4765ff5a43ec"
                            },
                            "151431565": {
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
                                "type": 3,
                                "uuid": "71232511-e98f-4268-8299-7daed5aa5bd9"
                            },
                            "-1685014131": {
                                "indexedChildren": {
                                },
                                "indexedDeviceData": {
                                },
                                "integrity": 1.0,
                                "location": 4,
                                "payload": "{\"x\":-0.7190960049629211,\"y\":1.3185466527938843,\"z\":2.8326542377471926}",
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
                                "type": 3,
                                "uuid": "88386ecf-b6ae-4bb0-9609-b862162b8d67"
                            },
                            "-332682322": {
                                "indexedChildren": {
                                },
                                "indexedDeviceData": {
                                },
                                "integrity": 1.0,
                                "location": 4,
                                "payload": "{\"grabPosition\":{\"x\":-0.737023651599884,\"y\":1.3490030765533448,\"z\":2.32220721244812},\"colour\":0}",
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
                                "type": 3,
                                "uuid": "b28cb310-7eac-4539-886c-ba16b602783f"
                            }
                        },
                        "indexedDeviceData": {
                        },
                        "integrity": 1.0,
                        "location": 4,
                        "payload": null,
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
                            "-315346704": 0.0
                        },
                        "type": 23,
                        "uuid": "04892706-af63-4a84-9fe9-2de2c74d0a71"
                    }
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class SmallPowerSplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Small Power Splitter'
        self.color = 'red'
        self.type = 23
        self.image = 'https://ifetch.rocks/manual/images/DeviceLongLargePowerSplitter.png'
        self.uuid = data['uuid']
        #indexed_children = list(data['indexedChildren'].values())
        self.network_in_0 = get_connection_uuid_by_id(data, '-1685014131')

        # TODO: The order of the small outputs may not be correct
        # Small Output 0
        self.network_out_0 = get_connection_uuid_by_id(data, '151431565')
        # Small Output 1
        self.network_out_1 = get_connection_uuid_by_id(data, '1350724679')
        # Small output 3
        self.network_out_2 = get_connection_uuid_by_id(data, '-332682322')

        self.value = 0
        self.network_manager = network_manager
        self.output_networks = []
        self.input_networks = []
        self.input_power_networks = [self.network_in_0]
        self.output_power_networks = [self.network_out_0, self.network_out_1, self.network_out_2]
        self.large_input_power_networks = []
        self.large_output_power_networks = []

        network_manager.get_power_network(self.input_power_networks[0]).register_listener(self.update_in_0)



    def update_in_0(self, uuid: str, value: int):
        if self.value != value:
            self.value = value
            self.network_manager.get_power_network(self.network_out_0).update_source(self.uuid, self.value)
            self.network_manager.get_power_network(self.network_out_1).update_source(self.uuid, self.value)
            self.network_manager.get_power_network(self.network_out_2).update_source(self.uuid, self.value)

