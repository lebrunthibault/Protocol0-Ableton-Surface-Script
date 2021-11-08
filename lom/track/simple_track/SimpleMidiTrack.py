from typing import Any

from protocol0.enums.Push2InstrumentModeEnum import Push2InstrumentModeEnum
from protocol0.enums.Push2MatrixModeEnum import Push2MatrixModeEnum
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleMidiTrack(SimpleTrack):
    DEFAULT_NAME = "midi"
    CLIP_CLASS = MidiClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMidiTrack, self).__init__(*a, **k)
        self.push2_selected_matrix_mode = Push2MatrixModeEnum.NOTE
        self.push2_selected_instrument_mode = Push2InstrumentModeEnum.SPLIT_MELODIC_SEQUENCER
