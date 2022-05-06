import itertools
from functools import partial

from typing import cast, Optional

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DrumPad import DrumPad
from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.device.DrumRackLoadedEvent import DrumRackLoadedEvent
from protocol0.domain.lom.drum.DrumCategory import DrumCategory
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class DrumRackService(object):
    def __init__(self, browser_service):
        # type: (BrowserServiceInterface) -> None
        self._browser_service = browser_service

    def load_category_drum_rack(self, drum_category):
        # type: (DrumCategory) -> Sequence
        seq = Sequence()
        try:
            self._browser_service.load_from_user_library(drum_category.drum_rack_name)
            seq.wait(10)
            seq.add(partial(self._assert_valid_rack_or_populate, drum_category))

        except Protocol0Error:
            Backend.client().show_warning("'%s' does not exist. Creating rack" % drum_category.drum_rack_name, True)
            seq.add(partial(self._browser_service.load_device_from_enum, DeviceEnum.DRUM_RACK))
            seq.add(partial(self._populate_drum_rack, drum_category))

        seq.add(partial(setattr, SongFacade.selected_track(), "name", drum_category.name))
        seq.add(SongFacade.selected_track().refresh_appearance)
        seq.add(partial(DomainEventBus.emit, DrumRackLoadedEvent()))
        return seq.done()

    def _assert_valid_rack_or_populate(self, drum_category):
        # type: (DrumCategory) -> Optional[Sequence]
        device = cast(DrumRackDevice, SongFacade.selected_track().instrument.device)
        preset_names = [p.name for p in drum_category.live_presets]

        if not device.pad_names_equal(preset_names):
            seq = Sequence()

            Backend.client().show_warning("'%s' is not synced : regenerating drum rack" % drum_category.drum_rack_name)
            seq.add(partial(self._browser_service.load_device_from_enum, DeviceEnum.DRUM_RACK))
            seq.add(partial(self._populate_drum_rack, drum_category))
            return seq.done()

        return None

    def _populate_drum_rack(self, drum_category):
        # type: (DrumCategory) -> Sequence
        device = cast(DrumRackDevice, SongFacade.selected_track().devices.selected)
        assert isinstance(device, DrumRackDevice)
        assert device == list(SongFacade.selected_track().devices)[0]
        assert len(device.filled_drum_pads) == 0
        presets = drum_category.presets
        drum_pads = [d for d in device.drum_pads if d.note >= DrumPad.INITIAL_NOTE][:len(presets)]

        seq = Sequence()
        seq.add(DrumPad.select_first_pad)

        for drum_pad, preset in itertools.izip(drum_pads, presets):
            seq.add(partial(setattr, device, "selected_drum_pad", drum_pad))
            seq.add(partial(self._browser_service.load_drum_pad_sample, preset.original_name))
            seq.wait(3)

        seq.wait(20)
        seq.add(partial(Backend.client().save_drum_rack, drum_category.drum_rack_name))
        return seq.done()

    def drum_rack_to_simpler(self):
        # type: () -> None
        assert SongFacade.selected_track().instrument
        device = cast(DrumRackDevice, SongFacade.selected_track().instrument.device)
        if not isinstance(device, DrumRackDevice):
            raise Protocol0Warning("Selected device should be a drum rack")

        self._from_drum_rack_to_simpler_notes()

        self._browser_service.load_sample("%s.wav" % device.selected_chain.name)

    def _from_drum_rack_to_simpler_notes(self):
        # type: () -> None
        device = cast(DrumRackDevice, SongFacade.selected_track().instrument.device)
        note_to_keep = device.selected_drum_pad.note
        for clip in cast(SimpleMidiTrack, SongFacade.selected_track()).clips:
            notes_to_set = []
            for note in clip.get_notes():
                if note.pitch != note_to_keep:
                    continue

                note.pitch = 60
                notes_to_set.append(note)

            clip.set_notes(notes_to_set)
