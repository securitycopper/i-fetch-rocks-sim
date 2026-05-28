"""
TwoAxisJoystick type 9

/CONTROLLERS/JOYSTICKS/2_AXIS_JOYSTICK

Outputs 0-65535 based on its current physical position from its centre point.
Outputs X+, X-, Y+ and Y- values separately.

Port keys (confirmed from save 102d6094 by wiring each port to a ValueDisplay,
2026-03-22; NOTE: in-game port labels do not match physical stick direction —
mapping is by label text only):

  '-931286282'  → X+ output  — idd key '-569088382'
  '1062940329'  → Y+ output  — idd key '1887731857'
  '-1221456788' → X- output  — idd key '808633644'
  '469203979'   → Y- output  — idd key '-1545963378'

NOTE: The 2-axis joystick is spring-return; it snaps to centre when released.
The idd signal fields are always 0 in any saved state observed. The device
outputs are live (runtime) only, so this implementation reads initial values
from the idd signal fields (all zero at save time).
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_device_data_by_id, get_connection_uuid_by_id

PORT_X_POS = '-931286282'   # confirmed 2026-03-22: in-game label X+
PORT_Y_POS = '1062940329'   # confirmed 2026-03-22: in-game label Y+
PORT_X_NEG = '-1221456788'  # confirmed 2026-03-22: in-game label X-
PORT_Y_NEG = '469203979'    # confirmed 2026-03-22: in-game label Y-

_IDD_X_POS = '-569088382'
_IDD_Y_POS = '1887731857'
_IDD_X_NEG = '808633644'
_IDD_Y_NEG = '-1545963378'


class TwoAxisJoystick:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = '2 Axis Joystick'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceJoystick2Axis1.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self.network_x_pos = get_connection_uuid_by_id(data, PORT_X_POS)
        self.network_y_pos = get_connection_uuid_by_id(data, PORT_Y_POS)
        self.network_x_neg = get_connection_uuid_by_id(data, PORT_X_NEG)
        self.network_y_neg = get_connection_uuid_by_id(data, PORT_Y_NEG)

        self.x_pos = int((get_device_data_by_id(data, _IDD_X_POS).get('signal') or 0))
        self.y_pos = int((get_device_data_by_id(data, _IDD_Y_POS).get('signal') or 0))
        self.x_neg = int((get_device_data_by_id(data, _IDD_X_NEG).get('signal') or 0))
        self.y_neg = int((get_device_data_by_id(data, _IDD_Y_NEG).get('signal') or 0))

        self.input_networks = []
        self.output_networks = [self.network_x_pos, self.network_y_pos,
                                self.network_x_neg, self.network_y_neg]

        self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_x_pos).update_source(self.uuid, self.x_pos)
        self.network_manager.get_network(self.network_y_pos).update_source(self.uuid, self.y_pos)
        self.network_manager.get_network(self.network_x_neg).update_source(self.uuid, self.x_neg)
        self.network_manager.get_network(self.network_y_neg).update_source(self.uuid, self.y_neg)
