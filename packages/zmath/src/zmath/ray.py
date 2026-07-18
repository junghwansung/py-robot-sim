from .vector import Vector3


class Ray3:
    def __init__(self, origin: Vector3, direction: Vector3):
        self._origin: Vector3 = origin
        self._direction: Vector3 = direction.normalized()
