from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E


type Result[T, E] = Ok[T] | Err[E]

"""
Result Pattern: A type that represents either a success (Ok) or an error (Err).
Usage:

from enum import Enum
from zutil.result import Err, Ok, Result


class CalcError(str, Enum):
    DIVISION_BY_ZERO = "Division by zero"
    OVERFLOW = "Overflow"


def divide(a: float, b: float) -> Result[float, CalcError]:
    if b == 0:
        return Err(CalcError.DIVISION_BY_ZERO)
    result = a / b
    if result in (float("inf"), float("-inf")):
        return Err(CalcError.OVERFLOW)
    return Ok(result)


def main():
    match divide(10, 2):
        case Ok(value=v):
            print(f"Result: {v}")
        case Err(error=CalcError.DIVISION_BY_ZERO):
            print("0으로 나눌 수 없음")
        case Err(error=CalcError.OVERFLOW):
            print("오버플로우")
"""
