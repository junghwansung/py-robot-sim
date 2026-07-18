from typing import TypeVar

T = TypeVar("T")


class Range[T]:
    """
    Range class representing a numerical interval

    min - minimum value of the range
    max - maximum value of the range

    should be used
        - for representing numerical intervals
        - for range-related operations like containment checks, clamping, etc.
    """

    __slots__ = ("_min", "_max")
    _min: T
    _max: T

    def __init__(self, _min: T, _max: T):
        if not all(isinstance(v, T) for v in (_min, _max)):
            raise TypeError("min and max must be T numbers")
        if _min > _max:
            raise ValueError(f"min ({_min}) must be <= max ({_max})")

        object.__setattr__(self, "_min", T(_min))
        object.__setattr__(self, "_max", T(_max))

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"min", "max", "_min", "_max"}:
            raise AttributeError("Direct assignment is not allowed. Use set_range()")
        object.__setattr__(self, name, value)

    @property
    def min(self) -> T:
        """return the minimum value of the range"""
        return self._min

    @property
    def max(self) -> T:
        """return the maximum value of the range"""
        return self._max

    def set_range(self, _min: T, _max: T) -> None:
        """update range bounds in-place"""
        if not all(isinstance(v, T) for v in (_min, _max)):
            raise TypeError("min and max must be T numbers")
        if _min > _max:
            raise ValueError(f"min ({_min}) must be <= max ({_max})")
        object.__setattr__(self, "_min", T(_min))
        object.__setattr__(self, "_max", T(_max))

    def span(self) -> T:
        """return the length of the range (max - min)"""
        return self._max - self._min

    def is_contain(self, value: T) -> bool:
        """return True if value is within [min, max] inclusive"""
        return self._min <= value <= self._max

    def clamp(self, value: T) -> T:
        """return value clamped to [min, max]"""
        return max(self._min, min(self._max, T(value)))

    def lerp(self, t: T) -> T:
        """return interpolated value at t (t=0 -> min, t=1 -> max)"""
        return self._min + (self._max - self._min) * t

    def normalize(self, value: T) -> T:
        """return t such that lerp(t) == value; inverse of lerp"""
        s = self.span()
        if s == 0.0:
            raise ValueError("Cannot normalize value in a zero-span range")
        return (T(value) - self._min) / s

    def copy(self) -> "Range[T]":
        """return a copy of this range"""
        return Range[T](self._min, self._max)

    def __contains__(self, value: object) -> bool:
        """value in range -> bool (inclusive bounds)"""
        if not isinstance(value, T):
            return False
        return self._min <= T(value) <= self._max

    def __eq__(self, other: object) -> bool:
        """Range == Range -> bool"""
        if not isinstance(other, Range[T]):
            return NotImplemented
        return self._min == other._min and self._max == other._max

    def __repr__(self) -> str:
        return f"Range({self._min}, {self._max})"

    def __str__(self) -> str:
        return f"Range({self._min}, {self._max})"


if __name__ == "__main__":
    r = Range[float](0.0, 10.0)
    assert r.min == 0.0 and r.max == 10.0
    assert r.span() == 10.0
    assert r.clamp(-1.0) == 0.0
    assert r.clamp(5.0) == 5.0
    assert r.clamp(11.0) == 10.0
    assert r.is_contain(0.0) and r.is_contain(10.0) and not r.is_contain(10.1)
    assert 0.0 in r and 10.0 in r and 11.0 not in r
    assert r.lerp(0.5) == 5.0
    assert r.normalize(5.0) == 0.5
    print("Range: all assertions passed")
