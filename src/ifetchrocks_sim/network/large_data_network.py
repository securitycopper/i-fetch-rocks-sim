from __future__ import annotations

from typing import Callable


class LargeDataNetwork:
    """Large wire carrying a fixed-width vector merged from multiple sources."""

    WIDTH = 32

    def __init__(self, uuid: str):
        self.value = [0] * self.WIDTH
        self.sources: dict[str, list[int]] = {}
        self.listener_functions: list[Callable[[str, list[int]], None]] = []
        self.uuid = uuid
        self._warning_count = 1

    def register_listener(self, func: Callable[[str, list[int]], None]) -> None:
        self.listener_functions.append(func)
        func(self.uuid, self.value)

    def register_source(self, source_uuid: str) -> None:
        self.sources[source_uuid] = [0] * self.WIDTH
        if len(self.sources) > self._warning_count:
            self._warning_count = len(self.sources)
            print(f"Warning: Wire {self.uuid} has more then one source {self.sources}")

    def update_source(self, source_uuid: str, value: list[int]) -> None:
        self.sources[source_uuid] = value
        if len(self.sources) > self._warning_count:
            self._warning_count = len(self.sources)
            print(f"Warning: Wire {self.uuid} has more then one source {self.sources}")
        self.update_and_notify()

    def update_and_notify(self) -> None:
        calculated_value = [0] * self.WIDTH
        for value in self.sources.values():
            calculated_value = [calculated_value[i] | x for i, x in enumerate(value)]

        if calculated_value != self.value:
            self.value = calculated_value
            self.notify_listeners_of_change()

    def notify_listeners_of_change(self) -> None:
        for func in self.listener_functions:
            func(self.uuid, self.value)
