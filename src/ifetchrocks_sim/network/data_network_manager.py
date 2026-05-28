from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .data_network import DataNetwork
from .large_data_network import LargeDataNetwork


class DataNetworkManager:
    def __init__(self):
        self.networks: dict[str, DataNetwork] = {}
        self.large_networks: dict[str, LargeDataNetwork] = {}
        self.power_networks: dict[str, DataNetwork] = {}
        self.start_of_tick_listeners: list[Callable[[], Any]] = []
        self.end_of_tick_listeners: list[Callable[[], Any]] = []
        self.tick = 0
        self.wireless_channels: dict[int, list[int]] = {}
        self._pending_notify: list[DataNetwork | LargeDataNetwork] = []

    def register_start_of_tick_listener(self, func: Callable[[], Any]) -> None:
        self.start_of_tick_listeners.append(func)

    def register_end_of_tick_listener(self, func: Callable[[], Any]) -> None:
        self.end_of_tick_listeners.append(func)

    def set_tick(self, tick: int) -> None:
        if self.tick != tick:
            self.tick = tick
            for listener in self.end_of_tick_listeners:
                listener()
            for listener in self.start_of_tick_listeners:
                listener()
            self._flush_pending_notify()

    def queue_notify(self, network: DataNetwork | LargeDataNetwork) -> None:
        self._pending_notify.append(network)

    def _flush_pending_notify(self) -> None:
        while self._pending_notify:
            batch = self._pending_notify
            self._pending_notify = []
            for network in batch:
                network.notify_listeners_of_change()

    def get_network(self, uuid: str) -> DataNetwork:
        if uuid not in self.networks:
            self.networks[uuid] = DataNetwork(uuid)
        return self.networks[uuid]

    def get_power_network(self, uuid: str) -> DataNetwork:
        if uuid not in self.power_networks:
            self.power_networks[uuid] = DataNetwork(uuid)
        return self.power_networks[uuid]

    def does_power_network_exists(self, uuid: str) -> bool:
        return uuid in self.power_networks

    def get_large_network(self, uuid: str) -> LargeDataNetwork:
        if uuid not in self.large_networks:
            self.large_networks[uuid] = LargeDataNetwork(uuid)
        return self.large_networks[uuid]

    def does_network_exists(self, uuid: str) -> bool:
        return uuid in self.networks

    def does_large_network_exists(self, uuid: str) -> bool:
        return uuid in self.large_networks
