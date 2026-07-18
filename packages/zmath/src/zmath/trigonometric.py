import math

from .types import Direction

#
#          C
#         /\
#        /γ \
#     b /    \ a
#      /      \
#     / α     β\
#    /___________\
#   A      c      B
#
#   α + β + γ = π
#   a ↔ BC,  b ↔ CA,  c ↔ AB
#


def calc_c_from_a_b_gamma(a: float, b: float, gamma: float) -> float:
    """
    Calculate the length of side c in a triangle given sides a, b and angle γ (gamma).
    """
    return math.sqrt(a**2 + b**2 - 2 * a * b * math.cos(gamma))


def calc_gamma_from_a_b_c(a: float, b: float, c: float) -> float:
    """
    Calculate the angle γ (gamma) in a triangle given sides a, b and c.
    """
    return math.acos((a**2 + b**2 - c**2) / (2 * a * b))


def calc_beta_from_a_b_gamma(a: float, b: float, gamma: float) -> float:
    """
    Calculate the angle β (beta) in a triangle given sides a, b and angle γ (gamma).
    """
    c = calc_c_from_a_b_gamma(a, b, gamma)
    return math.acos((b**2 + c**2 - a**2) / (2 * b * c))


def solve_sin_cos_combination(p: float, q: float, r: float, dir: Direction) -> float:
    """
    Solve the equation p * sin(x) + q * cos(x) +r = 0 for x.
    Returns a single solution x in radians.
    """
    a = p**2 + q**2
    if a == 0:
        raise ValueError("Both p and q cannot be zero.")

    dir: float = float(dir)

    b = math.sqrt(a - r**2)

    cos_x = (-p * r + dir * q * b) / a
    sin_x = (-q * r - dir * p * b) / a

    return math.atan2(sin_x, cos_x)
