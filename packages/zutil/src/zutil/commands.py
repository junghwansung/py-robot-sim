from abc import ABC, abstractmethod
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from .result import Err, Ok, Result


def _run_parallel(
    commands: list["UndoableCommand"],
    action: Callable[["UndoableCommand"], Result[None, Exception]],
) -> list[Result[None, Exception]]:
    if not commands:
        return []

    with ThreadPoolExecutor(max_workers=len(commands)) as executor:
        return list(executor.map(action, commands))


class UndoableCommand(ABC):
    @abstractmethod
    def execute(self) -> Result[None, Exception]: ...

    @abstractmethod
    def undo(self) -> Result[None, Exception]: ...

    def redo(self) -> Result[None, Exception]:
        return self.execute()


class MacroCommand(UndoableCommand):
    def __init__(self, commands: list[UndoableCommand]):
        self._commands = commands

    def execute(self) -> Result[None, Exception]:
        done: list[UndoableCommand] = []
        for command in self._commands:
            result = command.execute()
            if isinstance(result, Err):
                for completed in reversed(done):
                    completed.undo()
                return result
            done.append(command)
        return Ok(None)

    def undo(self) -> Result[None, Exception]:
        for command in reversed(self._commands):
            result = command.undo()
            if isinstance(result, Err):
                return result
        return Ok(None)

    def redo(self) -> Result[None, Exception]:
        for command in self._commands:
            result = command.redo()
            if isinstance(result, Err):
                return result
        return Ok(None)


class PartialMacroCommand(UndoableCommand):
    """Runs commands sequentially, stopping at the first failure.

    Unlike MacroCommand, a failure does not roll back prior successes: as
    long as at least one command succeeded, execute() reports success and
    only the succeeded commands are tracked for undo/redo.
    """

    def __init__(self, commands: list[UndoableCommand]):
        self._commands = commands
        self._succeeded: list[UndoableCommand] = []

    def execute(self) -> Result[None, Exception]:
        succeeded: list[UndoableCommand] = []
        error: Result[None, Exception] | None = None
        for command in self._commands:
            result = command.execute()
            if isinstance(result, Err):
                error = result
                break
            succeeded.append(command)

        self._succeeded = succeeded
        if succeeded:
            return Ok(None)
        return error if error is not None else Ok(None)

    def undo(self) -> Result[None, Exception]:
        for command in reversed(self._succeeded):
            result = command.undo()
            if isinstance(result, Err):
                return result
        return Ok(None)

    def redo(self) -> Result[None, Exception]:
        for command in self._succeeded:
            result = command.redo()
            if isinstance(result, Err):
                return result
        return Ok(None)


class ParallelCommand(UndoableCommand):
    def __init__(self, commands: list[UndoableCommand]):
        self._commands = commands

    def execute(self) -> Result[None, Exception]:
        if not self._commands:
            return Ok(None)

        results = _run_parallel(self._commands, lambda command: command.execute())
        errors = [result for result in results if isinstance(result, Err)]

        if errors:
            succeeded = [
                command
                for command, result in zip(self._commands, results)
                if isinstance(result, Ok)
            ]
            _run_parallel(succeeded, lambda command: command.undo())
            return errors[0]
        return Ok(None)

    def undo(self) -> Result[None, Exception]:
        if not self._commands:
            return Ok(None)

        results = _run_parallel(self._commands, lambda command: command.undo())
        errors = [result for result in results if isinstance(result, Err)]
        return errors[0] if errors else Ok(None)

    def redo(self) -> Result[None, Exception]:
        if not self._commands:
            return Ok(None)

        results = _run_parallel(self._commands, lambda command: command.redo())
        errors = [result for result in results if isinstance(result, Err)]
        return errors[0] if errors else Ok(None)


class PartialParallelCommand(UndoableCommand):
    """Runs commands in parallel; all are attempted regardless of failures.

    execute() reports success as long as at least one command succeeded.
    Only the succeeded commands are tracked for undo/redo.
    """

    def __init__(self, commands: list[UndoableCommand]):
        self._commands = commands
        self._succeeded: list[UndoableCommand] = []

    def execute(self) -> Result[None, Exception]:
        if not self._commands:
            self._succeeded = []
            return Ok(None)

        results = _run_parallel(self._commands, lambda command: command.execute())
        succeeded = [
            command for command, result in zip(self._commands, results) if isinstance(result, Ok)
        ]
        errors = [result for result in results if isinstance(result, Err)]

        self._succeeded = succeeded
        if succeeded:
            return Ok(None)
        return errors[0]

    def undo(self) -> Result[None, Exception]:
        if not self._succeeded:
            return Ok(None)

        results = _run_parallel(self._succeeded, lambda command: command.undo())
        errors = [result for result in results if isinstance(result, Err)]
        return errors[0] if errors else Ok(None)

    def redo(self) -> Result[None, Exception]:
        if not self._succeeded:
            return Ok(None)

        results = _run_parallel(self._succeeded, lambda command: command.redo())
        errors = [result for result in results if isinstance(result, Err)]
        return errors[0] if errors else Ok(None)
