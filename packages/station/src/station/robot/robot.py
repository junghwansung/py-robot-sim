import math

from zmath.range import Range
from zmath.transform_matrix import TMatrix3
from zmath.types import Axis
from zutil.result import Err, Ok, Result

from station.base.component import ComponentType, SComponent
from station.base.types import RobotType, RobotVendor

from .kinematics.dh_param import DHLink, DHParam
from .kinematics.joint import Joint
from .kinematics.kinematics import Kinematics
from .kinematics.link import Link
from .kinematics.solver import KinematicsErr, KinematicsSolver


def _get_robot_type_and_vendor(name: str) -> tuple[RobotType, RobotVendor]:
    name_lower = name.lower()
    if "fanuc" in name_lower:
        return RobotType.SERIAL_6DOF, RobotVendor.FANUC
    elif "kuka" in name_lower:
        return RobotType.SERIAL_6DOF, RobotVendor.KUKA
    elif "abb" in name_lower:
        return RobotType.SERIAL_6DOF, RobotVendor.ABB
    elif "yaskawa" in name_lower:
        return RobotType.SERIAL_6DOF, RobotVendor.YASKAWA
    elif "ur" in name_lower or "universal" in name_lower:
        return RobotType.SERIAL_6DOF, RobotVendor.UNIVERSAL_ROBOTS
    elif "kawasaki" in name_lower:
        return RobotType.SERIAL_6DOF, RobotVendor.KAWASAKI
    elif "hyundai" in name_lower:
        return RobotType.SERIAL_6DOF, RobotVendor.HYUNDAI
    else:
        return RobotType.UNKNOWN, RobotVendor.UNKNOWN


def _get_dh_param_from_model(model_name: str) -> DHParam:
    # Placeholder — real implementation loads from robot database
    return DHParam([DHLink(0.0, 0.0, 0.0, 0.0)] * 6)


def _get_links_from_model(dof: int) -> list[Link]:
    # Placeholder — real implementation loads specs from robot database
    default_limit = Range(-math.pi, math.pi)
    return [
        Link(
            joint=Joint.create_revolute_joint(Axis.Z, default_limit, math.pi),
            name=f"link_{i}",
        )
        for i in range(dof)
    ]


class Robot(SComponent):
    def __init__(
        self,
        name: str,
        robot_type: RobotType,
        vendor: RobotVendor,
        dh_param: DHParam,
        links: list[Link],
    ):
        super().__init__(name, ComponentType.ROBOT)

        self._type: RobotType = robot_type
        self._vendor: RobotVendor = vendor
        self._kinematics: Kinematics = Kinematics(dh_param, links)

        self._override_speed: int = 5
        self._base_to_kin: TMatrix3 = TMatrix3.identity()
        self._end_to_flange: TMatrix3 = TMatrix3.identity()

    @classmethod
    def from_model(cls, model_name: str) -> "Robot":
        robot_type, vendor = _get_robot_type_and_vendor(model_name)
        dh_param = _get_dh_param_from_model(model_name)
        links = _get_links_from_model(dh_param.dof)
        return cls(model_name, robot_type, vendor, dh_param, links)

    @property
    def type(self) -> RobotType:
        return self._type

    @property
    def vendor(self) -> RobotVendor:
        return self._vendor

    @property
    def kinematics(self) -> Kinematics:
        return self._kinematics

    @property
    def override_speed(self) -> int:
        return self._override_speed

    @override_speed.setter
    def override_speed(self, value: int):
        assert 1 <= value <= 100, "Override speed must be between 1 and 100."
        self._override_speed = value

    @property
    def base_to_kin(self) -> TMatrix3:
        return self._base_to_kin

    @property
    def end_to_flange(self) -> TMatrix3:
        return self._end_to_flange

    def get_base_to_flange(self) -> Result[TMatrix3, KinematicsErr]:
        match self._kin_solver().forward(
            self.kinematics.dh_param, self.kinematics.get_joint_values()
        ):
            case Ok(value=t):
                return Ok(t @ self.end_to_flange)
            case Err() as err:
                return err

    def _kin_solver(self) -> KinematicsSolver:
        return KinematicsSolver.create(self._type)
