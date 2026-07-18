from .vector import Vector3


class AABB:
    """Axis-Aligned Bounding Box"""

    def __init__(self, min_point: Vector3, max_point: Vector3):
        self.min_point = min_point
        self.max_point = max_point


class OBB:
    """Oriented Bounding Box"""

    def __init__(self, center: Vector3, half_extents: Vector3, rotation: Vector3):
        self.center = center
        self.half_extents = half_extents
        self.rotation = rotation
