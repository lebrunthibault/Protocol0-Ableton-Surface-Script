from math import floor

from ClyphX_Pro.ClyphXComponentBase import ClyphXComponentBase, schedule
from typing import Any, Optional

from _Framework.SubjectSlot import subject_slot
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.scheduler.BeatChangedEvent import BeatChangedEvent
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.shared.SongFacade import SongFacade


class SyncedScheduler(ClyphXComponentBase):
    """ SyncedScheduler schedules action lists to be triggered after a specified
    number of bars. """

    def __init__(self, unschedule_on_stop, *a, **k):
        # type: (bool, Any, Any) -> None
        super(SyncedScheduler, self).__init__(*a, **k)
        self._unschedule_on_stop = unschedule_on_stop
        self._last_beat = None  # type: Optional[int]
        self._last_sixteenth = None  # type: Optional[int]
        self._last_32th = False
        self._bar_ending = False
        self._pending_action_list = {}
        self._pending_precise_action_list = {}
        self._is_playing_listener.subject = self._song
        self._current_song_time_listener.subject = self._song

    def schedule_message(self, num_beats, msg):
        # type: (float, Any) -> None
        """ Schedules the given action_list to be triggered after the specified number
        of bars. """
        action = {'beats': num_beats, 'sixteenths': 0, 'ticks': 0}
        if float(num_beats).is_integer():
            self._pending_action_list[msg] = action
        else:
            beats = floor(num_beats)
            beats_reminder = (num_beats - beats)
            sixteenth_float_value = float(1) / SongFacade.signature_numerator()
            tick_float_value = float(1) / 60

            sixteenths = beats_reminder // sixteenth_float_value
            sixteenths_float_reminder = beats_reminder % sixteenth_float_value
            ticks = sixteenths_float_reminder // tick_float_value

            action["beats"] = beats
            action["sixteenths"] = sixteenths
            action["ticks"] = ticks

            self._pending_precise_action_list[msg] = action

    @subject_slot('is_playing')
    def _is_playing_listener(self):
        # type: () -> None
        if not self._song.is_playing and self._unschedule_on_stop:
            self._pending_action_list = {}
        self._last_beat = None
        self._last_sixteenth = None
        self._last_32th = False
        self._bar_ending = False

    @subject_slot('current_song_time')
    def _current_song_time_listener(self):
        # type: () -> None
        if not self._song.is_playing:
            return

        current_beat_time = SongFacade.current_beats_song_time()
        current_beat = current_beat_time.beats
        current_sixteenth = current_beat_time.sub_division
        current_tick = current_beat_time.ticks

        if current_beat == SongFacade.signature_numerator() and current_sixteenth == 4:
            if current_tick >= 30:  # out of 60 (1/32th)
                if not self._last_32th:
                    self._last_32th = True
                    DomainEventBus.notify(Last32thPassedEvent())
            if current_tick >= 45:  # out of 60 (1/64th)
                if not self._bar_ending:
                    self._bar_ending = True
                    DomainEventBus.notify(BarEndingEvent())
        else:
            self._last_32th = False
            self._bar_ending = False

        for k, v in self._pending_precise_action_list.items():
            if v['beats'] == 0 and v['sixteenths'] == 0 and current_tick > v['ticks']:
                schedule(k)
                del self._pending_precise_action_list[k]

        if self._last_sixteenth != current_sixteenth:
            self._last_sixteenth = current_sixteenth
            for k, v in self._pending_precise_action_list.items():
                if v['beats'] == 0:
                    v['sixteenths'] -= 1
                if v['sixteenths'] < 0:
                    schedule(k)
                    del self._pending_precise_action_list[k]

        if self._last_beat != current_beat:
            self._last_beat = current_beat

            DomainEventBus.notify(BeatChangedEvent())

            for k, v in self._pending_precise_action_list.items():
                v['beats'] -= 1

            for k, v in self._pending_action_list.items():
                v['beats'] -= 1
                if v['beats'] == 0:
                    schedule(k)
                    del self._pending_action_list[k]

    def disconnect(self):
        # type: () -> None
        super(SyncedScheduler, self).disconnect()
        self._pending_action_list = {}
        return
