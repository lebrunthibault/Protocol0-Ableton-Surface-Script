import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.ClipName import ClipName
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.shared.observer.Observable import Observable


class ClipSlotSynchronizer(SlotManager):
    """ For ExternalSynthTrack """

    def __init__(self, midi_cs, audio_cs):
        # type: (MidiClipSlot, AudioClipSlot) -> None
        super(ClipSlotSynchronizer, self).__init__()
        self._midi_cs = midi_cs
        self._audio_cs = audio_cs

        self._has_clip_listener.replace_subjects([midi_cs._clip_slot, audio_cs._clip_slot])
        self._sync_clips()

    def _sync_clips(self):
        # type: () -> None
        if self._midi_cs.clip and self._audio_cs.clip:
            self._midi_cs.clip.register_observer(self)

    @property
    def _clip_exists(self):
        # type: () -> bool
        return self._audio_cs.clip is not None and self._midi_cs.clip is not None

    def update(self, observable):
        # type: (Observable) -> None
        if not self._clip_exists:
            return
        audio_clip = self._audio_cs.clip
        midi_clip = self._midi_cs.clip

        if isinstance(observable, ClipLoop):
            audio_clip.loop.looping = midi_clip.loop.looping
            audio_clip.loop.start = midi_clip.loop.start
            audio_clip.loop.end = midi_clip.loop.end
        if isinstance(observable, ClipName):
            audio_clip.name = midi_clip.name

    @subject_slot_group("has_clip")
    def _has_clip_listener(self, _):
        # type: (Live.ClipSlot.ClipSlot) -> None
        self._sync_clips()
