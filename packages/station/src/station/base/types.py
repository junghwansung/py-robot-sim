from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, NewType

from zmath.range import Range
from zmath.ranged_value import RangedValue
from zmath.types import Sign

JointValues = NewType("JointValues", list[float])


class JointType(int, Enum):
    REVOLUTE = 0
    PRISMATIC = 1


class DriveType(int, Enum):
    DRIVING = 0
    DRIVEN = 1


class RobotErr(int, Enum):
    INVALID_JOINT_INDEX = 0
    INVALID_JOINT_VALUES = 1
    SINGULARITY = 2
    INVERSE_KINEMATICS_FAILED = 3


class RobotType(int, Enum):
    SERIAL_6DOF = 0
    SERIAL_6DOF_COUNTER_BALANCER = 1
    SERIAL_6DOF_4_BAR_LINKAGE = 2


class RobotVendor(int, Enum):
    UNKNOWN = 0
    FANUC = 1
    KUKA = 2
    ABB = 3
    YASKAWA = 4
    UNIVERSAL_ROBOTS = 5
    KAWASAKI = 6
    HYUNDAI = 7


class ArmConfig(NamedTuple):
    shoulder: Sign  # 1=righty, -1=lefty
    elbow: Sign  # 1=up, -1=down
    wrist: Sign  # 1=flip, -1=no-flip


class ArmMotionType(int, Enum):
    JOINT = 0
    LINEAR = 1


class BlendMotion:
    def __init__(self, is_blend: bool = False, intensity: int = -1):
        self.blend: bool = is_blend
        self.intensity: RangedValue[int] = RangedValue(Range(-1, 10), intensity)

    def is_blend(self) -> bool:
        return self.blend

    def set_blend(self, is_blend: bool):
        self.blend = is_blend
        if not is_blend:
            self.intensity.set_value(-1)

    def get_intensity(self) -> int:
        if not self.blend:
            return -1
        return self.intensity.value

    def set_intensity(self, value: int):
        self.intensity.set_value(value)

    def __repr__(self) -> str:
        return f"BlendMotion(blend={self.blend}, intensity={self.intensity})"


class JointInterpolationMode(int, Enum):
    SHORTEST_ANGLE = 0
    TURN_NO = 1
    SOLUTION_ANGLE = 2
