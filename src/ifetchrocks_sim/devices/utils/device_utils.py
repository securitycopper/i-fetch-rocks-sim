import traceback
from collections import defaultdict
from typing import Any, Dict, List
import uuid

from ifetchrocks_sim.network.data_network_manager import DataNetworkManager


def build_network_in(*,network_manager: DataNetworkManager, data: Dict, change_event: Any,  network_in_descriptions: Dict[str, str]) -> Dict[str,Dict[str,Any]]:
    network_in_data = defaultdict(lambda:dict())
    for k, v in network_in_descriptions.items():
        network_in_data[k]['value'] = 0
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v
        def listener(u: str, value: int, k: str = k):
            if network_in_data[k]['value'] != value:
                network_in_data[k]['value'] = value
                change_event(k, value)

        network_in_data[k]['listener'] = listener

        #network_manager.get_network(network_in_data[k]['uuid']).register_listener(listener)
    return network_in_data


def register_listeners(*, network_manager: DataNetworkManager,
                       network_in_data: Dict[str, Dict[str, Any]],
                       large_network_in_data: Dict[str, Dict[str, Any]],
                       power_in_data: Dict[str, Dict[str, Any]],
                       large_power_in_data: Dict[str, Dict[str, Any]],
                       vector_in_data: Dict[str, Dict[str, Any]] = None
                       ) -> None:
    for i in network_in_data.values():
        device_uuid = i['uuid']
        device_listener = i['listener']
        network_manager.get_network(device_uuid).register_listener(device_listener)

    for i in large_network_in_data.values():
        device_uuid = i['uuid']
        device_listener = i['listener']
        network_manager.get_large_network(device_uuid).register_listener(device_listener)

    for i in power_in_data.values():
        device_uuid = i['uuid']
        device_listener = i['listener']
        network_manager.get_power_network(device_uuid).register_listener(device_listener)

    for i in large_power_in_data.values():
        device_uuid = i['uuid']
        device_listener = i['listener']
        network_manager.get_power_network(device_uuid).register_listener(device_listener)

    if vector_in_data:
        for i in vector_in_data.values():
            device_uuid = i['uuid']
            device_listener = i['listener']
            network_manager.get_large_network(device_uuid).register_listener(device_listener)


def build_power_network_in(*,network_manager: DataNetworkManager, data: Dict, change_event: Any,  network_in_descriptions: Dict[str, str]) -> Dict[str,Dict[str,Any]]:
    network_in_data = defaultdict(lambda:dict())
    for k, v in network_in_descriptions.items():
        network_in_data[k]['value'] = 0
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v

        def listener(u: str, value: int, k: str = k):
            if network_in_data[k]['value'] != value:
                network_in_data[k]['value'] = value
                change_event(k, value)

        network_in_data[k]['listener'] = listener
        #network_manager.get_power_network(network_in_data[k]['uuid']).register_listener(listener)
    return network_in_data


def build_large_network_in(*,network_manager: DataNetworkManager, data: Dict, change_event: Any,  network_in_descriptions: Dict[str, str]) -> Dict[str,Dict[str,Any]]:
    network_in_data = defaultdict(lambda:dict())
    for k, v in network_in_descriptions.items():
        network_in_data[k]['value'] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v

        def listener(u: str, value: int, k: str = k):
            if network_in_data[k]['value'] != value:
                network_in_data[k]['value'] = value
                change_event(k, value)

        network_in_data[k]['listener'] = listener
        #network_manager.get_large_network(network_in_data[k]['uuid']).register_listener(listener)
    return network_in_data


def build_vector_network_in(*, network_manager: DataNetworkManager, data: Dict, change_event: Any,
                              network_in_descriptions: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    network_in_data = defaultdict(lambda: dict())
    for k, v in network_in_descriptions.items():
        network_in_data[k]['value'] = [0] * 16
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v

        def listener(u: str, value: int, k: str = k):
            if network_in_data[k]['value'] != value:
                network_in_data[k]['value'] = value
                change_event(k, value)

        network_in_data[k]['listener'] = listener
    return network_in_data


def build_network_out(*,network_manager: DataNetworkManager, data: Dict, network_in_descriptions: Dict[str, str]) -> Dict[str,Dict[str,Any]]:
    network_in_data = defaultdict(lambda: dict())
    device_uuid = data['uuid']
    for k, v in network_in_descriptions.items():
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v
        network_manager.get_network(network_in_data[k]['uuid']).register_source(device_uuid)
    return network_in_data


def build_large_network_out(*,network_manager: DataNetworkManager, data: Dict, network_in_descriptions: Dict[str, str]) -> Dict[str,Dict[str,Any]]:
    network_in_data = defaultdict(lambda: dict())
    device_uuid = data['uuid']
    for k, v in network_in_descriptions.items():
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v
        network_manager.get_large_network(network_in_data[k]['uuid']).register_source(device_uuid)
    return network_in_data


def build_vector_network_out(*, network_manager: DataNetworkManager, data: Dict,
                               network_in_descriptions: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    network_in_data = defaultdict(lambda: dict())
    device_uuid = data['uuid']
    for k, v in network_in_descriptions.items():
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v
        network_manager.get_large_network(network_in_data[k]['uuid']).register_source(device_uuid)
    return network_in_data


def build_power_out(*,network_manager: DataNetworkManager, data: Dict, network_in_descriptions: Dict[str, str]) -> Dict[str,Dict[str,Any]]:
    network_in_data = defaultdict(lambda: dict())
    device_uuid = data['uuid']
    for k, v in network_in_descriptions.items():
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v
        network_manager.get_power_network(network_in_data[k]['uuid']).register_source(device_uuid)
    return network_in_data


def build_large_power_out(*,network_manager: DataNetworkManager, data: Dict, network_in_descriptions: Dict[str, str]) -> Dict[str,Dict[str,Any]]:
    network_in_data = defaultdict(lambda: dict())
    device_uuid = data['uuid']
    for k, v in network_in_descriptions.items():
        network_in_data[k]['uuid'] = get_connection_uuid_by_id(data=data, connection_id=k)
        network_in_data[k]['description'] = v
        network_manager.get_power_network(network_in_data[k]['uuid']).register_source(device_uuid)
    return network_in_data


def _get_description_of_uuid(d: Dict[str,Dict[str,str]], find_by_uuid: str) -> str:
    for component_id, component in d.items():
        if component['uuid'] == find_by_uuid:
            return component['description']
    return '?'


def graph_mappings(self: Any) -> None:
    self.input_networks = [i['uuid'] for i in self.network_in_data.values()]
    self.input_networks_labels = [_get_description_of_uuid(self.network_in_data, i) for i in self.input_networks]
    self.large_input_networks = [i['uuid'] for i in self.large_network_in_data.values()]
    self.large_input_networks_labels = [_get_description_of_uuid(self.large_network_in_data, i) for i in self.large_input_networks]
    self.input_power_networks = [i['uuid'] for i in self.power_in_data.values()]
    self.large_input_power_networks = [i['uuid'] for i in self.large_power_in_data.values()]
    self.output_networks = [o['uuid'] for o in self.network_out_data.values()]
    self.output_networks_labels = [_get_description_of_uuid(self.network_out_data,i) for i in self.output_networks]

    self.large_output_networks = [o['uuid'] for o in self.large_network_out_data.values()]
    self.power_output_networks = [o['uuid'] for o in self.power_out_data.values()]
    self.large_power_output_networks = [o['uuid'] for o in self.large_power_out_data.values()]
    self.vector_input_networks = [i['uuid'] for i in getattr(self, 'vector_in_data', {}).values()]
    self.vector_output_networks = [o['uuid'] for o in getattr(self, 'vector_out_data', {}).values()]


def get_connections_uuids_of_type(data: dict, type: int) -> List[str]:
    if 'indexedChildren' not in data:
        return []
    try:
        #  list(filter(lambda x: x['type'] == 5, list(data['indexedChildren'].values())))  #
        to_return = list()
        for connection in [i for i in data['indexedChildren'].values() if i is not None]:

            if 'type' in connection:
                if connection['type'] == type:
                    to_return.append(connection['uuid'])
            else:
                pass
    except:
        print(traceback.format_exc())
        return []

    return to_return


class NetworkManager:
    pass


def get_device_data_by_id(data: dict, connection_id: str) -> Dict:
    for child_id, connection in [i for i in data['indexedDeviceData'].items() if i is not None]:
        if child_id == connection_id:
            return connection
    raise KeyError(f"Device data id {connection_id!r} not found in {data.get('uuid', '?')}")


def get_connection_uuid_by_id(data: dict, connection_id: str) -> str:
    for child_id, connection in [i for i in data['indexedChildren'].items() if i is not None]:
        if child_id == connection_id:
            return connection['uuid']
    else:
        return str(uuid.uuid4())
