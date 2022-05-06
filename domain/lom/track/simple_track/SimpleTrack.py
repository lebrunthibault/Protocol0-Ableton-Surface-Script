import Live
from _Framework.SubjectSlot import subject_slot
from typing import cast, List, Optional

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.instrument.InstrumentFactory import InstrumentFactory
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackArmState import SimpleTrackArmState
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots
from protocol0.domain.lom.track.simple_track.SimpleTrackCreatedEvent import SimpleTrackCreatedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils import ForwardTo
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable


class SimpleTrack(AbstractTrack):
    # is_active is used to differentiate set tracks for return / master
    # we act only on active tracks
    IS_ACTIVE = True
    CLIP_SLOT_CLASS = ClipSlot

    def __init__(self, live_track, index):
        # type: (Live.Track.Track, int) -> None
        self._track = live_track  # type: Live.Track.Track
        self._index = index
        super(SimpleTrack, self).__init__(self)
        # Note : SimpleTracks represent the first layer of abstraction and know nothing about
        # AbstractGroupTracks except with self.abstract_group_track which links both layers
        # and is handled by the abg
        self.live_id = live_track._live_ptr  # type: int
        self.group_track = self.group_track  # type: Optional[SimpleTrack]
        self.sub_tracks = []  # type: List[SimpleTrack]

        self._instrument = None  # type: Optional[InstrumentInterface]
        self._view = live_track.view
        self._clip_slots = SimpleTrackClipSlots(live_track, self.CLIP_SLOT_CLASS)

        if self.IS_ACTIVE:
            self._clip_slots.build()

        self.devices = SimpleTrackDevices(live_track)
        self.devices.register_observer(self)
        self.devices.build()

        self.arm_state = SimpleTrackArmState(live_track)

        self._output_meter_level_listener.subject = None

        DomainEventBus.emit(SimpleTrackCreatedEvent(self))

    device_insert_mode = cast(int, ForwardTo("_view", "device_insert_mode"))

    def on_tracks_change(self):
        # type: () -> None
        self._link_to_group_track()
        # because we traverse the tracks left to right : sub tracks will register themselves
        if self.is_foldable:
            self.sub_tracks[:] = []

    def on_scenes_change(self):
        # type: () -> None
        self._clip_slots.build()

    def _link_to_group_track(self):
        # type: () -> None
        """
            1st layer linking
            Connect to the enclosing simple group track is any
        """
        if self._track.group_track is None:
            self.group_track = None
            return None

        self.group_track = SongFacade.simple_track_from_live_track(self._track.group_track)
        self.group_track.add_or_replace_sub_track(self)

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return list(self._clip_slots)

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, SimpleTrackDevices):
            # Refreshing is only really useful from simpler devices that change when a new sample is loaded
            if self.IS_ACTIVE and not self.is_foldable:
                self.instrument = InstrumentFactory.make_instrument_from_simple_track(self)
        elif isinstance(observable, SimpleTrackArmState) and self.arm_state.is_armed:
            DomainEventBus.emit(SimpleTrackArmedEvent(self))

    def refresh_appearance(self):
        # type: () -> None
        super(SimpleTrack, self).refresh_appearance()
        for clip_slot in self.clip_slots:
            clip_slot.refresh_appearance()

    @subject_slot("output_meter_level")
    def _output_meter_level_listener(self):
        # type: () -> None
        if not Config.TRACK_VOLUME_MONITORING:
            return
        if self._track.output_meter_level > Config.CLIPPING_TRACK_VOLUME:
            # some clicks e.g. when starting / stopping the song have this value
            if round(self._track.output_meter_level, 3) == 0.921:
                return
            Backend.client().show_warning("%s is clipping (%.3f)" % (self.abstract_track.name, self._track.output_meter_level))

    @property
    def current_monitoring_state(self):
        # type: () -> CurrentMonitoringStateEnum
        if self._track is None:
            return CurrentMonitoringStateEnum.AUTO
        return CurrentMonitoringStateEnum.from_value(self._track.current_monitoring_state)

    @current_monitoring_state.setter
    def current_monitoring_state(self, monitoring_state):
        # type: (CurrentMonitoringStateEnum) -> None
        self._track.current_monitoring_state = monitoring_state.value

    @property
    def output_meter_left(self):
        # type: () -> float
        return self._track.output_meter_left if self._track else 0

    @property
    def instrument(self):
        # type: () -> Optional[InstrumentInterface]
        return self._instrument

    @instrument.setter
    def instrument(self, instrument):
        # type: (InstrumentInterface) -> None
        self._instrument = instrument
        self.appearance.set_instrument(instrument)
        self._clip_slots.set_instrument(instrument)

    @property
    def is_playing(self):
        # type: () -> bool
        return any(clip_slot.is_playing for clip_slot in self.clip_slots)

    @property
    def is_triggered(self):
        # type: () -> bool
        return any(clip_slot.is_triggered for clip_slot in self.clip_slots)

    @property
    def is_recording(self):
        # type: () -> bool
        return any(clip for clip in self.clips if clip and clip.is_recording)

    def disconnect(self):
        # type: () -> None
        super(SimpleTrack, self).disconnect()
        for device in self.devices:
            device.disconnect()
        for clip_slot in self.clip_slots:
            clip_slot.disconnect()
