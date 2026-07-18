import unittest

from zutil.commands import CommandHistory, UndoableCommand, UndoRedoService
from zutil.result import Err, Ok, Result


class RecordingCommand(UndoableCommand):
    def __init__(self, values: list[str], value: str):
        self._values = values
        self._value = value
        self.fail_execute = False
        self.fail_undo = False
        self.fail_redo = False

    def execute(self) -> Result[None, Exception]:
        if self.fail_execute:
            return Err(Exception("execute failed"))
        self._values.append(self._value)
        return Ok(None)

    def undo(self) -> Result[None, Exception]:
        if self.fail_undo:
            return Err(Exception("undo failed"))
        self._values.remove(self._value)
        return Ok(None)

    def redo(self) -> Result[None, Exception]:
        if self.fail_redo:
            return Err(Exception("redo failed"))
        return self.execute()


class UndoRedoServiceTest(unittest.TestCase):
    def test_execute_undo_and_redo(self) -> None:
        values: list[str] = []
        command = RecordingCommand(values, "value")
        service = UndoRedoService()

        self.assertIsInstance(service.execute(command), Ok)
        self.assertEqual(values, ["value"])
        self.assertTrue(service.can_undo)

        self.assertIsInstance(service.undo(), Ok)
        self.assertEqual(values, [])
        self.assertTrue(service.can_redo)

        self.assertIsInstance(service.redo(), Ok)
        self.assertEqual(values, ["value"])
        self.assertTrue(service.can_undo)

    def test_failed_execute_is_not_recorded(self) -> None:
        command = RecordingCommand([], "value")
        command.fail_execute = True
        service = UndoRedoService()

        self.assertIsInstance(service.execute(command), Err)
        self.assertFalse(service.can_undo)
        self.assertFalse(service.can_redo)

    def test_failed_execute_does_not_clear_redo_stack(self) -> None:
        values: list[str] = []
        successful_command = RecordingCommand(values, "successful")
        failed_command = RecordingCommand(values, "failed")
        service = UndoRedoService()
        service.execute(successful_command)
        service.undo()

        failed_command.fail_execute = True
        self.assertIsInstance(service.execute(failed_command), Err)

        self.assertFalse(service.can_undo)
        self.assertTrue(service.can_redo)
        self.assertEqual(values, [])

    def test_failed_undo_keeps_command_in_history(self) -> None:
        values: list[str] = []
        command = RecordingCommand(values, "value")
        service = UndoRedoService()
        service.execute(command)

        command.fail_undo = True
        self.assertIsInstance(service.undo(), Err)

        self.assertTrue(service.can_undo)
        self.assertFalse(service.can_redo)
        self.assertEqual(values, ["value"])

    def test_failed_redo_keeps_command_in_redo_stack(self) -> None:
        values: list[str] = []
        command = RecordingCommand(values, "value")
        service = UndoRedoService()
        service.execute(command)
        service.undo()

        command.fail_redo = True
        self.assertIsInstance(service.redo(), Err)

        self.assertFalse(service.can_undo)
        self.assertTrue(service.can_redo)
        self.assertEqual(values, [])

    def test_empty_history_returns_error(self) -> None:
        service = UndoRedoService()

        self.assertIsInstance(service.undo(), Err)
        self.assertIsInstance(service.redo(), Err)

    def test_history_enforces_maximum_size(self) -> None:
        values: list[str] = []
        service = UndoRedoService(history=CommandHistory(max_history=1))
        first = RecordingCommand(values, "first")
        second = RecordingCommand(values, "second")

        service.execute(first)
        service.execute(second)
        service.undo()

        self.assertEqual(values, ["first"])
        self.assertFalse(service.can_undo)

    def test_history_rejects_non_positive_maximum(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            CommandHistory(max_history=0)


if __name__ == "__main__":
    unittest.main()
