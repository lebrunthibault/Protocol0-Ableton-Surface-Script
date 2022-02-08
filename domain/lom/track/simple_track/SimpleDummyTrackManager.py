from functools import partial

from typing import Optional

from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackAddedEvent import SimpleDummyTrackAddedEvent
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.BrowserManagerInterface import BrowserManagerInterface
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class SimpleDummyTrackManager(object):
    def __init__(self, browser_manager):
        # type: (BrowserManagerInterface) -> None
        self._browser_manager = browser_manager
        self._parameter_type = None  # type: Optional[str]
        DomainEventBus.subscribe(SimpleDummyTrackAddedEvent, self._on_simply_dummy_track_added_event)

    def _on_simply_dummy_track_added_event(self, event):
        # type: (SimpleDummyTrackAddedEvent) -> Sequence
        # creating automation
        seq = Sequence()
        seq.add(self._select_parameters)
        seq.add(self._insert_device)
        seq.add(wait=5)
        seq.add(partial(self._insert_dummy_clip, event.track))
        seq.add(partial(self._create_dummy_automation, event.track))
        return seq.done()

    def _select_parameters(self):
        # type: () -> Sequence
        parameters = [enum.name for enum in DeviceParameterEnum.automatable_parameters()]
        seq = Sequence()
        seq.select(question="Automated parameter", options=parameters)
        seq.add(lambda: setattr(self, "_parameter_type", seq.res))
        return seq.done()

    def _insert_device(self):
        # type: () -> Optional[Sequence]
        self.parameter_enum = DeviceParameterEnum.from_value(self._parameter_type)
        return self._browser_manager.load_device_from_enum(self.parameter_enum.device_enum)

    def _insert_dummy_clip(self, track):
        # type: (SimpleDummyTrack) -> Optional[Sequence]
        if not SongFacade.template_dummy_clip() or len(track.clips):
            return None

        cs = track.clip_slots[SongFacade.selected_scene().index]
        seq = Sequence()
        seq.add(partial(SongFacade.template_dummy_clip().clip_slot.duplicate_clip_to, cs))
        seq.add(lambda: setattr(track.clips[0], "muted", False))
        seq.add(wait=2)
        return seq.done()

    def _create_dummy_automation(self, track):
        # type: (SimpleDummyTrack) -> None
        clip = track.clip_slots[SongFacade.selected_scene().index].clip
        automated_device = track.get_device_from_enum(self.parameter_enum.device_enum)
        if automated_device is None:
            Logger.log_error("The automated device was not inserted")
            return None

        automated_parameter = automated_device.get_parameter_by_name(self.parameter_enum)

        existing_envelope = clip.automation_envelope(automated_parameter)
        if not existing_envelope:
            clip.create_automation_envelope(parameter=automated_parameter)

        clip.loop_end = 1

        clip.show_parameter_envelope(automated_parameter)
        if SongFacade.is_playing():
            clip.fire()
