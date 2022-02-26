from typing import TYPE_CHECKING

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


class ClipLoop(object):
    """ handle start / end markers and loop gracefully """
    def __init__(self, clip):
        # type: (Clip) -> None
        self._clip = clip

    @property
    def start(self):
        # type: () -> float
        return self._clip.start_marker

    @start.setter
    def start(self, start):
        # type: (float) -> None
        assert start >= 0, "start should be >= 0"
        if start % SongFacade.signature_numerator() != 0:
            Backend.client().show_warning("start should be a bar length : %s" % self._clip)
            return
        if start >= self._clip.end_marker:
            Backend.client().show_warning("Cannot set start >= end_marker : %s" % self._clip)
            return
        if start >= self._clip.loop_end:
            Backend.client().show_warning("Cannot set start >= loop_end : %s" % self._clip)
            return

        self._clip.start_marker = start
        self._clip.loop_start = start

    @property
    def end(self):
        # type: () -> float
        return self._clip.end_marker

    @end.setter
    def end(self, end):
        # type: (float) -> None
        if end % SongFacade.signature_numerator() != 0:
            Backend.client().show_warning("end should be a bar length : %s" % self._clip)
            return
        if end <= self._clip.start_marker:
            Backend.client().show_warning("Cannot set end <= start_marker : %s" % self._clip)
            return
        if end <= self._clip.loop_start:
            Backend.client().show_warning("Cannot set end <= loop_start : %s" % self._clip)
            return

        self._clip.end_marker = end
        self._clip.loop_end = end

    def scroll_start(self, go_next):
        # type: (bool) -> None
        factor = 1 if go_next else -1
        start = self.start + (factor * SongFacade.signature_numerator())
        if start >= self.end or start < 0:
            return
        self.start = start

    def scroll_end(self, go_next):
        # type: (bool) -> None
        factor = 1 if go_next else -1
        end = self.end + (factor * SongFacade.signature_numerator())
        if end <= self.start:
            return
        self.end = end

    def scroll_loop(self, go_next):
        # type: (bool) -> None
        factor = 1 if go_next else -1
        start = self.start + (factor * SongFacade.signature_numerator())
        end = self.end + (factor * SongFacade.signature_numerator())
        if start < 0:
            return

        self.start = start
        self.end = end

    def set_loop_bar_length(self, bar_length):
        # type: (int) -> None
        self.end = self.start + (bar_length * SongFacade.signature_numerator())
