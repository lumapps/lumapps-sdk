from __future__ import annotations

from typing import Union
from uuid import UUID

EntityIdValue = Union[str, int, UUID]


# pylint: disable=too-many-return-statements
def get_int(value: EntityIdValue) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, UUID):
        return value.int
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return UUID(value).int


class EntityId(UUID):
    def __init__(self, value: EntityIdValue) -> None:
        super().__init__(int=get_int(value))

    @property
    def str(self) -> str:
        return str(self)
