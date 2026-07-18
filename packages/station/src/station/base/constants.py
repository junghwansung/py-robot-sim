from station.base.types import ArmConfig

ARM_CONFIG_NO: list[ArmConfig] = [
    ArmConfig(shoulder=+1, elbow=+1, wrist=+1),  # 0
    ArmConfig(shoulder=+1, elbow=+1, wrist=-1),  # 1
    ArmConfig(shoulder=+1, elbow=-1, wrist=+1),  # 2
    ArmConfig(shoulder=+1, elbow=-1, wrist=-1),  # 3
    ArmConfig(shoulder=-1, elbow=+1, wrist=+1),  # 4
    ArmConfig(shoulder=-1, elbow=+1, wrist=-1),  # 5
    ArmConfig(shoulder=-1, elbow=-1, wrist=+1),  # 6
    ArmConfig(shoulder=-1, elbow=-1, wrist=-1),  # 7
]
