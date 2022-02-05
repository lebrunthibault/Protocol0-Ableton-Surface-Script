from protocol0.application.system_command.SerializableCommand import SerializableCommand


class ShowMessageCommand(SerializableCommand):
    def __init__(self, message):
        # type: (str) -> None
        self.message = message
