from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import subject_slot


class AbstractAutomationClip(Clip):
    @subject_slot("playing_status")
    def _playing_status_listener(self):
        linked_clip = self._playing_status_listener.subject
        if self.is_playing == linked_clip.is_playing:
            return
        self.parent.log_debug("----------")
        self.parent.log_debug(linked_clip)
        self.parent.log_debug(self)
        self.parent.log_debug(linked_clip.is_playing)
        self.parent.log_debug(self.is_playing)
        seq = Sequence()
        # noinspection PyUnresolvedReferences
        seq.add(setattr(self.track.get_clip(linked_clip)._playing_status_listener, "subject", None))
        if linked_clip.is_playing:
            self.is_playing = True
            seq.add(wait=1)
            seq.add(lambda: setattr(self, "start_marker", self.parent.utilsManager.get_next_quantized_position(
                linked_clip.playing_position, linked_clip.length)))
            seq.add(lambda: setattr(self, "is_playing", True))
        else:
            self.is_playing = False
        seq.add(wait=2)
        # noinspection PyUnresolvedReferences
        seq.add(setattr(self.track.get_clip(linked_clip)._playing_status_listener, "subject", self._clip))

        return seq.done()
