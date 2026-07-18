from station.base.component import ComponentType, SComponent
from station.robot.tpose import TPose


class Path(SComponent):
    def __init__(self, name: str, parent: SComponent):
        super().__init__(name, ComponentType.PATH, parent=parent)

        self._tposes: list[TPose] = []

    def insert_tpose(self, tpose: TPose, index: int = -1) -> None:
        self._tposes.insert(index, tpose)

    def remove_tpose(self, index: int) -> None:
        self._tposes.pop(index)

    def get_tpose_by_index(self, index: int) -> TPose:
        return self._tposes[index]

    def get_tpose_by_name(self, name: str) -> TPose | None:
        return next((tpose for tpose in self._tposes if tpose.name == name), None)

    def __getitem__(self, index: int) -> TPose:
        return self._tposes[index]
