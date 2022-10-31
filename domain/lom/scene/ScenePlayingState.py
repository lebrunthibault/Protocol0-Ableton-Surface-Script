from typing import Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.shared.SongFacade import SongFacade


class ScenePlayingState(object):
    def __init__(self, clips, scene_length):
        # type: (SceneClips, SceneLength) -> None
        self._clips = clips
        self._scene_length = scene_length

    def __repr__(self):
        # type: () -> str
        return "position: %.2f, bar_position: %.2f, current_bar: %s, in_last_bar: %s" % (
            self.position,
            self.bar_position,
            self.current_bar,
            self.in_last_bar,
        )

    @property
    def is_playing(self):
        # type: () -> bool
        def _is_clip_playing(clip):
            # type: (Clip) -> bool
            if clip is None or not clip.is_playing or clip.muted:
                return False
            # tail clips of audio tracks
            if isinstance(clip, AudioClip) and clip.bar_length > self._scene_length.bar_length:
                return False

            return True

        return SongFacade.is_playing() and any(
            _is_clip_playing(clip) for clip in self._clips
        )

    @property
    def position(self):
        # type: () -> float
        if self._longest_un_muted_clip:
            return self._longest_un_muted_clip.playing_position.position
        else:
            return 0

    @property
    def bar_position(self):
        # type: () -> float
        return self.position / SongFacade.signature_numerator()

    @property
    def current_bar(self):
        # type: () -> int
        if self._scene_length.length == 0:
            return 0
        return int(self.bar_position)

    @property
    def in_last_bar(self):
        # type: () -> bool
        return self.current_bar == self._scene_length.bar_length - 1

    @property
    def _longest_un_muted_clip(self):
        # type: () -> Optional[Clip]
        clips = [clip for clip in self._clips if (not clip.is_recording or float(clip.length).is_integer()) and not clip.muted]
        if len(clips) == 0:
            return None
        else:
            return max(clips, key=lambda c: c.length)
