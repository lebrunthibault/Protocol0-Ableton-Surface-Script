import Live
from typing import Optional, List

from protocol0.domain.lom.clip.ClipEnvelopeShowedEvent import ClipEnvelopeShowedEvent
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.automation.ClipAutomationEnvelope import ClipAutomationEnvelope
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils import scroll_values


class ClipAutomation(object):
    def __init__(self, live_clip, loop):
        # type: (Live.Clip.Clip, ClipLoop) -> None
        self._live_clip = live_clip
        self._loop = loop
        self.displayed_automated_parameter = None  # type: Optional[DeviceParameter]

    def get_automated_parameters(self, device_parameters):
        # type: (List[DeviceParameter]) -> List[DeviceParameter]
        return [parameter for parameter in device_parameters if self.get_envelope(parameter)]

    def show_parameter_envelope(self, parameter):
        # type: (DeviceParameter) -> None
        ApplicationViewFacade.show_clip()
        self.show_envelope()
        # noinspection PyArgumentList
        self._live_clip.view.select_envelope_parameter(parameter._device_parameter)
        DomainEventBus.emit(ClipEnvelopeShowedEvent())
        self.displayed_automated_parameter = parameter

    def scroll_envelopes(self, device_parameters, go_next=True):
        # type: (List[DeviceParameter], bool) -> None
        automated_parameters = self.get_automated_parameters(device_parameters)
        if len(automated_parameters) == 0:
            raise Protocol0Warning("No automated parameters")

        if self.displayed_automated_parameter is None:
            self.displayed_automated_parameter = automated_parameters[0]
        else:
            self.displayed_automated_parameter = scroll_values(
                automated_parameters, self.displayed_automated_parameter, go_next
            )

        self.show_parameter_envelope(self.displayed_automated_parameter)

    def get_envelope(self, parameter):
        # type: (DeviceParameter) -> Optional[ClipAutomationEnvelope]
        if self._live_clip:
            env = self._live_clip.automation_envelope(parameter._device_parameter)
            if env:
                return ClipAutomationEnvelope(env, self._loop.length)

        return None

    def select_or_create_envelope(self, parameter):
        # type: (DeviceParameter) -> None
        existing_envelope = self.get_envelope(parameter)
        if not existing_envelope:
            self._live_clip.create_automation_envelope(parameter._device_parameter)

        existing_envelope = self.get_envelope(parameter)
        existing_envelope.create_start_and_end_points()

        self.show_parameter_envelope(parameter)

    def clear_all_envelopes(self):
        # type: () -> None
        if self._live_clip:
            return self._live_clip.clear_all_envelopes()

    @handle_error
    def show_envelope(self):
        # type: () -> None
        self.hide_envelope()  # necessary
        self._live_clip.view.show_envelope()

    @handle_error
    def hide_envelope(self):
        # type: () -> None
        self._live_clip.view.hide_envelope()
