import Live
from _Framework.SubjectSlot import SlotManager
from typing import List, Dict

from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter


class MixerDevice(SlotManager):
    def __init__(self, live_mixer_device):
        # type: (Live.MixerDevice.MixerDevice) -> None
        super(MixerDevice, self).__init__()

        parameters = live_mixer_device.sends + [live_mixer_device.volume, live_mixer_device.panning]
        self._parameters = [
            DeviceParameter(parameter, is_mixer_parameter=True) for parameter in parameters
        ]

    def to_dict(self):
        # type: () -> Dict
        return {
            "params": [p.value for p in self.parameters]
        }

    def update_from_dict(self, mixer_data):
        # type: (Dict) -> None
        assert len(self.parameters) == len(mixer_data["params"]), "Cannot update mixer device"
        for param, value in zip(self.parameters, mixer_data["params"]):
            param.value = value

    @property
    def parameters(self):
        # type: () -> List[DeviceParameter]
        return self._parameters

    def copy_to(self, mixer_device):
        # type: (MixerDevice) -> None
        for source_param, dest_param in zip(self.parameters, mixer_device.parameters):
            dest_param.value = source_param.value

    def reset(self):
        # type: () -> None
        for param in self.parameters:
            param.value = 0
