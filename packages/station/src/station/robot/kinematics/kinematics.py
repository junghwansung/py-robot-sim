from station.base.constants import JointValues
from zmath.transform_matrix import TMatrix3
from zutil.result import Err, Ok, Result

from ..constants import ArmConfig, RobotType
from .dh_param import DHParam
from .joint import Joint
from .link import Link
from .solver import KinematicsErr, KinematicsSolver


class Kinematics:
    def __init__(self, robot_type: RobotType, dh_param: DHParam, links: list[Link]):
        if dh_param.dof != len(links):
            raise ValueError(
                "The number of links must match the degrees of freedom in DH parameters."
            )

        self._robot_type: RobotType = robot_type
        self._dh_param: DHParam = dh_param
        self._links: list[Link] = links

    @property
    def dof(self) -> int:
        return self._dh_param.dof

    @property
    def kin_type(self) -> RobotType:
        return self._robot_type

    @property
    def dh_param(self) -> DHParam:
        return self._dh_param

    def link(self, index: int) -> Link:
        assert 0 <= index < self.dof, "Index out of range for link list."
        return self._links[index]

    def joint(self, index: int) -> Joint:
        assert 0 <= index < self.dof, "Index out of range for joint list."
        return self._links[index].joint

    def get_joint_values(self) -> JointValues:
        return JointValues([link.joint.value for link in self._links])

    def set_joint_values(self, joint_values: JointValues) -> Result[None, KinematicsErr]:
        if len(joint_values) != self.dof:
            return Err(KinematicsErr.NO_JOINTS_IS_DIFFERENT)

        # 먼저 limit check, why? 되돌리는 코드를 넣어야하는데 비효율.
        for i, value in enumerate(joint_values):
            if not self.joint(i).soft_limit.is_contain(value):
                return Err(KinematicsErr.OUT_OF_JOINT_LIMITS)

        for i, value in enumerate(joint_values):
            self.joint(i).value = value

        return Ok(None)

    def get_end_pose(
        self, joint_values: JointValues, solver: KinematicsSolver | None = None
    ) -> Result[TMatrix3, KinematicsErr]:
        # currently, only support 6DOF serial robot
        assert self.kin_type == RobotType.SERIAL_6DOF, "IK is only supported for 6DOF."

        if solver is None:
            solver = KinematicsSolver.create(self.kin_type)

        return solver.forward(self.dh_param, joint_values)

    def get_joint_values_from_pose(
        self, target: TMatrix3, arm_config: ArmConfig, solver: KinematicsSolver | None = None
    ) -> Result[JointValues, KinematicsErr]:
        # currently, only support 6DOF serial robot
        assert self.kin_type == RobotType.SERIAL_6DOF, "IK is only supported for 6DOF."

        if solver is None:
            solver = KinematicsSolver.create(self.kin_type)

        return solver.inverse(self.dh_param, target, arm_config)
