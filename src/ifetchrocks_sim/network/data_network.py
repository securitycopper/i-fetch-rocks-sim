from __future__ import annotations

from typing import Callable


class DataNetwork:
    """Single wire carrying an int value merged from multiple sources."""

    def __init__(self, uuid: str):
        self.value = 0
        self.sources: dict[str, int] = {}
        self.listener_functions: list[Callable[[str, int], None]] = []
        self.name_listener_functions: list[Callable[[str, str], None]] = []
        self.uuid = uuid
        self._warning_count = 1
        self.name = ""
        self._override: int | None = None

    def register_listener(self, func: Callable[[str, int], None]) -> None:
        self.listener_functions.append(func)
        func(self.uuid, self.value)

    def register_name_listener(self, func: Callable[[str, str], None]) -> None:
        self.name_listener_functions.append(func)
        func(self.uuid, self.name)

    def set_name(self, name: str) -> None:
        self.name = name
        for func in self.name_listener_functions:
            func(self.uuid, name)

    def register_source(self, source_uuid: str) -> None:
        self.sources[source_uuid] = 0
        if len(self.sources) > self._warning_count:
            self._warning_count = len(self.sources)
            print(f"Warning: Wire {self.uuid} has more then one source {self.sources}")

    def update_source(self, source_uuid: str, value: int) -> None:
        self.sources[source_uuid] = value
        if len(self.sources) > self._warning_count:
            self._warning_count = len(self.sources)
            print(f"Warning: Wire {self.uuid} has more then one source {self.sources}")
        self.update_and_notify()

    def set_override(self, value: int) -> None:
        self._override = value
        if self.value != value:
            self.value = value
            self.notify_listeners_of_change()

    def clear_override(self) -> None:
        self._override = None
        self.update_and_notify()

    def unregister_source(self, source_uuid: str) -> int | None:
        value = self.sources.pop(source_uuid, None)
        if value is not None:
            self.update_and_notify()
        return value

    def update_and_notify(self) -> None:
        if self._override is not None:
            if self.value != self._override:
                self.value = self._override
                self.notify_listeners_of_change()
            return

        calculated_value = 0
        for value in self.sources.values():
            calculated_value = calculated_value | value

        if calculated_value != self.value:
            self.value = calculated_value
            self.notify_listeners_of_change()

    def notify_listeners_of_change(self) -> None:
        for func in self.listener_functions:
            func(self.uuid, self.value)
