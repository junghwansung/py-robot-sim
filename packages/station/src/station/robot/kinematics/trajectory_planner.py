import math
from enum import Enum

from zmath.range import Range
from zutil.result import Err, Ok, Result

from .joint import Joint

"""
terms
- vel: joint velocity 
- accel: joint acceleration
- travel: from start position to target position of joint
- phase1: acceleration phase
- phase2: constant velocity phase
- phase3: deceleration phase
- accel_time: time taken to reach max velocity from rest
- delta_accel_phase: distance of phase1 + phase3
"""


class TrajectoryErr(str, Enum):
    OUT_OF_RANGE = "Joint value is out of range."


class VelocityProfiler:
    def __init__(self, accel_time: float, decel_time: float, const_vel: float):
        self._accel_time: float = accel_time
        self._decel_time: float = decel_time
        self._const_vel: float = const_vel


class TrajectoryPlanner:
    def __init__(self, joints: list[Joint]):
        self._joints: list[Joint] = joints

    @staticmethod
    def get_accel_time() -> float:
        """
        초기 조인트가 멈춰서 있을때 부터 최대 속도까지 도달하는데 걸리는 시간.
        제조사의 실제 가속도를 를 알 수 없으므로, 임으로 0.3초로 가정.
        시뮬레이션을 위한 근사적인 값.
        """
        return 0.3

    @staticmethod
    def calc_trapezoid_travel_time(
        joint: Joint, joint_travel: Range, accel_time: float
    ) -> Result[float, TrajectoryErr]:
        """
        주어진 조인트가 시작 위치에서 목표 위치까지 도달하는데 걸리는 시간 계산.
        `phase 1`: 등가속 구간.
        `phase 2`: 등속 구간.
        `phase 3`: 등감속 구간으로 나누어 계산.
        phase1과 phase3의 거리가 동일하다고 가정.
        `delta_accel_phase` 는 phase1과 phase3의 거리를 더한 거리를 의미.
        `delta_const_phase` 는 phase2의 거리를 의미.
        """
        limit: Range = joint.soft_limit
        if not limit.is_contain(joint_travel.min) or not limit.is_contain(joint_travel.max):
            return Err(TrajectoryErr.OUT_OF_RANGE)

        delta_travel = joint_travel.span()

        if delta_travel < 1e-6:
            return Ok(0.0)

        max_vel: float = joint.max_velocity
        accel: float = max_vel / accel_time

        # phase1과 phase3의 속도 및 거리 계산
        # v_accel = func(time) = accel * time
        # delta_accel = func(time) = 0.5 * accel * time^2

        # phase1과 phase3의 거리를 더한 거리 계산
        delta_accel_phase = accel_time * max_vel

        # 목표 위치가 최대 속도에 도달하기 전에 도달하는 경우
        if delta_travel < delta_accel_phase:
            return Ok(2 * math.sqrt(delta_travel / accel))

        # 목표 위치가 최대 속도에 도달한 후 도달하는 경우
        delta_const_phase = delta_travel - delta_accel_phase
        time_const_phase = delta_const_phase / max_vel
        return Ok(2 * accel_time + time_const_phase)

    @staticmethod
    def tune_trapezoid_vel_and_accel(
        delta_travel: float, travel_time: float, accel_time: float
    ) -> tuple[float, float]:
        """
        주어진 시작 위치와 목표 위치, 이동 시간, 가속 시간에 따라 새로운 등속 속도를 계산.
        """
        if delta_travel < 1e-6:
            return 0.0, 0.0

        tune_max_vel: float = delta_travel / (travel_time - accel_time)
        tune_accel: float = tune_max_vel / accel_time

        return tune_max_vel, tune_accel

    def get_longest_travel_time(
        self, travels: list[Range], accel_time: float
    ) -> Result[float, TrajectoryErr]:
        """
        주어진 조인트들의 이동 시간 중 가장 긴 시간을 반환.
        """
        assert len(travels) == len(self._joints), "Travels length must match joints length."

        travel_times: list[float] = []
        for joint, travel in zip(self._joints, travels):
            result = TrajectoryPlanner.calc_trapezoid_travel_time(joint, travel, accel_time)
            if isinstance(result, Err):
                return result
            travel_times.append(result.value)

        return Ok(max(travel_times))

    def define_velocity_profile(
        self, travels: list[Range], travel_time: float, accel_time: float
    ) -> Result[list[tuple[float, float]], TrajectoryErr]:
        """
        주어진 조인트들의 이동 거리와 이동 시간에 따라 각 조인트의 속도 및 가속도를 계산.
        """
        assert len(travels) == len(self._joints), "Travels length must match joints length."

        velocity_profiles: list[tuple[float, float]] = []
        for joint, travel in zip(self._joints, travels):
            delta_travel = travel.span()
            tune_max_vel, tune_accel = TrajectoryPlanner.tune_trapezoid_vel_and_accel(
                delta_travel, travel_time, accel_time
            )
            velocity_profiles.append((tune_max_vel, tune_accel))

        return Ok(velocity_profiles)
