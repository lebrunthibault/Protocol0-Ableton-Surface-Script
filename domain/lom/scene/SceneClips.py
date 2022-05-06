import itertools
import re

from _Framework.SubjectSlot import SlotManager
from typing import List, cast, Iterator

from protocol0.domain.lom.clip.AudioDummyClip import AudioDummyClip
from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.decorators import throttle
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable


class SceneClips(SlotManager, Observable):
    def __init__(self, index):
        # type: (int) -> None
        super(SceneClips, self).__init__()
        self.index = index
        self._clips = []  # type: List[Clip]
        self._all_clips = []  # type: List[Clip]
        self.audio_tail_clips = []  # type: List[Clip]
        self._clip_slots = []  # type: List[ClipSlot]
        self._tracks = []  # type: List[SimpleTrack]

        self.build()

    def __iter__(self):
        # type: () -> Iterator[Clip]
        return iter(self._clips)

    @throttle(wait_time=10)
    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, ClipSlot) or isinstance(observable, Clip):
            self.build()
            self.notify_observers()

    def build(self):
        # type: () -> None
        self._tracks = []
        self._clip_slots = []
        self._all_clips = []
        self._clips = []

        for track in SongFacade.simple_tracks():
            clip_slot = track.clip_slots[self.index]
            self._clip_slots.append(clip_slot)
            clip = clip_slot.clip
            if clip and clip_slot.has_clip and not isinstance(track, SimpleInstrumentBusTrack):
                self._all_clips.append(clip)  # type: ignore[unreachable]
                if not isinstance(clip, AudioTailClip) and not isinstance(clip, AudioDummyClip):
                    self._clips.append(clip)
                    self._tracks.append(track)

        self.audio_tail_clips = cast(List[AudioTailClip],
                                     [c for c in self._all_clips if isinstance(c, AudioTailClip)])

        for clip in self._clips:
            clip.register_observer(self)
        for clip_slot in self._clip_slots:
            clip_slot.register_observer(self)

    def on_added_scene(self):
        # type: () -> None
        """ Rename clips when doing consolidate time to new scene """
        if any(clip for clip in self._all_clips if self._clip_has_default_recording_name(clip)):
            for clip in self._all_clips:
                if isinstance(clip, AudioTailClip):
                    clip.delete()
                    continue

                if self._clip_has_default_recording_name(clip):
                    clip.color = ClipColorEnum.AUDIO_UN_QUANTIZED.color_int_value
                clip.clip_name.update("")

    def _clip_has_default_recording_name(self, clip):
        # type: (Clip) -> bool
        return bool(re.match(".*\\[\\d{4}-\\d{2}-\\d{2} \\d+]$", clip.name))

    @property
    def tracks(self):
        # type: () -> Iterator[SimpleTrack]
        for track, clip in itertools.izip(self._tracks, list(self._clips)):
            if not clip.muted:
                yield track
