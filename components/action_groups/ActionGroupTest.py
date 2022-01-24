from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.sequence.Sequence import Sequence


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        # channel is not 1 because 1 is reserved for non script midi
        # NB: each scroll encoder is sending a cc value of zero on startup / shutdown and that can interfere
        super(ActionGroupTest, self).__init__(channel=16, *a, **k)

        # TEST encoder
        self.add_encoder(identifier=1, name="test", on_press=self.action_test, on_cancel_press=self.action_cancel_test)

        # PROFiling encoder
        self.add_encoder(identifier=2, name="start set launch time profiling", on_press=self.start_set_profiling)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=self.parent.logManager.clear)

    def action_test(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(wait=100)
        return seq.done()

    def action_cancel_test(self):
        # type: () -> None
        self.system.show_warning("cancelling !")

    def start_set_profiling(self):
        # type: () -> None
        self.system.start_set_profiling()
