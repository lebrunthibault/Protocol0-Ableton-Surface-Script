from protocol0.enums.AbstractEnum import AbstractEnum


class Push2MatrixModeEnum(AbstractEnum):
    NOTE = "note"
    SESSION = "session"

    @property
    def label(self):
        # type: () -> str
        return self.value
