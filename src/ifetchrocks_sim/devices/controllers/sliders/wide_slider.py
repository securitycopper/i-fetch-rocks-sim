from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id


class WideSlider:
    """
    /CONTROLLERS/SLIDERS/WIDE_SLIDER (type 16)

    Outputs 0-65535 based on physical position.

    Port keys (confirmed from save 102d6094, 2026-03-21):
      '753686288'   → data out (type 5)
      devData key '352543217' → stored slider value
    """

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Wide Slider'
        self.color = 'blue'
        self.type = 16
        self.image = 'http://ifetch.rocks/manual/images/DeviceSliderWide1.png'
        self.uuid = data['uuid']
        self.network_out = get_connection_uuid_by_id(data, '753686288')
        dd = data.get('indexedDeviceData', {})
        self.value = dd.get('352543217', {}).get('signal', 0) if dd else 0
        self.network_manager = network_manager
        self.input_networks = []
        self.output_networks = [self.network_out]
        self.notify()

    def set_value(self, value: int):
        if self.value != value:
            self.value = value
            self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_out).update_source(self.uuid, self.value)
