from typing import TYPE_CHECKING, List

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.domain.track_recorder.abstract_track_recorder import AbstractTrackRecorder

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackRecorderDecorator(AbstractTrackRecorder):
    def __init__(self, recorder, song):
        # type: (AbstractTrackRecorder, Song) -> None
        super(TrackRecorderDecorator, self).__init__(track=recorder.track, song=song)
        self.recorder = recorder
        self._track = recorder.track

    def legend(self, bar_length):
        # type: (int) -> str
        return self.recorder.legend(bar_length)

    @property
    def recording_scene_index(self):
        # type: () -> int
        return self.recorder.recording_scene_index

    @property
    def recording_scene(self):
        # type: () -> Scene
        return self.recorder.recording_scene

    def set_recording_scene_index(self, recording_scene_index):
        # type: (int) -> None
        self.recorder.set_recording_scene_index(recording_scene_index)

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return self.recorder._recording_tracks

    @property
    def _main_recording_track(self):
        # type: () -> SimpleTrack
        return self.recorder._main_recording_track

    def pre_record(self):
        # type: () -> Sequence
        return self.recorder.pre_record()

    def record(self, bar_length):
        # type: (float) -> Sequence
        return self.recorder.record(bar_length)

    def post_audio_record(self):
        # type: () -> None
        return self.recorder.post_audio_record()

    def post_record(self, bar_length):
        # type: (int) -> None
        return self.recorder.post_record(bar_length)

    def cancel_record(self):
        # type: () -> None
        return self.recorder.cancel_record()
