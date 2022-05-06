from math import floor

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.loop.LoopableInterface import LoopableInterface
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable


class ClipLoop(SlotManager, Observable, LoopableInterface):
    """ handle start / end markers and loop gracefully """

    def __init__(self, clip):
        # type: (Live.Clip.Clip) -> None
        super(ClipLoop, self).__init__()
        self._clip = clip

        self._loop_start_listener.subject = self._clip
        self._loop_end_listener.subject = self._clip

    def __repr__(self):
        # type: () -> str
        return "ClipLoop(name=%s, start=%s, end=%s, length=%s)" % (
            self._clip.name,
            self.start,
            self.end,
            self.length
        )

    @subject_slot("loop_start")
    def _loop_start_listener(self):
        # type: () -> None
        self.notify_observers()

    @subject_slot("loop_end")
    def _loop_end_listener(self):
        # type: () -> None
        self.notify_observers()

    @property
    def looping(self):
        # type: () -> bool
        return self._clip.looping

    @looping.setter
    def looping(self, looping):
        # type: (bool) -> None
        self._clip.looping = looping

    @property
    def start(self):
        # type: () -> float
        return self._clip.loop_start

    @start.setter
    def start(self, start):
        # type: (float) -> None
        self._clip.start_marker = start
        self._clip.loop_start = start

    @property
    def end(self):
        # type: () -> float
        return self._clip.loop_end

    @end.setter
    def end(self, end):
        # type: (float) -> None
        self._clip.end_marker = end
        self._clip.loop_end = end

    @property
    def length(self):
        # type: () -> float
        """
        For looped clips: loop length in beats.
        Casting to int to have whole beats.
        not using unwarped audio clips
        """
        if self._clip.is_audio_clip and not self._clip.warping:
            return 0
        else:
            return int(floor(self._clip.length))

    @length.setter
    def length(self, length):
        # type: (float) -> None
        self.end = self.start + length

    @property
    def bar_length(self):
        # type: () -> int
        return int(self.length / SongFacade.signature_numerator())

    @bar_length.setter
    def bar_length(self, bar_length):
        # type: (int) -> None
        self.length = bar_length * SongFacade.signature_numerator()
