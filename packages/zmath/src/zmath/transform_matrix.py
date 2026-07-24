import numpy as np
from scipy.spatial.transform import Rotation as R

from .vector import Vector2, Vector3


class TMatrix3:
    """
    mutable transformation homogeneous matrix for 3D transformations.
    last row is implicitly [0, 0, 0, 1] for homogeneous coordinates
    so we only store the upper 3 rows

    private attributes:
        - rotation: 3x3 rotation matrix
        - position: 3D translation vector

    should be used
        - unit is in meters and radians
        - right-handed coordinate system

    Example usage:
        - create identity transform:
            a_to_b: TMatrix3 = TMatrix3.identity()

        - create transform from euler angles:
            tm = TMatrix3.from_euler_xyz(np.radians(30), np.radians(45), np.radians(60), Vector3(1, 2, 3))

        - invert a transform in-place:
            inv_tm = tm.invert()

        - return the inverse of a transform as a new TMatrix3:
            inv_tm = tm.inverse()
    """

    __slots__ = ("_position", "_rotation")
    _rotation: R
    _position: Vector3

    def __init__(self, rotation: R, position: Vector3):
        if not isinstance(rotation, R):
            raise TypeError("rotation must be scipy.spatial.transform.Rotation")
        if not isinstance(position, Vector3):
            raise TypeError("position must be Vector3")

        # Keep internal state independent from externally shared Rotation instances.
        object.__setattr__(self, "_rotation", R.from_quat(rotation.as_quat()))
        object.__setattr__(self, "_position", position.copy())

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"rotation", "position", "_rotation", "_position"}:
            raise AttributeError(
                "Direct assignment is not allowed. Use set_pose(), set_rotation(), or set_position()"
            )
        object.__setattr__(self, name, value)

    @classmethod
    def identity(cls) -> "TMatrix3":
        """identity matrix"""
        return cls(R.from_euler("xyz", [0, 0, 0]), Vector3())

    @classmethod
    def from_euler_xyz(
        cls, rx: float, ry: float, rz: float, position: Vector3 | None = None
    ) -> "TMatrix3":
        """create a TMatrix3 from translation (x, y, z) and euler angles (rx, ry, rz in radians)"""
        if position is None:
            position = Vector3.zero()
        rot = R.from_euler("xyz", [rx, ry, rz])
        return cls(rot, position)

    @classmethod
    def from_euler_zyx(
        cls, rz: float, ry: float, rx: float, position: Vector3 | None = None
    ) -> "TMatrix3":
        """create a TMatrix3 from translation (x, y, z) and euler angles (rz, ry, rx in radians)"""
        if position is None:
            position = Vector3.zero()
        rot = R.from_euler("zyx", [rz, ry, rx])
        return cls(rot, position)

    @classmethod
    def from_euler_zyz(
        cls, rz1: float, ry: float, rz2: float, position: Vector3 | None = None
    ) -> "TMatrix3":
        """create a TMatrix3 from translation (x, y, z) and euler angles (rz1, ry, rz2 in radians)"""
        if position is None:
            position = Vector3.zero()
        rot = R.from_euler("zyz", [rz1, ry, rz2])
        return cls(rot, position)

    @classmethod
    def from_quaternion(
        cls, q: list[float] | np.ndarray, position: Vector3 | None = None
    ) -> "TMatrix3":
        """
        create a TMatrix3 from translation (x, y, z) and quaternion (qx, qy, qz, qw)
        """
        if position is None:
            position = Vector3.zero()
        rot = R.from_quat(q)
        return cls(rot, position)

    @classmethod
    def from_4by4_row_major(cls, values: list[list[float]]) -> "TMatrix3":
        """create a TMatrix3 from list data [[...], [...], [...] ,[...]]"""
        mat = np.array(values, dtype=float)
        return cls(R.from_matrix(mat[:3, :3]), Vector3.from_array(mat[:3, 3]))

    @classmethod
    def from_flat_row_major(cls, values: list[float]) -> "TMatrix3":
        """create a TMatrix3 from list data [....]"""
        mat = np.array(values, dtype=float).reshape(4, 4)
        return cls(R.from_matrix(mat[:3, :3]), Vector3.from_array(mat[:3, 3]))

    def to_quaternion(self) -> list[float]:
        """return the rotation as a quaternion (qx, qy, qz, qw)"""
        return list(self._rotation.as_quat())

    def to_euler_xyz(self) -> list[float]:
        """return the rotation as euler angles (rx, ry, rz in radians)"""
        return list(self._rotation.as_euler("xyz"))

    def to_euler_zyx(self) -> list[float]:
        """return the rotation as euler angles (rz, ry, rx in radians)"""
        return list(self._rotation.as_euler("zyx"))

    def to_euler_zyz(self) -> list[float]:
        """return the rotation as euler angles (rz1, ry, rz2 in radians)"""
        return list(self._rotation.as_euler("zyz"))

    def to_matrix(self) -> list[list[float]]:
        """return the 4x4 transformation matrix as a nested list"""
        mat = np.zeros((4, 4), dtype=float)
        mat[:3, :3] = self._rotation.as_matrix()
        mat[:3, 3] = self._position.to_tuple()
        mat[3, 3] = 1.0
        return mat.tolist()

    def to_column_major_matrix(self) -> list[list[float]]:
        """return the 4x4 transformation matrix as a nested list in column-major order"""
        mat = np.zeros((4, 4), dtype=float)
        mat[:3, :3] = self._rotation.as_matrix()
        mat[:3, 3] = self._position.to_tuple()
        mat[3, 3] = 1.0
        return mat.T.tolist()

    @property
    def position(self) -> Vector3:
        """read-only translation component"""
        return self._position.copy()

    @property
    def rotation(self) -> R:
        """read-only rotation component as a defensive copy"""
        return self._rotation

    def copy(self) -> "TMatrix3":
        """return a mutable copy of this transform"""
        return type(self)(self._rotation, self._position.copy())

    def set_position(self, position: Vector3) -> None:
        """update position in-place"""
        if not isinstance(position, Vector3):
            raise TypeError("position must be Vector3")
        object.__setattr__(self, "_position", position.copy())

    def set_rotation(self, rotation: R) -> None:
        """update rotation in-place"""
        if not isinstance(rotation, R):
            raise TypeError("rotation must be scipy.spatial.transform.Rotation")
        object.__setattr__(self, "_rotation", R.from_quat(rotation.as_quat()))

    def n(self) -> Vector3:
        """return the forward direction (x-axis) as a Vector3"""
        return Vector3.from_array(self._rotation.as_matrix()[:, 0])

    def o(self) -> Vector3:
        """return the right direction (y-axis) as a Vector3"""
        return Vector3.from_array(self._rotation.as_matrix()[:, 1])

    def a(self) -> Vector3:
        """return the up direction (z-axis) as a Vector3"""
        return Vector3.from_array(self._rotation.as_matrix()[:, 2])

    def inverse(self) -> "TMatrix3":
        """return the inverse of the TMatrix3"""
        inv_rotation = self._rotation.inv()
        inv_position = -inv_rotation.apply(self._position.to_tuple())
        return type(self)(inv_rotation, Vector3.from_array(inv_position))

    def invert(self) -> "TMatrix3":
        """invert the TMatrix3 in-place"""
        inv_rotation = self._rotation.inv()
        inv_position = -inv_rotation.apply(self._position.to_tuple())
        object.__setattr__(self, "_rotation", inv_rotation)
        object.__setattr__(self, "_position", Vector3.from_array(inv_position))
        return self

    def translate_local(self, translation: Vector3) -> "TMatrix3":
        """translate the TMatrix3 in-place by the given translation vector"""
        new_position = self._position + self._rotation.apply(translation.to_tuple())
        self.set_position(Vector3.from_array(new_position))
        return self

    def translate_world(self, translation: Vector3) -> "TMatrix3":
        """translate the TMatrix3 in-place by the given translation vector in world coordinates"""
        new_position = self._position + translation
        self.set_position(new_position)
        return self

    def rotate_x_local(self, angle: float) -> "TMatrix3":
        """apply local x-axis rotation in-place"""
        rot = R.from_euler("x", angle)
        self.set_rotation(rot * self._rotation)
        return self

    def rotate_y_local(self, angle: float) -> "TMatrix3":
        """apply local y-axis rotation in-place"""
        rot = R.from_euler("y", angle)
        self.set_rotation(rot * self._rotation)
        return self

    def rotate_z_local(self, angle: float) -> "TMatrix3":
        """apply local z-axis rotation in-place"""
        rot = R.from_euler("z", angle)
        self.set_rotation(rot * self._rotation)
        return self

    def rotate_x_world(self, angle: float) -> "TMatrix3":
        """apply world x-axis rotation in-place"""
        rot = R.from_euler("x", angle)
        self.set_rotation(self._rotation * rot)
        return self

    def rotate_y_world(self, angle: float) -> "TMatrix3":
        """apply world y-axis rotation in-place"""
        rot = R.from_euler("y", angle)
        self.set_rotation(self._rotation * rot)
        return self

    def rotate_z_world(self, angle: float) -> "TMatrix3":
        """apply world z-axis rotation in-place"""
        rot = R.from_euler("z", angle)
        self.set_rotation(self._rotation * rot)
        return self

    def compose_all(self, transforms: list["TMatrix3"]) -> list["TMatrix3"]:
        """return a list of TMatrix3 results from composing this TMatrix3 with each TMatrix3 in the input list"""
        return [self @ tm for tm in transforms]

    def transform_points(self, points: list[Vector3]) -> list[Vector3]:
        """return a list of Vector3 results from transforming each point in the input list by this TMatrix3"""
        return [self * point for point in points]

    def __matmul__(self, other: "TMatrix3") -> "TMatrix3":
        """TMatrix3 @ TMatrix3 -> TMatrix3 (matrix multiplication)"""
        if isinstance(other, TMatrix3):
            new_rotation = self._rotation * other._rotation
            new_position = self._position + self._rotation.apply(other._position.to_tuple())
            return type(self)(new_rotation, new_position)
        else:
            raise TypeError("Unsupported type for matrix multiplication with TMatrix3")

    def __mul__(self, other: Vector3) -> Vector3:
        """TMatrix3 * Vector3 -> Vector3 (transform a point)"""
        if isinstance(other, Vector3):
            return Vector3.from_array(
                self._rotation.apply(other.to_tuple()) + self._position.to_tuple()
            )
        else:
            raise TypeError("Unsupported type for multiplication with TMatrix3")


class TMatrix2:
    """
    mutable transformation homogeneous matrix for 2D transformations.
    last row is implicitly [0, 0, 1] for homogeneous coordinates
    so we only store the upper 2 rows

    private attributes:
        - rotation: 2x2 rotation matrix
        - position: 2D translation vector
    """

    __slots__ = ("_position", "_rotation")
    _rotation: float
    _position: Vector2

    def __init__(self, rotation: float, position: Vector2):
        if not isinstance(rotation, (int, float)):
            raise TypeError("rotation must be a float")
        if not isinstance(position, Vector2):
            raise TypeError("position must be Vector2")

        # Keep internal state independent from externally shared Rotation instances.
        object.__setattr__(self, "_rotation", rotation)
        object.__setattr__(self, "_position", position.copy())

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"rotation", "position", "_rotation", "_position"}:
            raise AttributeError(
                "Direct assignment is not allowed. Use set_pose(), set_rotation(), or set_position()"
            )
        object.__setattr__(self, name, value)

    @classmethod
    def identity(cls) -> "TMatrix2":
        """identity matrix"""
        return cls(0.0, Vector2())

    def to_matrix(self) -> list[list[float]]:
        """return the 3x3 transformation matrix as a nested list"""
        cos_theta = np.cos(self._rotation)
        sin_theta = np.sin(self._rotation)
        mat = np.zeros((3, 3), dtype=float)
        mat[0, 0] = cos_theta
        mat[0, 1] = -sin_theta
        mat[1, 0] = sin_theta
        mat[1, 1] = cos_theta
        mat[0, 2] = self._position.x
        mat[1, 2] = self._position.y
        mat[2, 2] = 1.0
        return mat.tolist()

    def __matmul__(self, other: "TMatrix2") -> "TMatrix2":
        """TMatrix2 @ TMatrix2 -> TMatrix2 (matrix multiplication)"""
        if isinstance(other, TMatrix2):
            new_rotation = self._rotation + other._rotation
            new_position = self._position + Vector2(
                np.cos(self._rotation) * other._position.x
                - np.sin(self._rotation) * other._position.y,
                np.sin(self._rotation) * other._position.x
                + np.cos(self._rotation) * other._position.y,
            )
            return type(self)(new_rotation, new_position)
        else:
            raise TypeError("Unsupported type for multiplication with TMatrix2")

    def __mul__(self, other: Vector2) -> Vector2:
        """TMatrix2 * Vector2 -> Vector2 (transform a point)"""
        if isinstance(other, Vector2):
            return Vector2(
                np.cos(self._rotation) * other.x
                - np.sin(self._rotation) * other.y
                + self._position.x,
                np.sin(self._rotation) * other.x
                + np.cos(self._rotation) * other.y
                + self._position.y,
            )
        else:
            raise TypeError("Unsupported type for multiplication with TMatrix2")
