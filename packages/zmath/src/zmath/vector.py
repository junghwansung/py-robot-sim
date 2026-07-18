"""
2D/3D vector class with basic vector operations
"""

import math
from numbers import Real

import numpy as np


class Vector2:
    """
    2D vector class with basic vector operations

    x - x component, unit is mm
    y - y component, unit is mm

    should be used
        - for representing points, directions, and translations in 2D space
        - for vector math operations like addition, subtraction, dot product, etc.
    """

    __slots__ = ("_x", "_y")
    _x: float
    _y: float

    def __init__(self, x: float = 0.0, y: float = 0.0):
        if not all(isinstance(value, Real) for value in (x, y)):
            raise TypeError("x and y must be real numbers")

        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"x", "y", "_x", "_y"}:
            raise AttributeError("Direct assignment is not allowed. Use set_xy()")

        object.__setattr__(self, name, value)

    @classmethod
    def from_array(cls, arr: list[float] | tuple[float, float] | np.ndarray) -> "Vector2":
        """create a Vector2 from an array-like with 2 elements"""
        if len(arr) != 2:
            raise ValueError("Array must have exactly 2 elements")
        return cls(*arr)

    @classmethod
    def from_xy(cls, x: float, y: float) -> "Vector2":
        """create a Vector2 from x and y components"""
        return cls(x, y)

    @classmethod
    def zero(cls) -> "Vector2":
        """return a zero vector"""
        return cls(0.0, 0.0)

    @property
    def x(self) -> float:
        """return the x component of the vector"""
        return self._x

    @property
    def y(self) -> float:
        """return the y component of the vector"""
        return self._y

    def set_xy(self, x: float, y: float) -> None:
        """update vector components in-place"""
        if not all(isinstance(value, Real) for value in (x, y)):
            raise TypeError("x and y must be real numbers")
        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)

    @staticmethod
    def center(vectors: list["Vector2"] | tuple["Vector2", ...]) -> "Vector2":
        """return the centroid of a list of Vector2 objects"""
        if not vectors:
            raise ValueError("vectors list must not be empty")
        if not all(isinstance(vec, Vector2) for vec in vectors):
            raise TypeError("vectors list must contain only Vector2 objects")
        sum_x = sum(vec.x for vec in vectors)
        sum_y = sum(vec.y for vec in vectors)
        count = len(vectors)
        return Vector2(sum_x / count, sum_y / count)

    def to_list(self) -> list[float]:
        """Vector2 -> list"""
        return [self.x, self.y]

    def to_tuple(self) -> tuple[float, float]:
        """Vector2 -> tuple"""
        return (self.x, self.y)

    def copy(self) -> "Vector2":
        """return a mutable copy of this vector"""
        return type(self).from_xy(self.x, self.y)

    def squared_length(self) -> float:
        """return the squared length of the vector"""
        return self.x**2 + self.y**2

    def length(self) -> float:
        """return the length of the vector"""
        return math.sqrt(self.squared_length())

    def normalized(self) -> "Vector2":
        """return a new normalized vector"""
        length: float = self.length()
        if math.isclose(length, 0.0):
            raise ValueError("Cannot normalize a zero-length vector")
        return type(self).from_xy(self.x / length, self.y / length)

    def normalize(self) -> "Vector2":
        """normalize this vector in-place (alias for normalize_ip())"""
        length: float = self.length()
        if math.isclose(length, 0.0):
            raise ValueError("Cannot normalize a zero-length vector")
        self.set_xy(self.x / length, self.y / length)
        return self

    def distance_to(self, other: "Vector2") -> float:
        """distance between two points represented by vectors"""
        return (self - other).length()

    def angle_with(self, other: "Vector2") -> float:
        """return the angle to another vector in radians"""
        len_product: float = self.length() * other.length()
        if math.isclose(len_product, 0.0):
            raise ValueError("Cannot compute angle with a zero-length vector")
        # Clamp due to floating point drift so acos domain stays valid.
        return math.acos(max(-1.0, min(1.0, self.dot(other) / len_product)))

    def dot(self, other: "Vector2") -> float:
        """Vector2 · Vector2 -> float"""
        return self.x * other.x + self.y * other.y

    def lerp(self, other: "Vector2", t: float) -> "Vector2":
        """linear interpolation between this vector and another by t (t=0 -> self, t=1 -> other)"""
        if not isinstance(t, Real):
            raise TypeError("t must be a real number")
        return type(self).from_xy(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    def __eq__(self, other: object) -> bool:
        """Vector2 == Vector2 -> bool (exact equality)"""
        if not isinstance(other, Vector2):
            return NotImplemented

        return bool(math.isclose(self.x, other.x) and math.isclose(self.y, other.y))

    def __neg__(self) -> "Vector2":
        """Vector2 -> Vector2 (negation)"""
        return type(self).from_xy(-self.x, -self.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        """Vector2 - Vector2 -> Vector2"""
        return type(self).from_xy(self.x - other.x, self.y - other.y)

    def __isub__(self, other: "Vector2") -> "Vector2":
        """Vector2 -= Vector2 -> Vector2"""
        self.set_xy(self.x - other.x, self.y - other.y)
        return self

    def __add__(self, other: "Vector2") -> "Vector2":
        """Vector2 + Vector2 -> Vector2"""
        return type(self).from_xy(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: "Vector2") -> "Vector2":
        """Vector2 += Vector2 -> Vector2"""
        self.set_xy(self.x + other.x, self.y + other.y)
        return self

    def __mul__(self, scalar: float) -> "Vector2":
        """Vector2 * scalar -> Vector2"""
        if not isinstance(scalar, Real):
            return NotImplemented
        return type(self).from_xy(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2":
        """scalar * Vector2 -> Vector2"""
        return self.__mul__(scalar)

    def __imul__(self, scalar: float) -> "Vector2":
        """Vector2 *= scalar -> Vector2"""
        if not isinstance(scalar, Real):
            return NotImplemented
        self.set_xy(self.x * scalar, self.y * scalar)
        return self

    def __truediv__(self, scalar: float) -> "Vector2":
        """Vector2 / scalar -> Vector2"""
        if not isinstance(scalar, Real):
            return NotImplemented
        if math.isclose(float(scalar), 0.0):
            raise ValueError("Cannot divide by zero")
        return type(self).from_xy(self.x / scalar, self.y / scalar)

    def __itruediv__(self, scalar: float) -> "Vector2":
        """Vector2 /= scalar -> Vector2"""
        if not isinstance(scalar, Real):
            return NotImplemented
        if math.isclose(float(scalar), 0.0):
            raise ValueError("Cannot divide by zero")
        self.set_xy(self.x / scalar, self.y / scalar)
        return self

    def __str__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"


class Vector3:
    """
    mutable 3D vector class with controlled updates

    x - x component, unit is mm
    y - y component, unit is mm
    z - z component, unit is mm

    should be used
        - for representing points, directions, and translations in 3D space
        - for vector math operations like addition, subtraction, dot product, cross product, etc.

    Example usage:
    v1 = Vector3(1, 2, 3)
    v2 = Vector3(4, 5, 6)
    v3 = v1 + v2  # Vector3(5, 7, 9)
    v4 = v1.cross(v2)  # Vector3(-3, 6, -3)
    v5 = v1.normalized()  # Vector3(0.2672612419124244, 0.5345224838248488, 0.8017837257372732)

    """

    __slots__ = ("_x", "_y", "_z")
    _x: float
    _y: float
    _z: float

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        if not all(isinstance(value, Real) for value in (x, y, z)):
            raise TypeError("x, y, z must be real numbers")

        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)
        object.__setattr__(self, "_z", z)

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"x", "y", "z", "_x", "_y", "_z"}:
            raise AttributeError("Direct assignment is not allowed. Use set_xyz()")

        object.__setattr__(self, name, value)

    @classmethod
    def from_array(cls, arr: list[float] | tuple[float, float, float] | np.ndarray) -> "Vector3":
        """create a Vector3 from an array-like with 3 elements"""
        if len(arr) != 3:
            raise ValueError("Array must have exactly 3 elements")
        return cls(*arr)

    @classmethod
    def from_xyz(cls, x: float, y: float, z: float) -> "Vector3":
        """create a Vector3 from x, y, z components"""
        return cls(x, y, z)

    @classmethod
    def zero(cls) -> "Vector3":
        """return a zero vector"""
        return cls(0.0, 0.0, 0.0)

    @property
    def x(self) -> float:
        """return the x component of the vector"""
        return self._x

    @property
    def y(self) -> float:
        """return the y component of the vector"""
        return self._y

    @property
    def z(self) -> float:
        """return the z component of the vector"""
        return self._z

    def set_xyz(self, x: float, y: float, z: float) -> None:
        """update vector components in-place"""
        if not all(isinstance(value, Real) for value in (x, y, z)):
            raise TypeError("x, y, z must be real numbers")
        object.__setattr__(self, "_x", x)
        object.__setattr__(self, "_y", y)
        object.__setattr__(self, "_z", z)

    def to_list(self) -> list[float]:
        """Vector3 -> list"""
        return [self.x, self.y, self.z]

    def to_tuple(self) -> tuple[float, float, float]:
        """Vector3 -> tuple"""
        return (self.x, self.y, self.z)

    def copy(self) -> "Vector3":
        """return a mutable copy of this vector"""
        return type(self).from_xyz(self.x, self.y, self.z)

    def squared_length(self) -> float:
        """return the squared length of the vector"""
        return self.x**2 + self.y**2 + self.z**2

    def length(self) -> float:
        """return the length of the vector"""
        return math.sqrt(self.squared_length())

    def normalized(self) -> "Vector3":
        """return a new normalized vector"""
        length: float = self.length()
        if math.isclose(length, 0.0):
            raise ValueError("Cannot normalize a zero-length vector")
        return type(self).from_xyz(self.x / length, self.y / length, self.z / length)

    def normalize(self) -> "Vector3":
        """normalize this vector in-place (alias for normalize_ip())"""
        length: float = self.length()
        if math.isclose(length, 0.0):
            raise ValueError("Cannot normalize a zero-length vector")
        self.set_xyz(self.x / length, self.y / length, self.z / length)
        return self

    def distance_to(self, other: "Vector3") -> float:
        """distance between two points represented by vectors"""
        return (self - other).length()

    def angle_with(self, other: "Vector3") -> float:
        """return the angle to another vector in radians"""
        len_product: float = self.length() * other.length()
        if math.isclose(len_product, 0.0):
            raise ValueError("Cannot compute angle with a zero-length vector")
        # Clamp due to floating point drift so acos domain stays valid.
        return math.acos(max(-1.0, min(1.0, self.dot(other) / len_product)))

    def dot(self, other: "Vector3") -> float:
        """Vector3 · Vector3 -> float"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vector3") -> "Vector3":
        """Vector3 x Vector3 -> Vector3"""
        cx = self.y * other.z - self.z * other.y
        cy = self.z * other.x - self.x * other.z
        cz = self.x * other.y - self.y * other.x
        return type(self).from_xyz(cx, cy, cz)

    def lerp(self, other: "Vector3", t: float) -> "Vector3":
        """linear interpolation between this vector and another by t (t=0 -> self, t=1 -> other)"""
        if not isinstance(t, Real):
            raise TypeError("t must be a real number")
        return type(self).from_xyz(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
        )

    def __eq__(self, other: object) -> bool:
        """Vector3 == Vector3 -> bool (exact equality)"""
        if not isinstance(other, Vector3):
            return NotImplemented

        return bool(
            np.isclose(self.x, other.x)
            and np.isclose(self.y, other.y)
            and np.isclose(self.z, other.z)
        )

    def __ne__(self, other: object) -> bool:
        """Vector3 != Vector3 -> bool"""
        eq_result = self.__eq__(other)
        if eq_result is NotImplemented:
            return NotImplemented

        return not eq_result

    def __neg__(self) -> "Vector3":
        """-Vector3 -> Vector3"""
        return type(self).from_xyz(-self.x, -self.y, -self.z)

    def __sub__(self, other: "Vector3") -> "Vector3":
        """Vector3 - Vector3 -> Vector3"""
        return type(self).from_xyz(self.x - other.x, self.y - other.y, self.z - other.z)

    def __isub__(self, other: "Vector3") -> "Vector3":
        """Vector3 -= Vector3 -> Vector3"""
        self.set_xyz(self.x - other.x, self.y - other.y, self.z - other.z)
        return self

    def __add__(self, other: "Vector3") -> "Vector3":
        """Vector3 + Vector3 -> Vector3"""
        return type(self).from_xyz(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iadd__(self, other: "Vector3") -> "Vector3":
        """Vector3 += Vector3 -> Vector3"""
        self.set_xyz(self.x + other.x, self.y + other.y, self.z + other.z)
        return self

    def __mul__(self, scalar: float) -> "Vector3":
        """Vector3 * scalar -> Vector3"""
        if not isinstance(scalar, Real):
            return NotImplemented
        return type(self).from_xyz(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> "Vector3":
        """scalar * Vector3 -> Vector3"""
        return self.__mul__(scalar)

    def __imul__(self, scalar: float) -> "Vector3":
        """Vector3 *= scalar -> Vector3"""
        if not isinstance(scalar, Real):
            return NotImplemented
        self.set_xyz(self.x * scalar, self.y * scalar, self.z * scalar)
        return self

    def __truediv__(self, scalar: float) -> "Vector3":
        """Vector3 / scalar -> Vector3"""
        if not isinstance(scalar, Real):
            return NotImplemented
        if np.isclose(float(scalar), 0.0):
            raise ValueError("Cannot divide by zero")
        return type(self).from_xyz(self.x / scalar, self.y / scalar, self.z / scalar)

    def __itruediv__(self, scalar: float) -> "Vector3":
        """Vector3 /= scalar -> Vector3"""
        if not isinstance(scalar, Real):
            return NotImplemented
        if np.isclose(float(scalar), 0.0):
            raise ValueError("Cannot divide by zero")
        self.set_xyz(self.x / scalar, self.y / scalar, self.z / scalar)
        return self

    def __str__(self) -> str:
        return f"Vector3({self.x}, {self.y}, {self.z})"

    def __repr__(self) -> str:
        return f"Vector3({self.x}, {self.y}, {self.z})"
