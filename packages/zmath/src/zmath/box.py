import math

from .size import Size2, Size3
from .transform_matrix import TMatrix3
from .vector import Vector2, Vector3


class Box2:
    """immutable 2D box defined by width and height"""

    def __init__(self, width: float, height: float, center: Vector2 = Vector2.zero()):
        self._size: Size2 = Size2(width, height)
        self._center: Vector2 = center

    @classmethod
    def from_corners(cls, corners: list[Vector2]) -> "Box2":
        """create a Box2 from 4 corners in CCW order starting from left-top.
        position stores the center of the box."""
        assert len(corners) == 4

        x_values: list[float] = [v.x for v in corners]
        y_values: list[float] = [v.y for v in corners]
        width = max(x_values) - min(x_values)
        height = max(y_values) - min(y_values)
        return cls(
            width,
            height,
            Vector2((max(x_values) + min(x_values)) / 2, (max(y_values) + min(y_values)) / 2),
        )

    def to_corners(self) -> list[list[float]]:
        half_width: float = self.width / 2
        half_height: float = self.height / 2
        left: float = self.center.x - half_width
        right: float = self.center.x + half_width
        top: float = self.center.y - half_height
        bottom: float = self.center.y + half_height

        corners: list[list[float]] = [[left, bottom], [right, bottom], [right, top], [left, top]]
        return corners

    @property
    def size(self) -> Size2:
        """return the size of the box"""
        return self._size

    @property
    def width(self) -> float:
        """return the width of the box"""
        return self._size.width

    @property
    def height(self) -> float:
        """return the height of the box"""
        return self._size.height

    @property
    def center(self) -> Vector2:
        """return the position"""
        return self._center

    @property
    def area(self) -> float:
        """return the area of the box"""
        return self._size.area()

    @property
    def perimeter(self) -> float:
        """return the perimeter of the box"""
        return 2 * (self._size.width + self._size.height)

    @property
    def diagonal(self) -> float:
        """return the length of the diagonal of the box"""
        return math.sqrt(self._size.width**2 + self._size.height**2)

    @property
    def aspect_ratio(self) -> float:
        """return the aspect ratio of the box (width / height)"""
        if self._size.height == 0:
            raise ValueError("Height cannot be zero for aspect ratio calculation")
        return self._size.width / self._size.height

    @property
    def is_square(self) -> bool:
        """return True if the box is a square, False otherwise"""
        return self._size.width == self._size.height

    @property
    def is_rectangle(self) -> bool:
        """return True if the box is a rectangle (not a square), False otherwise"""
        return self._size.width != self._size.height

    def is_close(self, other: "Box2", thereshold_size: float, threshold_position: float) -> bool:
        return (
            abs(self._size.width - other.width) <= thereshold_size
            and abs(self._size.height - other.height) <= thereshold_size
            and abs(self.center.x - other.center.x) <= threshold_position
            and abs(self.center.y - other.center.y) <= threshold_position
        )

    def __str__(self) -> str:
        return f"Box2({self._size.width}, {self._size.height})"

    def __repr__(self) -> str:
        return f"Box2({self._size.width}, {self._size.height})"


class Box3:
    """immutable 3D box defined by width, length, and height"""

    def __init__(
        self, width: float, length: float, height: float, pose: TMatrix3 = TMatrix3.identity()
    ):
        # ponytail: Size3 uses (width, height, depth); length maps to depth here
        self._size: Size3 = Size3(width, height, length)
        self._pose: TMatrix3 = pose

    @classmethod
    def from_corners(cls, corners: list[Vector3]) -> "Box3":
        """create a Box3 from 8 corners.
        position stores the center of the box."""
        assert len(corners) == 8

        x_values: list[float] = [v.x for v in corners]
        y_values: list[float] = [v.y for v in corners]
        z_values: list[float] = [v.z for v in corners]

        width: float = max(x_values) - min(x_values)
        height: float = max(y_values) - min(y_values)
        length: float = max(z_values) - min(z_values)

        return cls(
            width,
            length,
            height,
            TMatrix3.from_euler_xyz(
                0,
                0,
                0,
                Vector3.from_xyz(
                    (max(x_values) + min(x_values)) / 2,
                    (max(y_values) + min(y_values)) / 2,
                    (max(z_values) + min(z_values)) / 2,
                ),
            ),
        )

    @property
    def size(self) -> Size3:
        """return the size of the box"""
        return self._size

    @property
    def width(self) -> float:
        """return the width of the box"""
        return self._size.width

    @property
    def height(self) -> float:
        """return the height of the box"""
        return self._size.height

    @property
    def length(self) -> float:
        """return the length of the box"""
        return self._size.depth

    @property
    def pose(self) -> TMatrix3:
        return self._pose

    @property
    def center(self) -> Vector3:
        return self._pose.position

    @property
    def volume(self) -> float:
        """return the volume of the box"""
        return self._size.volume()

    @property
    def surface_area(self) -> float:
        """return the surface area of the box"""
        w, h, l = self._size.width, self._size.height, self._size.depth
        return 2 * (w * h + w * l + h * l)

    @property
    def diagonal(self) -> float:
        """return the length of the diagonal of the box"""
        return math.sqrt(self._size.width**2 + self._size.height**2 + self._size.depth**2)

    def is_close_size(self, other: "Box3", thereshold_size: float) -> bool:
        return (
            abs(self.length - other.length) <= thereshold_size
            and abs(self.width - other.width) <= thereshold_size
            and abs(self.height - other.height) <= thereshold_size
        )

    def is_close_position(self, other: "Box3", threshold_position: float) -> bool:
        center: Vector3 = self.center
        other_center: Vector3 = other.center
        return (
            abs(center.x - other_center.x) <= threshold_position
            and abs(center.y - other_center.y) <= threshold_position
            and abs(center.z - other_center.z) <= threshold_position
        )

    def __str__(self) -> str:
        return f"Box3({self._size.width}, {self._size.height}, {self._size.depth})"

    def __repr__(self) -> str:
        return f"Box3({self._size.width}, {self._size.height}, {self._size.depth})"
