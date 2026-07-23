from .range import Range


class RangedValue[T: (int, float)]:
    """
    RangedValue class representing a single value constrained to a Range

    range - the Range this value is bounded to
    value - current value, always clamped to [range.min, range.max]

    should be used
        - for values that must never leave a numerical interval (e.g. sensor readings, sliders)
        - values set outside the range are clamped, not rejected
    """

    __slots__ = ("_range", "_value")
    _range: Range[T]
    _value: T

    def __init__(self, bound: Range[T], value: T):
        if not isinstance(bound, Range):
            raise TypeError("bound must be a Range")
        if not isinstance(value, (int, float)):
            raise TypeError("value must be an int or float")

        object.__setattr__(self, "_range", bound)
        object.__setattr__(self, "_value", bound.clamp(value))

    def __setattr__(self, name: str, value: object) -> None:
        if name in {"range", "value", "_range", "_value"}:
            raise AttributeError("Direct assignment is not allowed. Use set_value()/set_range()")
        object.__setattr__(self, name, value)

    @classmethod
    def from_range(cls, bound: Range[T]) -> "RangedValue[T]":
        """create a RangedValue with the given range and value set to the range's midpoint"""
        return cls(bound, bound.midpoint())

    @property
    def range(self) -> Range[T]:
        """return the Range this value is bounded to"""
        return self._range

    @property
    def value(self) -> T:
        """return the current value"""
        return self._value

    def set_value(self, value: T) -> None:
        """update value in-place, clamped to the current range"""
        if not isinstance(value, (int, float)):
            raise TypeError("value must be an int or float")

        object.__setattr__(self, "_value", self._range.clamp(value))

    def set_range(self, bound: Range[T]) -> None:
        """update range in-place; current value is re-clamped to the new range"""
        if not isinstance(bound, Range):
            raise TypeError("bound must be a Range")

        self._range.set_range(bound.min, bound.max)
        object.__setattr__(self, "_value", bound.clamp(self._value))

    def copy(self) -> "RangedValue[T]":
        return RangedValue[T](self._range, self._value)

    def __repr__(self) -> str:
        return f"RangedValue({self._range!r}, {self._value})"

    def __str__(self) -> str:
        return f"RangedValue({self._range}, {self._value})"


if __name__ == "__main__":
    r = Range[float](0.0, 10.0)
    bv = RangedValue[float](r, 5.0)
    assert bv.value == 5.0
    assert bv.range == r

    bv.set_value(-1.0)
    assert bv.value == 0.0

    bv.set_value(11.0)
    assert bv.value == 10.0

    bv2 = RangedValue[float](r, 20.0)
    assert bv2.value == 10.0

    bv.set_range(Range[float](5.0, 20.0))
    assert bv.value == 10.0

    print("RangedValue: all assertions passed")
