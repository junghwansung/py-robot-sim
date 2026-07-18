from station.base.types import DriveType, JointType
from zmath.range import Range
from zmath.types import Axis


class Joint:
    def __init__(
        self,
        joint_axis: Axis,
        joint_type: JointType,
        drive_type: DriveType,
        hard_limit: Range,
        max_speed: float,
        name: str = "",
    ):
        # Current State
        self._current_value: float = 0.0
        self._soft_limit: Range = hard_limit
        # Specifications
        self._name: str = name
        self._axis: Axis = joint_axis
        self._drive_type: DriveType = drive_type
        self._type: JointType = joint_type
        self._hard_limit: Range = hard_limit
        self._max_speed: float = max_speed
        self._effort_limit: float = 0.0  # use later for torque/force limit

    @classmethod
    def create_revolute_joint(
        cls,
        joint_axis: Axis,
        drive_type: DriveType,
        hard_limit: Range,
        max_speed: float,
        name: str,
    ) -> "Joint":
        return cls(joint_axis, JointType.REVOLUTE, drive_type, hard_limit, max_speed, name)

    @property
    def value(self) -> float:
        return self._current_value

    @value.setter
    def value(self, new_value: float) -> None:
        self._current_value = (
            new_value if self.soft_limit.is_contain(new_value) else self.soft_limit.clamp(new_value)
        )

    @property
    def soft_limit(self) -> Range:
        return self._soft_limit

    @soft_limit.setter
    def soft_limit(self, new_soft_limit: Range) -> None:
        new_min = new_soft_limit.min
        new_max = new_soft_limit.max

        if not self.hard_limit.is_contain(new_min):
            new_min = self.hard_limit.clamp(new_min)
        if not self.hard_limit.is_contain(new_max):
            new_max = self.hard_limit.clamp(new_max)

        self._soft_limit = Range(new_min, new_max)

    # Specifications
    @property
    def name(self) -> str:
        return self._name

    @property
    def joint_type(self) -> JointType:
        return self._type

    @property
    def hard_limit(self) -> Range:
        return self._hard_limit

    @property
    def max_speed(self) -> float:
        return self._max_speed

    @property
    def effort_limit(self) -> float:
        return self._effort_limit
