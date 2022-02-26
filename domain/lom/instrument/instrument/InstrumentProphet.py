from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.System import System
from protocol0.domain.track_recorder.recorder.ExternalSynthAudioRecordingEndedEvent import \
    ExternalSynthAudioRecordingEndedEvent
from protocol0.domain.track_recorder.recorder.ExternalSynthAudioRecordingStartedEvent import \
    ExternalSynthAudioRecordingStartedEvent
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class InstrumentProphet(InstrumentInterface):
    NAME = "Prophet"
    DEVICE_NAME = "rev2editor"
    TRACK_COLOR = InstrumentColorEnum.PROPHET
    ACTIVE_INSTANCE = None  # type: Optional[InstrumentProphet]

    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 3.2
    MIDI_INPUT_ROUTING_TYPE = InputRoutingTypeEnum.REV2_AUX

    def __init__(self, track, device):
        # type: (SimpleTrack, Optional[Device]) -> None
        super(InstrumentProphet, self).__init__(track, device)
        DomainEventBus.subscribe(SimpleTrackArmedEvent, self._on_simple_track_armed_event)
        DomainEventBus.subscribe(ExternalSynthAudioRecordingStartedEvent, self._on_audio_recording_started_event)
        DomainEventBus.subscribe(ExternalSynthAudioRecordingEndedEvent, self._on_audio_recording_ended_event)

    @property
    def needs_exclusive_activation(self):
        # type: () -> bool
        return InstrumentProphet.ACTIVE_INSTANCE != self

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        InstrumentProphet.ACTIVE_INSTANCE = self
        seq = Sequence()
        seq.wait(5)
        seq.add(System.client().activate_rev2_editor)
        seq.wait(5)
        return seq.done()

    def post_activate(self):
        # type: () -> Optional[Sequence]
        seq = Sequence()
        seq.add(System.client().post_activate_rev2_editor)
        seq.wait(20)
        return seq.done()

    def _on_simple_track_armed_event(self, event):
        # type: (SimpleTrackArmedEvent) -> None
        """ because prophet midi is generated by the rev2 editor which handles  """
        if event.track != self.track:
            return
        SongFacade.usamo_device().device_on = False
        self.device.device_on = True

    def _on_audio_recording_started_event(self, event):
        # type: (ExternalSynthAudioRecordingStartedEvent) -> None
        if event.track != self.track.abstract_track:
            return
        self.device.device_on = False

    def _on_audio_recording_ended_event(self, event):
        # type: (ExternalSynthAudioRecordingEndedEvent) -> None
        if event.track != self.track.abstract_track:
            return
        SongFacade.usamo_device().device_on = False
        self.device.device_on = True
