from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id, get_device_data_by_id

"""
COUNTER_DISPLAY (/DATA_MONITORS/DISPLAYS/COUNTER_DISPLAY, type 45)

In COUNT_TRUE mode (default): increments the count by 1 each time the input
transitions from FALSE (0) to TRUE (non-zero).

In COUNT_ANY mode (device data -2139921001 non-zero): increments the count
on any transition that crosses zero (0→non-zero OR non-zero→0).

NOTE: ANY BINARY VALUE NOT 0000000000000000 WILL BE READ AS TRUE.

The current count is emitted as a 16-bit unsigned value on the output wire
(wraps 65535 → 0).

Tick-boundary semantics mirror SmallLoopBreak:
  end_of_tick  — detect edge; increment count internally.
  start_of_tick — emit updated count to downstream via the output wire.

Port IDs confirmed from save d88a1650:
  -1352816633  data input  (clock / increment trigger)
   1521555828  data output (current count value, 16-bit wrapping)
  -1759672832  power in    (power loss → immediate count reset to 0)
  -2139921001  COUNT_ANY mode flag (device data; non-zero = COUNT_ANY)
"""


class CounterDisplay:

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.uuid = data['uuid']
        self.network_in = get_connection_uuid_by_id(data, '-1352816633')
        self.network_out = get_connection_uuid_by_id(data, '1521555828')
        self.network_power_in = get_connection_uuid_by_id(data, '-1759672832')
        self.count = data.get('signalValue', 0)
        self._input_buffer = 0
        self._prev_input = 0
        self._count_dirty = False
        self._power_was_on = False
        self.network_manager = network_manager

        # COUNT_ANY mode: device data key -2139921001 with non-zero signal
        try:
            self._count_any = bool(get_device_data_by_id(data, '-2139921001')['signal'])
        except (KeyError, TypeError):
            self._count_any = False

        self.input_networks = [n for n in [self.network_in] if n]
        self.output_networks = [self.network_out] if self.network_out else []
        self.input_power_networks = [self.network_power_in] if self.network_power_in else []

        if self.network_in:
            network_manager.get_network(self.network_in).register_listener(self._on_input)
        if self.network_power_in:
            network_manager.get_power_network(self.network_power_in).register_listener(self._on_power)

        network_manager.register_end_of_tick_listener(self._end_of_tick)
        network_manager.register_start_of_tick_listener(self._start_of_tick)

        self._notify()

    def _on_input(self, uuid: str, value: int):
        self._input_buffer = value

    def _on_power(self, uuid: str, value: int):
        # Power loss: reset count AND edge detector immediately (same tick)
        # to match in-game behaviour.  In hardware, a power cut clears all
        # internal state — including the edge detector's previous-input
        # memory — so the counter can re-detect a 0→TRUE edge after power
        # is restored.
        was_on = self._power_was_on
        self._power_was_on = (value != 0)
        if was_on and value == 0:
            self.count = 0
            self._prev_input = 0
            self._notify()

    def _end_of_tick(self):
        prev_zero = self._prev_input == 0
        curr_zero = self._input_buffer == 0
        if self._count_any:
            # COUNT_ANY: increment on any zero-boundary crossing
            edge = prev_zero != curr_zero
        else:
            # COUNT_TRUE (default): increment on 0 → non-zero only
            edge = prev_zero and not curr_zero
        if edge:
            self.count = (self.count + 1) % 65536
            self._count_dirty = True
        self._prev_input = self._input_buffer

    def _start_of_tick(self):
        if self._count_dirty:
            self._count_dirty = False
            self._notify()

    def _notify(self):
        if self.network_out:
            self.network_manager.get_network(self.network_out).update_source(self.uuid, self.count)
