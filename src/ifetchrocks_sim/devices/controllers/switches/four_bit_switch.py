from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_device_data_by_id, get_connection_uuid_by_id

"""

"""

class FourBitSwitch:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = '4 Bit Switch'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceSwitchBankShort.png'
        self.value = 0
        self.uuid = data['uuid']
        self.network_out = get_connection_uuid_by_id(data, '245567209')
        self.switch_1 = get_device_data_by_id(data,'-1426717297')['signal']
        self.switch_2 = get_device_data_by_id(data,'-74374117')['signal']
        self.switch_3 = get_device_data_by_id(data,'-1981437778')['signal']
        self.switch_4 = get_device_data_by_id(data,'-1941741643')['signal']
        self.network_manager = network_manager
        self.notify()
        self.input_networks = []
        self.output_networks = [self.network_out]

    # def press_with_value(self, value: int):
    #     if self.value == value:
    #         pass
    #     else:
    #         self.value = value
    #         self.notify()

    def notify(self):
        value = 0
        if self.switch_1:
            value = value | 0b0001
        if self.switch_2:
            value = value | 0b0010
        if self.switch_3:
            value = value | 0b0100
        if self.switch_4:
            value = value | 0b1000
        self.value = value
        self.network_manager.get_network(self.network_out).update_source(self.uuid, value)
