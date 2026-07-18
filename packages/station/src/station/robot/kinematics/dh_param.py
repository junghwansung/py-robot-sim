import math
from collections.abc import Iterator

from zmath.transform_matrix import TMatrix3


class DHLink:
    """
    Modified Denavit-Hartenberg parameters for a single link of a robotic manipulator.
    """

    def __init__(self, a: float, alpha: float, d: float, theta: float):
        self._a = a  # Link length
        self._alpha = alpha  # Link twist
        self._d = d  # Link offset
        self._theta = theta  # Joint angle

    @property
    def a(self) -> float:
        return self._a

    @property
    def alpha(self) -> float:
        return self._alpha

    @property
    def d(self) -> float:
        return self._d

    @property
    def theta(self) -> float:
        return self._theta

    def next(self, value: float = 0.0) -> TMatrix3:
        cos_alpha = math.cos(self._alpha)
        sin_alpha = math.sin(self._alpha)
        cos_theta = math.cos(self._theta + value)
        sin_theta = math.sin(self._theta + value)

        return TMatrix3.from_4by4_row_major(
            [
                [cos_theta, -sin_theta, 0, self._a],
                [sin_theta * cos_alpha, cos_theta * cos_alpha, -sin_alpha, -sin_alpha * self._d],
                [sin_theta * sin_alpha, cos_theta * sin_alpha, cos_alpha, cos_alpha * self._d],
                [0, 0, 0, 1],
            ]
        )

    def __repr__(self) -> str:
        return f"DHLink(a={self._a}, alpha={self._alpha}, d={self._d}, theta={self._theta})"


class DHParam:
    """
    Modified Denavit-Hartenberg parameters for a robotic manipulator.
    """

    def __init__(self, links: list[DHLink]):
        self._links: list[DHLink] = links  # List of DHLink objects

    @property
    def dof(self) -> int:
        return len(self._links)

    def __getitem__(self, index: int) -> DHLink:
        return self._links[index]

    def __repr__(self) -> str:
        return f"DHParam(links={self._links})"

    def __iter__(self) -> Iterator[DHLink]:
        return iter(self._links)
