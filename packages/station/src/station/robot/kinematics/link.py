from .joint import Joint


class Link:
    def __init__(self, joint: Joint, name: str = ""):
        self._name = name
        self._joint = joint
        self._weight = 0.0
        self._inertia = None  # Placeholder for inertia properties, can be set later

    @property
    def joint(self) -> Joint:
        return self._joint

    @property
    def name(self) -> str:
        return self._name
