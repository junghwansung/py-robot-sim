from .commands import UndoableCommand
from .result import Err, Ok, Result


class CommandExecutor:
    def execute(self, command: UndoableCommand) -> Result[None, Exception]:
        return command.execute()

    def undo(self, command: UndoableCommand) -> Result[None, Exception]:
        return command.undo()

    def redo(self, command: UndoableCommand) -> Result[None, Exception]:
        return command.redo()


class CommandHistory:
    def __init__(self, max_history: int = 20):
        if max_history < 1:
            raise ValueError("max_history must be greater than zero")

        self._undo_stack: list[UndoableCommand] = []
        self._redo_stack: list[UndoableCommand] = []
        self._max_history = max_history

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def record(self, command: UndoableCommand) -> None:
        self._undo_stack.append(command)
        self._redo_stack.clear()

        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def peek_undo(self) -> UndoableCommand | None:
        return self._undo_stack[-1] if self._undo_stack else None

    def peek_redo(self) -> UndoableCommand | None:
        return self._redo_stack[-1] if self._redo_stack else None

    def commit_undo(self) -> None:
        command = self._undo_stack.pop()
        self._redo_stack.append(command)

    def commit_redo(self) -> None:
        command = self._redo_stack.pop()
        self._undo_stack.append(command)

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()


class UndoRedoService:
    def __init__(
        self,
        executor: CommandExecutor | None = None,
        history: CommandHistory | None = None,
    ):
        self._executor = executor if executor is not None else CommandExecutor()
        self._history = history if history is not None else CommandHistory()

    @property
    def can_undo(self) -> bool:
        return self._history.can_undo

    @property
    def can_redo(self) -> bool:
        return self._history.can_redo

    def execute(self, command: UndoableCommand) -> Result[None, Exception]:
        result = self._executor.execute(command)
        if isinstance(result, Err):
            return result

        self._history.record(command)
        return Ok(None)

    def undo(self) -> Result[None, Exception]:
        command = self._history.peek_undo()
        if command is None:
            return Err(Exception("Nothing to undo"))

        result = self._executor.undo(command)
        if isinstance(result, Err):
            return result

        self._history.commit_undo()
        return Ok(None)

    def redo(self) -> Result[None, Exception]:
        command = self._history.peek_redo()
        if command is None:
            return Err(Exception("Nothing to redo"))

        result = self._executor.redo(command)
        if isinstance(result, Err):
            return result

        self._history.commit_redo()
        return Ok(None)

    def clear(self) -> None:
        self._history.clear()
