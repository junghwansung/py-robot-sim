from enum import Enum

from zmath.transform_matrix import TMatrix3


class ComponentType(int, Enum):
    WORLD = 0
    ROBOT = 1
    TOOL = 3
    TCP = 4
    PATH = 5
    TPOSE = 6
    SENSOR = 7
    MOBILE = 8
    RAIL = 9


class SComponent:
    """Base class for all components in the `S`tation."""

    @staticmethod
    def get_world_name() -> str:
        return "world"

    def __init__(self, name: str, type: ComponentType, parent: "SComponent" | None):
        if type != ComponentType.WORLD and parent is None:
            raise ValueError("Non-world components must have a parent.")

        self._name = name
        self._type = type
        self._parent_to_base: TMatrix3 = TMatrix3.identity()

        self._parent: SComponent | None = parent

    @classmethod
    def create_world(cls) -> "SComponent":
        return cls(cls.get_world_name(), ComponentType.WORLD, parent=None)

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> ComponentType:
        return self._type

    def get_parent_to_base(self) -> TMatrix3:
        return self._parent_to_base

    def set_parent_to_base(self, value: TMatrix3):
        self._parent_to_base = value

    def get_world_to_base(self) -> TMatrix3:
        if self._parent is None:
            return self._parent_to_base
        else:
            return self._parent.get_world_to_base() @ self._parent_to_base

    def set_world_to_base(self, world_to_base: TMatrix3):
        if self._parent is None:
            self._parent_to_base = world_to_base
        else:
            world_to_parent = self._parent.get_world_to_base()
            self._parent_to_base = world_to_parent.inverse() @ world_to_base

    def get_parent(self) -> "SComponent" | None:
        return self._parent

    def set_parent(self, value: "SComponent"):
        self._parent = value
        self.set_world_to_base(self.get_world_to_base())
