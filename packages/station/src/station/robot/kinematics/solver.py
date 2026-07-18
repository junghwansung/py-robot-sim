from abc import abstractmethod
from enum import Enum
from math import atan2, cos, sin, sqrt

from station.base.constants import JointValues
from station.robot.constants import ArmConfig
from zmath.transform_matrix import TMatrix3
from zmath.trigonometric import solve_sin_cos_combination
from zmath.vector import Vector3
from zutil.result import Err, Ok, Result

from .. import RobotType
from .dh_param import DHParam


class KinematicsErr(int, Enum):
    OUT_OF_JOINT_LIMITS = 0
    NO_JOINTS_IS_DIFFERENT = 1
    FORWARD_KINEMATICS_INPUT_ERROR = 2
    INVERSE_KINEMATICS_NOT_REACHABLE = 3
    INVERSE_KINEMATICS_SINGULARITY = 4
    INVERSE_KINEMATICS_NOT_CONVERGED = 5


class KinematicsSolver:
    def __init__(self):
        pass

    @classmethod
    def create(cls, robot_type: RobotType) -> "KinematicsSolver":
        if robot_type == RobotType.SERIAL_6DOF:
            return Serial6DofSolver(robot_type)

        raise NotImplementedError(
            f"Kinematics solver for robot type {robot_type} is not implemented."
        )

    @abstractmethod
    def forward(self, dh_param: DHParam, joints: JointValues) -> Result[TMatrix3, KinematicsErr]:
        raise NotImplementedError

    @abstractmethod
    def inverse(self, dh_param: DHParam, target: TMatrix3) -> Result[JointValues, KinematicsErr]:
        raise NotImplementedError


class Serial6DofSolver(KinematicsSolver):

    def forward(self, dh_param: DHParam, joints: JointValues) -> Result[TMatrix3, KinematicsErr]:
        k_dof: int = 6
        if dh_param.dof != k_dof or len(joints) != k_dof:
            return Err(KinematicsErr.NO_JOINTS_IS_DIFFERENT)

        zero_to_six: TMatrix3 = TMatrix3.identity()
        for link, joint_value in zip(dh_param, joints):
            zero_to_six = zero_to_six @ link.next(joint_value)

        return Ok(zero_to_six)

    def inverse(
        self, dh_param: DHParam, target: TMatrix3, arm_config: ArmConfig
    ) -> Result[JointValues, KinematicsErr]:

        # 2_to_6 = (0_to_2)^-1 * target
        position: Vector3 = target.position

        shoulder: float = arm_config.shoulder
        elbow: float = arm_config.elbow
        wrist: float = arm_config.wrist

        # theta1
        p = position.y
        q = -position.x
        r = dh_param[1].d
        theta1: float = solve_sin_cos_combination(p, q, r, shoulder)

        # theta2, theta3
        A = cos(theta1) * position.x + sin(theta1) * position.y - dh_param[0].a
        B = position.z - dh_param[0].d
        p = dh_param[2].a
        q = dh_param[3].d
        r = (dh_param[1].a ** 2 + dh_param[2].a ** 2 + dh_param[3].d ** 2 - A**2 - B**2) / (
            2.0 * dh_param[1].a
        )
        theta3: float = solve_sin_cos_combination(p, q, r, elbow)

        E = dh_param[1].a + dh_param[2].a * cos(theta3) + dh_param[3].d * sin(theta3)
        F = dh_param[3].d * cos(theta3) - dh_param[2].a * sin(theta3)

        cos_theta2: float = (A * F + B * E) / (A**2 + B**2)
        sin_theta2: float = (B * F - A * E) / (A**2 + B**2)
        theta2: float = atan2(sin_theta2, cos_theta2)

        C = sin(theta1) * target.a().x - cos(theta1) * target.a().y
        cos_theta5 = -B
        sin_theta5 = wrist * sqrt(A**2 + C**2)
        theta5: float = atan2(sin_theta5, cos_theta5)

        cos_theta4 = A / sin_theta5
        sin_theta4 = C / sin_theta5
        theta4: float = atan2(sin_theta4, cos_theta4)

        n = target.n()
        o = target.o()
        theta23 = theta2 + theta3
        s23, c23 = sin(theta23), cos(theta23)
        s1, c1 = sin(theta1), cos(theta1)

        D = -c1 * c23 * n.x - s1 * c23 * n.y - s23 * n.z
        E = -c1 * c23 * o.x - s1 * c23 * o.y - s23 * o.z
        cos_theta6 = D / sin_theta5
        sin_theta6 = -E / sin_theta5
        theta6: float = atan2(sin_theta6, cos_theta6)

        return Ok(JointValues([theta1, theta2, theta3, theta4, theta5, theta6]))
