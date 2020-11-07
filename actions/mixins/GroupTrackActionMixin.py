from typing import Optional, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack


# noinspection PyTypeHints
class GroupTrackActionMixin(object):
    def action_arm(self):
        # type: ("GroupTrack", Optional[bool]) -> None
        self.clyphx.clips[0].color = Colors.ARM
        self.group.is_folded = False
        self.clyphx.arm = False
        self.midi.arm = self.audio.arm = True

        if self.song.current_action_name in ("sel_ext", "arm_ext"):
            self.audio.has_monitor_in = True

        # activate the rev2 editor for this group track
        if self.is_prophet_group_track:
            self.action_sel()

    def action_unarm(self, direct_unarm=False):
        # type: ("GroupTrack", bool) -> None
        self.color = self.color
        self.group.is_folded = True
        self.clyphx.arm = direct_unarm
        self.audio.arm = self.midi.arm = False
        if self.audio.is_playing:
            self.clyphx.clips[1].color = Colors.PLAYING
        self.audio.has_monitor_in = False

    def action_sel(self):
        # type: ("GroupTrack") -> Optional[str]
        if self.song.selected_track == self.selectable_track:
            self.group.is_folded = self.group.is_selected = True
            return

        self.action_arm()
        self.group.is_folded = False
        return self.selectable_track.action_sel()

    def action_switch_monitoring(self):
        # type: ("GroupTrack") -> None
        if self.midi.has_monitor_in and self.audio.has_monitor_in:
            self.midi.has_monitor_in = self.audio.has_monitor_in = False
        elif self.audio.has_monitor_in:
            self.midi.has_monitor_in = True
        else:
            self.audio.has_monitor_in = True

    def action_record_all(self):
        # type: ("GroupTrack") -> None
        self.midi.action_record_all()
        self.audio.action_record_all()

    def action_record_audio_only(self):
        # type: ("GroupTrack") -> None
        if self.midi.is_playing:
            self.song.bar_count = int(round((self.midi.playing_clip.length + 1) / 4))

        self.audio.action_record_all()

    def action_post_record(self):
        # type: ("GroupTrack") -> None
        self.song.metronome = False
        self.clyphx.clips[1].color = Colors.PLAYING
        if self.song.current_action_name == "record_ext":
            self.audio.has_monitor_in = True

        self.song.await_track_rename = True
        self.midi.action_post_record()
        self.audio.action_post_record()

    def stop(self):
        # type: ("GroupTrack") -> None
        self.midi.stop()
        self.audio.stop()

    def action_undo(self):
        # type: ("GroupTrack") -> None
        self.audio.action_undo()
        self.midi.action_undo()

