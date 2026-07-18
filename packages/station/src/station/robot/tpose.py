from station.base.component import ComponentType, SComponent
from station.base.constants import ARM_CONFIG_NO
from station.base.types import ArmConfig, ArmMotionType, BlendMotion
from station.robot.path import Path
from zmath.range import Range
from zmath.ranged_value import RangedValue
from zmath.transform_matrix import TMatrix3


class TPose(SComponent):
    def __init__(self, name: str, parent: Path):
        super().__init__(name, ComponentType.TPOSE, parent=parent)

        self._blend: BlendMotion = BlendMotion(is_blend=False, intensity=-1)  # Default blend motion
        self._config: ArmConfig = ARM_CONFIG_NO[0]  # Default arm configuration
        self._speed_override: RangedValue[int] = RangedValue(Range(1, 100), 100)  # Default speed
        self._motion_type: ArmMotionType = ArmMotionType.JOINT  # Default motion type
