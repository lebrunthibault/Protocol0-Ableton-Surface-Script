from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class ActionGroupTest(ActionGroupInterface):
    # NB: each scroll encoder is sending a cc value of zero on startup / shutdown and that can interfere

    CHANNEL = 16

    def configure(self):
        # type: () -> None
        # TEST encoder
        self.add_encoder(identifier=1, name="test",
                         on_press=self.action_test,
                         )

        # PROFiling encoder
        self.add_encoder(identifier=2, name="start set launch time profiling",
                         on_press=Backend.client().start_set_profiling)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

    def action_test(self):
        # type: () -> None
        track = SongFacade.current_external_synth_track()
        clip_slots = [track.midi_track.clip_slots[0], track.audio_track.clip_slots[0],
                      track.audio_tail_track.clip_slots[0]]
        seq = Sequence()
        seq.add([clip_slot.prepare_for_record for clip_slot in clip_slots])
        seq.done()
