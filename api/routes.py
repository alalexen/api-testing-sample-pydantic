from enum import Enum


class Routes(Enum):
    OBJECTS = '/objects'
    OBJECTS_ITEM = '/objects/{}'

    def __str__(self) -> str:
        return self.value
