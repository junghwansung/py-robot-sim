from numbers import Real


class Size2:
    """
    2D size class with basic size operations

    width - width component, unit is mm
    height - height component, unit is mm

    should be used
        - for representing dimensions in 2D space
        - for size-related operations like scaling, area calculation, etc.
    """

    __slots__ = ("_width", "_height")
    _width: float
    _height: float

    def __init__(self, width: float, height: float):
        if not all(isinstance(v, Real) for v in (width, height)):
            raise TypeError("width and height must be real numbers")
        if width < 0 or height < 0:
            raise ValueError("width and height must be non-negative")

        object.__setattr__(self, "_width", float(width))
        object.__setattr__(self, "_height", float(height))

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"width", "height", "_width", "_height"}:
            raise AttributeError("Direct assignment is not allowed. Use set_size()")
        object.__setattr__(self, name, value)

    @property
    def width(self) -> float:
        """return the width component"""
        return self._width

    @property
    def height(self) -> float:
        """return the height component"""
        return self._height

    def set_size(self, width: float, height: float) -> None:
        """update size components in-place"""
        if not all(isinstance(v, Real) for v in (width, height)):
            raise TypeError("width and height must be real numbers")
        if width < 0 or height < 0:
            raise ValueError("width and height must be non-negative")
        object.__setattr__(self, "_width", float(width))
        object.__setattr__(self, "_height", float(height))

    def area(self) -> float:
        """return the area (width * height)"""
        return self._width * self._height

    def scale(self, factor: float) -> "Size2":
        """return a new Size2 scaled by factor"""
        if not isinstance(factor, Real):
            raise TypeError("factor must be a real number")
        if factor < 0:
            raise ValueError("factor must be non-negative")
        return Size2(self._width * factor, self._height * factor)

    def copy(self) -> "Size2":
        """return a copy of this size"""
        return Size2(self._width, self._height)

    def __eq__(self, other: object) -> bool:
        """Size2 == Size2 -> bool"""
        if not isinstance(other, Size2):
            return NotImplemented
        return self._width == other._width and self._height == other._height

    def __repr__(self) -> str:
        return f"Size2({self._width}, {self._height})"

    def __str__(self) -> str:
        return f"Size2({self._width}, {self._height})"


class Size3:
    """
    3D size class with basic size operations

    width - width component, unit is mm
    height - height component, unit is mm
    depth - depth component, unit is mm

    should be used
        - for representing dimensions in 3D space
        - for size-related operations like scaling, volume calculation, etc.
    """

    __slots__ = ("_width", "_height", "_depth")
    _width: float
    _height: float
    _depth: float

    def __init__(self, width: float, height: float, depth: float):
        if not all(isinstance(v, Real) for v in (width, height, depth)):
            raise TypeError("width, height, and depth must be real numbers")
        if width < 0 or height < 0 or depth < 0:
            raise ValueError("width, height, and depth must be non-negative")

        object.__setattr__(self, "_width", float(width))
        object.__setattr__(self, "_height", float(height))
        object.__setattr__(self, "_depth", float(depth))

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"width", "height", "depth", "_width", "_height", "_depth"}:
            raise AttributeError("Direct assignment is not allowed. Use set_size()")
        object.__setattr__(self, name, value)

    @property
    def width(self) -> float:
        """return the width component"""
        return self._width

    @property
    def height(self) -> float:
        """return the height component"""
        return self._height

    @property
    def depth(self) -> float:
        """return the depth component"""
        return self._depth

    def set_size(self, width: float, height: float, depth: float) -> None:
        """update size components in-place"""
        if not all(isinstance(v, Real) for v in (width, height, depth)):
            raise TypeError("width, height, and depth must be real numbers")
        if width < 0 or height < 0 or depth < 0:
            raise ValueError("width, height, and depth must be non-negative")
        object.__setattr__(self, "_width", float(width))
        object.__setattr__(self, "_height", float(height))
        object.__setattr__(self, "_depth", float(depth))

    def volume(self) -> float:
        """return the volume (width * height * depth)"""
        return self._width * self._height * self._depth

    def scale(self, factor: float) -> "Size3":
        """return a new Size3 scaled by factor"""
        if not isinstance(factor, Real):
            raise TypeError("factor must be a real number")
        if factor < 0:
            raise ValueError("factor must be non-negative")
        return Size3(self._width * factor, self._height * factor, self._depth * factor)

    def copy(self) -> "Size3":
        """return a copy of this size"""
        return Size3(self._width, self._height, self._depth)

    def __eq__(self, other: object) -> bool:
        """Size3 == Size3 -> bool"""
        if not isinstance(other, Size3):
            return NotImplemented
        return self._width == other._width and self._height == other._height and self._depth == other._depth

    def __repr__(self) -> str:
        return f"Size3({self._width}, {self._height}, {self._depth})"

    def __str__(self) -> str:
        return f"Size3({self._width}, {self._height}, {self._depth})"


if __name__ == "__main__":
    s2 = Size2(10.0, 5.0)
    assert s2.area() == 50.0
    assert s2.scale(2.0) == Size2(20.0, 10.0)
    s2.set_size(4.0, 3.0)
    assert s2.width == 4.0 and s2.height == 3.0

    s3 = Size3(2.0, 3.0, 4.0)
    assert s3.volume() == 24.0
    assert s3.scale(0.5) == Size3(1.0, 1.5, 2.0)

    print("Size: all assertions passed")
