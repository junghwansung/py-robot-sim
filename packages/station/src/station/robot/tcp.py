from station.base.component import SComponent
from station.base.constants import ComponentType
from station.robot.robot import Robot
from zmath.transform_matrix import TMatrix3


class TCP(SComponent):
    def __init__(self, name: str, parent: Robot):
        super().__init__(name, ComponentType.TCP, parent=parent)
        self._name: str = name
        self._parent: Robot = parent
        self._flange_to_tcp: TMatrix3 = TMatrix3.identity()
