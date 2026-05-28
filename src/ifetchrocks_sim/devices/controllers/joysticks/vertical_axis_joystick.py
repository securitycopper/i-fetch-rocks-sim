"""
VerticalAxisJoystick type 74

/CONTROLLERS/JOYSTICKS/VERTICAL_AXIS

Outputs 0–65535 based on physical position from centre point.
Output is on either the Y+ or Y- port depending on which side of the centre
the joystick is held.

Port keys (confirmed from save 102d6094, 2026-03-22):
  '-797160931'  → Y+ output (positive side)  — idd key '1420139053'
  '-328908540'  → Y- output (negative side)  — idd key '624912278'

NOTE (2026-03-22): in the RE probe circuit, port '-328908540' was wired to the
BinaryLightArray (expected positive) and '-797160931' to the ValueDisplay
(expected negative). The outputs are reversed from that expectation — this is
a known in-game wiring-label bug. Implementation follows observed signal
behaviour.

State encoding (same pattern as HorizontalAxisJoystick type 73):
  idd '1420139053' signal field = current positive output value (0–65535)
  idd '624912278'  signal field = current negative output value (0–65535)
"""
from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_device_data_by_id, get_connection_uuid_by_id

PORT_POSITIVE = '-797160931'  # confirmed 2026-03-22: Y+ (observed signal=65535 at positive deflection)
PORT_NEGATIVE = '-328908540'  # confirmed 2026-03-22: Y- (observed signal=0 at positive deflection)

_IDD_POSITIVE = '1420139053'  # confirmed 2026-03-22: signal field = positive output
_IDD_NEGATIVE = '624912278'   # confirmed 2026-03-22: signal field = negative output


class VerticalAxisJoystick:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Vertical Axis Joystick'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceVerticalAxisJoystick.png'
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
