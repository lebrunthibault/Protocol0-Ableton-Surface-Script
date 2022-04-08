from typing import Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.shared.SongFacade import SongFacade


class ScenePlayingPosition(object):
    def __init__(self, clips, scene_length):
        # type: (SceneClips, SceneLength) -> None
        self._clips = clips
        self._scene_length = scene_length

    @property
    def position(self):
        # type: () -> float
        if self._longest_un_muted_clip:
            return self._longest_un_muted_clip.playing_position - self._longest_un_muted_clip.start_marker
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
    def _longest_un_muted_clip(self):
        # type: () -> Optional[Clip]
        clips = [clip for clip in self._clips if not clip.is_recording and not clip.muted]
        if len(clips) == 0:
            return None
        else:
            return max(clips, key=lambda c: c.length)
