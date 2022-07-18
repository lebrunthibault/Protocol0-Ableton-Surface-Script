from _Framework.ControlSurface import ControlSurface, get_control_surfaces
from typing import Any

from protocol0.application.CommandBus import CommandBus
from protocol0.application.Container import Container
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.command.InitializeSongCommand import InitializeSongCommand
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class Protocol0(ControlSurface):
    def __init__(self, c_instance=None):
        # type: (Any) -> None
        super(Protocol0, self).__init__(c_instance=c_instance)

        # noinspection PyBroadException
        try:
            Container(self)
        except Exception:
            DomainEventBus.emit(ErrorRaisedEvent())
            return

        self._check_for_duplicate_p0_instance()

        CommandBus.dispatch(InitializeSongCommand())

        Logger.info("Protocol0 script loaded")

    def _check_for_duplicate_p0_instance(self):
        # type: () -> None
        p0_instances = filter(lambda cs: isinstance(cs, Protocol0), get_control_surfaces())
        Logger.info("Loaded P0 instance : %s" % p0_instances)
        if len(p0_instances) != 1:
            raise Protocol0Error("Existing instance of Protocol0 already loaded")

    def disconnect(self):
        # type: () -> None
        super(Protocol0, self).disconnect()
        DomainEventBus.emit(ScriptDisconnectedEvent())
        # without this, the events are going to be handled twice
        DomainEventBus.reset()
        Sequence.reset()

        for track in SongFacade.all_simple_tracks():
            track.disconnect()
        for scene in SongFacade.scenes():
            scene.disconnect()
