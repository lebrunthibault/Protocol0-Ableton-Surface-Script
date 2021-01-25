from functools import partial

from typing import List

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.clip_slot.AutomationAudioClipSlot import AutomationAudioClipSlot
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer


class AutomationAudioTrack(AbstractAutomationTrack):
    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationAudioTrack, self).__init__(*a, **k)
        self.clip_slots = self.clip_slots  # type: List[AutomationAudioClipSlot]
        self.automated_device = None  # type: Device
        self.automated_parameter = None  # type: DeviceParameter

    def _added_track_init(self):
        if self.group_track is None:
            raise Protocol0Error("An automation track should always be grouped")

        self.has_monitor_in = True
        seq = Sequence()
        seq.add(self.clear_devices)
        seq.add(partial(self.parent.browserManager.load_rack_device, self.base_name.split(":")[1]))
        seq.add(self._get_automated_device_and_parameter)

        return seq.done()

    def _get_automated_device_and_parameter(self):
        [_, device_name, parameter_name] = self.base_name.split(":")
        (device, parameter) = self.parent.deviceManager.get_device_and_parameter_from_name(track=self, device_name=device_name, parameter_name=parameter_name)
        self.automated_device = device
        self.automated_parameter = parameter
