from collections.abc import Iterator
from typing import Generic, TypeVar

from .vector import Vector2, Vector3

V = TypeVar("V", Vector2, Vector3)


class Polygon(Generic[V]):
    def __init__(self, vertices: list[V]):
        assert 3 <= len(vertices), "A polygon must have at least 3 vertices."
        if len(vertices) < 3:
            raise ValueError("A polygon must have at least 3 vertices.")

        self._vertices: list[V] = vertices

    @property
    def count(self) -> int:
        return len(self._vertices)

    @property
    def perimeter(self) -> float:
        return sum(a.distance_to(b) for a, b in self.edges())

    def to_tuple(self) -> list[tuple[float, ...]]:
        return [v.to_tuple() for v in self._vertices]

    def get_center(self) -> V:
        assert 3 <= self.count, "Polygon must have at least three vertices to calculate center."

        sum_vector: V = self._vertices[0] * 0
        for vertex in self._vertices:
            sum_vector += vertex
        return sum_vector / self.count

    def edges(self) -> list[tuple[V, V]]:
        n = self.count
        return [(self._vertices[i], self._vertices[(i + 1) % n]) for i in range(n)]

    def __len__(self) -> int:
        return len(self._vertices)

    def __iter__(self) -> Iterator[V]:
        return iter(self._vertices)

    def __repr__(self) -> str:
        return f"Polygon({self._vertices})"


Polygon2 = Polygon[Vector2]
Polygon3 = Polygon[Vector3]
