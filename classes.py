from typing import Any


class Expandable:
    def set(self, name: str, value: Any):
        self.__setattr__(name, value)
