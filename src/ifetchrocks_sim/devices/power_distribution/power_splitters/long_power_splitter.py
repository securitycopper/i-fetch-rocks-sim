"""
Long Power splitter type 63
Large Power IN: 1840910058, a09ff2a9-93f9-41e7-95c0-3ec82cdc2c4e
Large Power OUT: 1855121003, 80e6d7ca-cb24-464f-ac05-1ff370662eb3
Small Power Out: 373250303, 3a74431e-bc85-471d-a4b7-990b8700a5ca
Small Power Out: -482531002, bf10bcb4-dd48-4ed7-b74d-cd010875fcf2
http://ifetch.rocks/manual/images/DeviceLongLargePowerSplitter.png
"""
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id

test_data_long_power_splitter = r"""
{
    "indexedChildren": {
        "1840910058": {
            "indexedChildren": {
            },
            "indexedDeviceData": {
            },
            "integrity": 1.0,
            "location": 4,
            "payload": null,
            "position": {
                "x": 2.745895,
                "y": 0.876391947,
                "z": -0.134742975
            },
            "rotation": {
                "w": 0.6373029,
                "x": -0.587347,
                "y": 0.36703977,
                "z": 0.337861538
            },
            "signalValue": 0,
            "storedPower": {
            },
            "type": 2,
            "uuid": "a09ff2a9-93f9-41e7-95c0-3ec82cdc2c4e"
        },
        "1855121003": {
            "indexedChildren": {
            },
            "indexedDeviceData": {
            },
            "integrity": 1.0,
            "location": 4,
            "payload": null,
            "position": {
                "x": 2.66856551,
                "y": 1.02434242,
                "z": -0.129278183
            },
            "rotation": {
                "w": 0.672515631,
                "x": -0.492345333,
                "y": 0.445905149,
                "z": 0.326324016
            },
            "signalValue": 0,
            "storedPower": {
            },
            "type": 2,
            "uuid": "80e6d7ca-cb24-464f-ac05-1ff370662eb3"
        },
        "373250303": {
            "indexedChildren": {
            },
            "indexedDeviceData": {
            },
            "integrity": 1.0,
            "location": 4,
            "payload": null,
            "position": {
                "x": 2.83086777,
                "y": 0.866952062,
                "z": -0.196223021
            },
            "rotation": {
                "w": 0.823252439,
                "x": -0.4434353,
                "y": 0.312042415,
                "z": 0.168078
            },
            "signalValue": 0,
            "storedPower": {
            },
            "type": 3,
            "uuid": "3a74431e-bc85-471d-a4b7-990b8700a5ca"
        },
        "-482531002": {
            "indexedChildren": {
            },
            "indexedDeviceData": {
            },
            "integrity": 1.0,
            "location": 4,
            "payload": null,
            "position": {
                "x": 2.82708454,
                "y": 0.9124735,
                "z": -0.206756353
            },
            "rotation": {
                "w": 0.829914331,
                "x": -0.427475721,
                "y": 0.3186886,
                "z": 0.164147377
            },
            "signalValue": 0,
            "storedPower": {
            },
            "type": 3,
            "uuid": "bf10bcb4-dd48-4ed7-b74d-cd010875fcf2"
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
        "w": -4.371139E-08,
        "x": 0.0,
        "y": 0.0,
        "z": 1.0
    },
    "signalValue": 0,
    "storedPower": {
        "-1505453132": 0.0
    },
    "type": 63,
    "uuid": "db544276-159b-4ccb-b043-1c0218aeef1b"
}
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


class LongPowerSplitter:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Long Power Splitter'
        self.color = 'red'
        self.type = 63
        self.image = 'https://ifetch.rocks/manual/images/DeviceLongLargePowerSplitter.png'
        self.uuid = data['uuid']
        #indexed_children = list(data['indexedChildren'].values())
        self.network_in_0 = get_connection_uuid_by_id(data, '1840910058')

        # Small Output 0
        self.network_out_0 = get_connection_uuid_by_id(data, '373250303')  # TODO: the small outputs may be reversed
        # Small Output 1
        self.network_out_1 = get_connection_uuid_by_id(data, '-482531002')
        # Large output 0
        self.network_out_2 = get_connection_uuid_by_id(data, '1855121003')

        self.value = 0
        self.network_manager = network_manager
        self.output_networks = []
        self.input_networks = []
        self.input_power_networks = []
        self.output_power_networks = [self.network_out_0, self.network_out_1]
        self.large_input_power_networks = [self.network_in_0]
        self.large_output_power_networks = [self.network_out_2]

        network_manager.get_network(self.large_input_power_networks[0]).register_listener(self.update_in_0)



    def update_in_0(self, uuid: str, value: int):
        if self.value != value:
            self.value = value
            self.network_manager.get_network(self.network_out_0).update_source(self.uuid, self.value)
            self.network_manager.get_network(self.network_out_1).update_source(self.uuid, self.value)
            self.network_manager.get_network(self.network_out_2).update_source(self.uuid, self.value)

