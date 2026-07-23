from zmath.range import Range
from zmath.ranged_value import RangedValue
from zmath.types import Axis, Direction

from station.base.types import DriveType, JointType


class Joint:
    def __init__(
        self,
        joint_axis: Axis,
        joint_direction: Direction,
        joint_type: JointType,
        drive_type: DriveType,
        hard_limit: Range[float],
        max_speed: float,
        name: str = "",
    ):
        # Current State
        self._value_with_soft_limit: RangedValue[float] = RangedValue(hard_limit, 0.0)
        # Specifications
        self._name: str = name
        self._axis: Axis = joint_axis
        self._direction: Direction = joint_direction
        self._drive_type: DriveType = drive_type
        self._type: JointType = joint_type
        self._hard_limit: Range[float] = hard_limit
        self._max_speed: float = max_speed
        self._effort_limit: float = 0.0  # use later for torque/force limit

    @classmethod
    def create_revolute_joint(
        cls,
        joint_axis: Axis,
        joint_direction: Direction,
        drive_type: DriveType,
        hard_limit: Range[float],
        max_speed: float,
        name: str,
    ) -> "Joint":
        return cls(joint_axis, joint_direction, JointType.REVOLUTE, drive_type, hard_limit, max_speed, name)

    @property
    def value(self) -> float:
        return self._value_with_soft_limit.value

    @value.setter
    def value(self, new_value: float) -> None:
        self._value_with_soft_limit.set_value(
            new_value 
            if self._value_with_soft_limit.range.is_contain(new_value) 
            else self._value_with_soft_limit.range.clamp(new_value)
        )

    @property
    def soft_limit(self) -> Range[float]:
        return self._value_with_soft_limit.range

    @soft_limit.setter
    def soft_limit(self, new_soft_limit: Range[float]) -> None:
        new_min = new_soft_limit.min
        new_max = new_soft_limit.max

        if not self.hard_limit.is_contain(new_min):
            new_min = self.hard_limit.clamp(new_min)
        if not self.hard_limit.is_contain(new_max):
            new_max = self.hard_limit.clamp(new_max)

        self._value_with_soft_limit = RangedValue(Range(new_min, new_max), self._value_with_soft_limit.value)

    # Specifications
    @property
    def name(self) -> str:
        return self._name

    @property
    def joint_type(self) -> JointType:
        return self._type

    @property
    def hard_limit(self) -> Range[float]:
        return self._hard_limit

    @property
    def max_speed(self) -> float:
        return self._max_speed

    @property
    def effort_limit(self) -> float:
        return self._effort_limit
