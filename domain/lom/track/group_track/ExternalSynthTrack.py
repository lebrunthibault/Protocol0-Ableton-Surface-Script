import itertools
from functools import partial

from typing import Optional, cast, List, Iterator

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin
from protocol0.domain.lom.track.group_track.ExternalSynthTrackMonitoringState import ExternalSynthTrackMonitoringState
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import find_if
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrack(ExternalSynthTrackActionMixin, AbstractGroupTrack):
    REMOVE_CLIPS_ON_ADDED = True

    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(ExternalSynthTrack, self).__init__(base_group_track=base_group_track)
        self.midi_track = cast(SimpleMidiTrack, base_group_track.sub_tracks[0])
        self.audio_track = cast(SimpleAudioTrack, base_group_track.sub_tracks[1])
        self.midi_track.track_name.disconnect()
        self.audio_track.track_name.disconnect()
        self.audio_tail_track = None  # type: Optional[SimpleAudioTailTrack]

        # sub tracks are now handled by self
        for sub_track in base_group_track.sub_tracks:
            sub_track.abstract_group_track = self

        self._clip_slot_synchronizers = []  # type: List[ClipSlotSynchronizer]

        self._external_device = None  # type: Optional[Device]
        self._devices_listener.subject = self.midi_track
        self._devices_listener()

        self.monitoring_state = ExternalSynthTrackMonitoringState(self)  # type: ExternalSynthTrackMonitoringState

        DomainEventBus.subscribe(LastBeatPassedEvent, self._on_last_beat_passed_event)

    def on_added(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(ExternalSynthTrack, self).on_added)
        seq.add(self.abstract_track.arm)

        # if len(self.base_track.devices):
        #     devices = "\n".join([str(d) for d in self.base_track.devices])
        #     seq.prompt("Clear %s effects ?\n\n%s" % (len(self.base_track.devices), devices))
        #     seq.add([device.delete for device in self.base_track.devices])

        for dummy_track in self.dummy_tracks:
            seq.add([clip.delete for clip in dummy_track.clips])

        return seq.done()

    def on_tracks_change(self):
        # type: () -> None
        self._map_optional_audio_tail_track()
        super(ExternalSynthTrack, self).on_tracks_change()
        self._link_clip_slots()

    def _on_last_beat_passed_event(self, _):
        # type: (LastBeatPassedEvent) -> None
        pass

    def _map_optional_audio_tail_track(self):
        # type: () -> None
        has_tail_track = len(self.base_track.sub_tracks) > 2 and len(self.base_track.sub_tracks[2].devices) == 0

        if has_tail_track and not self.audio_tail_track:
            track = self.base_track.sub_tracks[2]
            self.audio_tail_track = SimpleAudioTailTrack(track._track, track._index)
            self.audio_tail_track.abstract_group_track = self
            self.audio_tail_track.group_track = self.base_track
            Scheduler.defer(self.audio_tail_track.configure)
            self.audio_tail_track.track_name.disconnect()
            Scheduler.defer(partial(setattr, self.audio_tail_track, "name", SimpleAudioTailTrack.DEFAULT_NAME))
        elif not has_tail_track:
            self.audio_tail_track = None

    @classmethod
    def is_group_track_valid(cls, base_group_track):
        # type: (SimpleTrack) -> bool
        if len(base_group_track.sub_tracks) < 2:
            return False

        if not isinstance(base_group_track.sub_tracks[0], SimpleMidiTrack):
            return False
        if not isinstance(base_group_track.sub_tracks[1], SimpleAudioTrack):
            return False

        for track in base_group_track.sub_tracks[2:]:
            if not isinstance(track, SimpleAudioTrack):
                return False

        return True

    def on_scenes_change(self):
        # type: () -> None
        self._link_clip_slots()

    def _get_dummy_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        main_tracks_length = 3 if self.audio_tail_track else 2
        for track in self.base_track.sub_tracks[main_tracks_length:]:
            yield track

    def _link_clip_slots(self):
        # type: () -> None
        if len(self._clip_slot_synchronizers) == len(self.midi_track.clip_slots):
            return

        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()

        self._clip_slot_synchronizers = [
            ClipSlotSynchronizer(midi_clip_slot, audio_clip_slot)
            for midi_clip_slot, audio_clip_slot in
            itertools.izip(  # type: ignore[attr-defined]
                self.midi_track.clip_slots, self.audio_track.clip_slots
            )
        ]

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        self._external_device = find_if(lambda d: d.is_external_device, self.midi_track.devices)
        if self._external_device is None:
            raise Protocol0Warning("%s should have an external device" % self)

    @property
    def instrument(self):
        # type: () -> InstrumentInterface
        return cast(InstrumentInterface, self.midi_track.instrument or self.audio_track.instrument)

    @property
    def clips(self):
        # type: () -> List[Clip]
        clip_slots = cast(List[ClipSlot],
                          self.midi_track.clip_slots) + self.audio_track.clip_slots
        if self.audio_tail_track:
            clip_slots += self.audio_tail_track.clip_slots

        return [clip_slot.clip for clip_slot in clip_slots if clip_slot.has_clip and clip_slot.clip]

    @property
    def can_be_armed(self):
        # type: () -> bool
        return True

    @property
    def is_armed(self):
        # type: () -> bool
        return all(sub_track.is_armed for sub_track in self.sub_tracks if not isinstance(sub_track, SimpleDummyTrack))

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (bool) -> None
        for track in self.sub_tracks:
            if not isinstance(track, SimpleDummyTrack):
                track.is_armed = is_armed

    @property
    def is_partially_armed(self):
        # type: () -> bool
        return any(sub_track.is_armed for sub_track in self.sub_tracks if not isinstance(sub_track, SimpleDummyTrack))

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi_track.is_playing or self.audio_track.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self.midi_track.is_recording or self.audio_track.is_recording

    @property
    def solo(self):
        # type: () -> bool
        return super(ExternalSynthTrack, self).solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        self.base_track.solo = solo
        for sub_track in self.sub_tracks:
            sub_track.solo = solo

    @property
    def color(self):
        # type: () -> int
        return self.base_track.color

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self.base_track.color = color_index
        for sub_track in self.sub_tracks:
            sub_track.color = color_index

    @property
    def computed_color(self):
        # type: () -> int
        return self.instrument.TRACK_COLOR.color_int_value

    def disconnect(self):
        # type: () -> None
        super(ExternalSynthTrack, self).disconnect()
        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()
        self._clip_slot_synchronizers = []
