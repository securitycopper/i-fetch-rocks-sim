from ifetchrocks_sim.network.data_network_manager import DataNetworkManager
from ifetchrocks_sim.devices.utils.device_utils import get_connection_uuid_by_id, get_device_data_by_id


class Register:

    POWER_PORT = '1096989087'  # type-3 power input; confirmed across multiple saves
    POWER_OUT_PORT = '-64052931'  # type-3 power output; daisy-chains to next register

    def __init__(self, network_manager: DataNetworkManager, data: dict):
        self.data = data
        self.name = 'Register'
        self.color = 'blue'
        self.image = 'http://ifetch.rocks/manual/images/DeviceRegister.png'
        self.uuid = data['uuid']
        self.network_in_1 = get_connection_uuid_by_id(data, '-723312417')   # DATA_IN (value to store)
        self.network_in_2 = get_connection_uuid_by_id(data, '1266942261')   # WRITE_EN (trigger: latch IN when positive)
        self.network_out_1 = get_connection_uuid_by_id(data, '1892577010') #Confirmed
        # Only treat power as present when the port key actually exists in the save.
        # get_connection_uuid_by_id returns a random UUID when not found, which
        # would create a spurious power listener and leave _powered=False.
        _children = data.get('indexedChildren', {})
        self.network_power = (
            _children[self.POWER_PORT]['uuid']
            if self.POWER_PORT in _children else None
        )
        self.network_power_out = (
            _children[self.POWER_OUT_PORT]['uuid']
            if self.POWER_OUT_PORT in _children else None
        )

        self.in_value_a = 0
        self.in_value_b = 0
        self._powered = True
        self._we_set_tick = -2   # tick when update_in_2 last saw WE>0
        self._data_set_tick = -2  # tick when update_in_1 last set in_value_a
        self._power_value = 0
        self.value = get_device_data_by_id(data, '1963860831')['signal']
        self.network_manager = network_manager
        self.input_networks = [self.network_in_1, self.network_in_2]
        self.input_networks_labels = ['IN', 'WRITE']
        self.output_networks = [self.network_out_1]
        self.input_power_networks = [self.network_power] if self.network_power else []
        self.output_power_networks = [self.network_power_out] if self.network_power_out else []
        self._write_network = network_manager.get_network(self.network_in_2)
        network_manager.get_network(self.input_networks[0]).register_listener(self.update_in_1)
        self._write_network.register_listener(self.update_in_2)
        if self.network_power:
            network_manager.get_power_network(self.network_power).register_listener(self.update_power)
        if self.value:
            self.update_and_notify()

    def update_in_1(self, uuid: str, value: int):
        """DATA_IN: cache incoming value; latch if WRITE is currently enabled."""
        self.in_value_a = value
        self._data_set_tick = self.network_manager.tick
        if self._powered and self.in_value_b:
            # Only trust stale in_value_b from a recent tick.
            # Stale WE from 3+ ticks ago is a DFS ordering artefact — the
            # upstream SLB has already dropped WE but the cascade hasn't
            # reached this register's WRITE_EN yet.  The CPU's multi-step
            # pipeline delivers data up to 2 ticks after the WE pulse.
            if self.network_manager.tick - self._we_set_tick <= 3:
                self.value = value
                self.update_and_notify()

    def update_in_2(self, uuid: str, value: int):
        """WRITE_EN: latch DATA_IN on rising edge; hold on falling edge."""
        self.in_value_b = value
        if value:
            self._we_set_tick = self.network_manager.tick
        if self._powered and value:
            # Only latch when the DATA_IN value is fresh (within 1 tick) AND
            # non-zero.  Spurious WE pulses from the step-counter reset cascade
            # always arrive at the same tick as a transient DATA_IN=0 from the
            # power-cut double-speed mechanism.  Those must not reset the
            # register.  Legitimate same-tick latches (e.g. circuit-level tests)
            # always have non-zero data.  Zero-values destined for this register
            # arrive via update_in_1 with in_value_b already asserted.
            if self.in_value_a != 0 and self.network_manager.tick - self._data_set_tick <= 1:
                self.value = self.in_value_a
                self.update_and_notify()

    def update_power(self, uuid: str, value: int):
        self._powered = bool(value)
        if not value:
            self.value = 0
            self.update_and_notify()
        # Power passthrough: registers daisy-chain power to the next device.
        if self.network_power_out and self._power_value != value:
            self._power_value = value
            self.network_manager.get_power_network(self.network_power_out).update_source(
                self.uuid, value
            )

    def update_and_notify(self):
        self.network_manager.get_network(self.network_out_1).update_source(self.uuid, self.value)
