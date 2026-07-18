from enum import Enum
from typing import Literal

Sign = Literal[1, -1]


class Direction(int, Enum):
    POSITIVE = 1
    NEGATIVE = -1


class Axis(int, Enum):
    X = 0
    Y = 1
    Z = 2


class RotationOrder(str, Enum):
    XYZ = "XYZ"
    XZY = "XZY"
    YXZ = "YXZ"
    YZX = "YZX"
    ZXY = "ZXY"
    ZYX = "ZYX"
    ZYZ = "ZYZ"


class AxisPlane(int, Enum):
    XY = 0
    XZ = 1
    YZ = 2
