import Live
from typing import TYPE_CHECKING, List

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer
from a_protocol_0.lom.clip.ClipActionMixin import ClipActionMixin
from a_protocol_0.utils.decorators import p0_subject_slot, is_change_deferrable

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class Clip(ClipActionMixin, AbstractObject):
    __subject_events__ = ('notes', 'name', 'playing_status', 'is_triggered')

    def __init__(self, clip_slot, *a, **k):
        # type: (ClipSlot) -> None
        super(Clip, self).__init__(*a, **k)
        self.clip_slot = clip_slot
        self._clip_slot = clip_slot._clip_slot
        self._clip = self._clip_slot.clip  # type: Live.Clip.Clip
        self.view = self._clip.view  # type: Live.Clip.Clip.View
        self.index = clip_slot.index
        self.track = clip_slot.track  # type: SimpleTrack
        self.is_selected = False
        self._previous_name = self._clip.name
        self._notes_listener.subject = self._clip
        self._is_recording_listener.subject = self._clip
        self._playing_status_listener.subject = self._clip
        self.color = self.track.base_color

        # NOTES
        # storing notes for note change comparison
        self._prev_notes = self.get_notes() if self.is_midi_clip else []  # type: List[Note]
        self._added_note = None  # type: Note
        self._is_updating_notes = False

        # Clip sync
        self._clip_synchronizer = None  # type: ObjectSynchronizer
        self.parent.defer(self.link_clip)  # deferring

    def link_clip(self):
        if self.clip_slot.linked_clip_slot and self.clip_slot.linked_clip_slot.clip:
            self.clip_synchronizer = ObjectSynchronizer(
                self.clip_slot.clip, self.clip_slot.linked_clip_slot.clip, "_clip",
                ["name", "looping", "loop_start", "loop_end",
                 "start_marker", "end_marker"], bidirectional=False)

    @property
    def linked_clip(self):
        # type: () -> Clip
        return self.clip_slot.linked_clip_slot.clip if self.clip_slot.linked_clip_slot else None

    def _on_selected(self):
        pass

    @p0_subject_slot("notes")
    def _notes_listener(self):
        pass

    @p0_subject_slot("is_recording")
    def _is_recording_listener(self):
        pass

    @p0_subject_slot("name")
    def _name_listener(self):
        pass

    @p0_subject_slot("playing_status")
    def _playing_status_listener(self):
        # noinspection PyUnresolvedReferences
        self.notify_playing_status()

    @staticmethod
    def make(clip_slot):
        # type: (ClipSlot) -> Clip
        from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
        from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
        from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
        from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip

        if isinstance(clip_slot, AutomationMidiClipSlot):
            return AutomationMidiClip(clip_slot=clip_slot)
        elif isinstance(clip_slot.track, AutomationAudioTrack):
            return AutomationAudioClip(clip_slot=clip_slot)
        else:
            return Clip(clip_slot=clip_slot)

    @property
    def name(self):
        # type: () -> str
        return self._clip.name if getattr(self, "_clip", None) else None

    @name.setter
    @is_change_deferrable
    def name(self, name):
        # type: (str) -> None
        if self._clip and str(name) != self._clip.name:
            self._clip.name = str(name)

    @property
    def is_midi_clip(self):
        return self._clip.is_midi_clip if self._clip else None

    @property
    def is_audio_clip(self):
        return self._clip.is_audio_clip if self._clip else None

    @property
    def length(self):
        # type: () -> float
        """ For looped clips: loop length in beats """
        return self._clip.length if self._clip else 0

    @property
    def warping(self):
        # type: () -> float
        return self._clip.warping if self._clip else 0

    @warping.setter
    @is_change_deferrable
    def warping(self, warping):
        # type: (float) -> None
        if self._clip:
            self._clip.warping = warping

    @property
    def looping(self):
        # type: () -> float
        return self._clip.looping if self._clip else 0

    @looping.setter
    @is_change_deferrable
    def looping(self, looping):
        # type: (float) -> None
        if self._clip:
            self._clip.looping = looping

    @property
    def loop_start(self):
        # type: () -> float
        return self._clip.loop_start if self._clip else 0

    @loop_start.setter
    @is_change_deferrable
    def loop_start(self, loop_start):
        # type: (float) -> None
        if self._clip:
            self._clip.loop_start = loop_start

    @property
    def loop_end(self):
        # type: () -> float
        return self._clip.loop_end if self._clip else 0

    @loop_end.setter
    @is_change_deferrable
    def loop_end(self, loop_end):
        # type: (float) -> None
        if self._clip:
            self._clip.loop_end = loop_end

    @property
    def start_marker(self):
        # type: () -> float
        return self._clip.start_marker if self._clip else 0

    @start_marker.setter
    @is_change_deferrable
    def start_marker(self, start_marker):
        # type: (float) -> None
        if self._clip:
            self._clip.start_marker = start_marker

    @property
    def end_marker(self):
        # type: () -> float
        return self._clip.end_marker if self._clip else 0

    @end_marker.setter
    @is_change_deferrable
    def end_marker(self, end_marker):
        # type: (float) -> None
        if self._clip:
            self._clip.end_marker = end_marker

    @property
    def color(self):
        # type: () -> int
        return self._clip.color_index if self._clip else 0

    @color.setter
    @is_change_deferrable
    def color(self, color_index):
        # type: (int) -> None
        if self._clip and color_index != self._clip.color_index:
            self._clip.color_index = int(color_index)

    @property
    def is_playing(self):
        # type: () -> bool
        return self._clip and self._clip.is_playing

    @property
    def is_triggered(self):
        # type: () -> bool
        return self._clip and self._clip.is_triggered

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        if self._clip and is_playing != self.is_playing:
            self._clip.is_playing = is_playing

    @property
    def playing_position(self):
        # type: () -> float
        """ For MIDI and warped audio clips the value is given in beats of absolute clip time """
        return self._clip.playing_position if self._clip else 0

    @property
    def is_recording(self):
        # type: () -> bool
        return self._clip and self._clip.is_recording

    @property
    def warp_mode(self):
        return self._clip.warp_mode

    @warp_mode.setter
    @is_change_deferrable
    def warp_mode(self, warp_mode):
        if self._clip:
            self._clip.warp_mode = warp_mode

    def disconnect(self):
        if self._clip_synchronizer:
            self._clip_synchronizer.disconnect()
