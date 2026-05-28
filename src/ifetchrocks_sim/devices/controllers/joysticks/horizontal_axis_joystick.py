"""
HorizontalAxisJoystick type 73

/CONTROLLERS/JOYSTICKS/HORIZONTAL_AXIS

THE HORIZONTAL AXIS JOYSTICK OUTPUTS FROM 0 - 65,536 BASED UPON ITS PHYSICAL
POSITION FROM ITS CENTRE POINT.
THE OUTPUT IS ON EITHER THE Y+ OR Y- DEPENDING WHICH SIDE OF THE CENTRE POINT
THE JOYSTICK IS HELD CURRENTLY.

Port keys (confirmed from save 102d6094, 2026-03-22):
  '8306676'    → Y+ output (positive side)  — idd key '696373510'
  '508122447'  → Y- output (negative side)  — idd key '96910867'

State encoding:
  idd '696373510' signal field = current positive output value (0–65535)
  idd '96910867'  signal field = current negative output value (0–65535)
  rot_x > 0 → joystick deflected positive; rot_x < 0 → deflected negative
  At full deflection: active side = 65535, idle side = 0
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_device_data_by_id, get_connection_uuid_by_id

PORT_POSITIVE = '8306676'    # confirmed 2026-03-22: Y+ → BinaryLightArray
PORT_NEGATIVE = '508122447'  # confirmed 2026-03-22: Y- → ValueDisplay

_IDD_POSITIVE = '696373510'  # confirmed 2026-03-22: signal field = positive output
_IDD_NEGATIVE = '96910867'   # confirmed 2026-03-22: signal field = negative output


class HorizontalAxisJoystick:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Horizontal Axis Joystick'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceHorizontalAxisJoystick.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self.network_pos_out = get_connection_uuid_by_id(data, PORT_POSITIVE)
        self.network_neg_out = get_connection_uuid_by_id(data, PORT_NEGATIVE)

        pos_idd = get_device_data_by_id(data, _IDD_POSITIVE)
        neg_idd = get_device_data_by_id(data, _IDD_NEGATIVE)
        self.positive_value = int(pos_idd.get('signal') or 0)
        self.negative_value = int(neg_idd.get('signal') or 0)

        self.input_networks = []
        self.output_networks = [self.network_pos_out, self.network_neg_out]

        self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_pos_out).update_source(self.uuid, self.positive_value)
        self.network_manager.get_network(self.network_neg_out).update_source(self.uuid, self.negative_value)
