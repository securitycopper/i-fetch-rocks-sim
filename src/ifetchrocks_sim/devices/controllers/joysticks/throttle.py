"""
Throttle type 8

/CONTROLLERS/THROTTLES/THROTTLE

Outputs a value from 0 - 65,535 based upon its position relative to its
mid-point. Forward from the mid-point outputs to X+, backward to X-.

Port keys (confirmed from save 102d6094, 2026-03-22):
  '8306676'    → X+ output (forward)  — idd key '696373510'
  '508122447'  → X- output (backward) — idd key '96910867'

NOTE: Port keys and idd keys are identical to HorizontalAxisJoystick (type 73).
Physical rotation is encoded in idd rotation.y (vs rotation.x for type 73).
State encoding: idd signal field = current output value (0–65535).
At max forward: idd 696373510 signal=65535, idd 96910867 signal=0.
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_device_data_by_id, get_connection_uuid_by_id

PORT_X_POS = '8306676'    # confirmed 2026-03-22: X+ (forward) output
PORT_X_NEG = '508122447'  # confirmed 2026-03-22: X- (backward) output

_IDD_X_POS = '696373510'  # confirmed 2026-03-22: signal = X+ output value
_IDD_X_NEG = '96910867'   # confirmed 2026-03-22: signal = X- output value


class Throttle:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Throttle'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceJoystick1Axis1.png'
        self.uuid = data['uuid']
        self.network_manager = network_manager

        self.network_x_pos = get_connection_uuid_by_id(data, PORT_X_POS)
        self.network_x_neg = get_connection_uuid_by_id(data, PORT_X_NEG)

        pos_idd = get_device_data_by_id(data, _IDD_X_POS)
        neg_idd = get_device_data_by_id(data, _IDD_X_NEG)
        self.x_pos = int(pos_idd.get('signal') or 0)
        self.x_neg = int(neg_idd.get('signal') or 0)

        self.input_networks = []
        self.output_networks = [self.network_x_pos, self.network_x_neg]

        self.notify()

    def notify(self):
        self.network_manager.get_network(self.network_x_pos).update_source(self.uuid, self.x_pos)
        self.network_manager.get_network(self.network_x_neg).update_source(self.uuid, self.x_neg)
