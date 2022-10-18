from typing import Any

from protocol0.application.command.SerializableCommand import SerializableCommand


class ProcessBackendResponseCommand(SerializableCommand):
    def __init__(self, res):
        # type: (Any) -> None
        super(ProcessBackendResponseCommand, self).__init__()
        self.res = res
