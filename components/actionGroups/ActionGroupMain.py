from functools import partial

from typing import Any

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from a_protocol_0.controls.EncoderAction import EncoderAction
from a_protocol_0.controls.EncoderModifierEnum import EncoderModifierEnum
from a_protocol_0.enums.RecordTypeEnum import RecordTypeEnum


class ActionGroupMain(AbstractActionGroup):
    """
    Main manager: gathering most the functionnalities. My faithful companion when producing on Live !
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupMain, self).__init__(channel=15, record_actions_as_global=True, *a, **k)

        # DUPX modifier (both duplicate and shift)
        self.add_modifier(id=1, modifier_type=EncoderModifierEnum.DUPX)

        # SOLO modifier
        self.add_modifier(id=2, modifier_type=EncoderModifierEnum.SOLO)

        # FOLD modifier
        self.add_modifier(id=3, modifier_type=EncoderModifierEnum.FOLD)

        # PLAY_stop modifier
        self.add_modifier(id=4, modifier_type=EncoderModifierEnum.PLAY_STOP)

        # 5 AUTOmation encoder
        self.add_encoder(
            id=5,
            name="automation",
            on_press=self.parent.automationTrackManager.display_selected_parameter_automation,
            on_scroll=self.parent.automationTrackManager.scroll_automation_envelopes,
        )

        # 6: empty

        # 7: empty

        # MONitor encoder
        self.add_encoder(id=8, name="monitor", on_press=lambda: self.song.current_track.switch_monitoring)

        # RECord encoder
        self.add_encoder(
            id=9,
            name="record",
            on_scroll=self.song.scroll_recording_times,
            on_press=lambda: partial(self.song.current_track.record, RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(self.song.current_track.record, RecordTypeEnum.AUDIO_ONLY),
        )

        # 10: empty

        # SONG encoder
        self.add_encoder(id=11, name="song").add_action(
            EncoderAction(func=self.song.play_stop, modifier_type=EncoderModifierEnum.PLAY_STOP)
        ).add_action(
            EncoderAction(func=lambda: self.song.root_tracks.toggle_fold, modifier_type=EncoderModifierEnum.FOLD)
        )

        # 12 : CLIP encoder
        self.add_encoder(id=12, name="clip", on_scroll=lambda: self.song.selected_track.scroll_clips).add_action(
            EncoderAction(
                func=lambda: self.song.selected_clip and self.song.selected_clip.play_stop,
                modifier_type=EncoderModifierEnum.PLAY_STOP,
            )
        ).add_action(
            EncoderAction(func=lambda: self.song.current_track.toggle_solo, modifier_type=EncoderModifierEnum.FOLD)
        )

        # 13 : TRaCK encoder
        self.add_encoder(
            id=13,
            name="track",
            on_scroll=self.song.scroll_tracks,
            on_press=lambda: self.song.current_track.toggle_arm,
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_abstract_tracks.play_stop,
                modifier_type=EncoderModifierEnum.PLAY_STOP,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.current_track.toggle_solo,
                modifier_type=EncoderModifierEnum.SOLO,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_abstract_tracks.toggle_fold,
                modifier_type=EncoderModifierEnum.FOLD,
            )
        )

        # INSTrument encoder
        self.add_encoder(
            id=14,
            name="instrument",
            on_press=lambda: self.song.current_track.show_hide_instrument,
            on_scroll=lambda: self.song.current_track.scroll_presets_or_samples,
        )

        # 14 : CATegory encoder
        self.add_encoder(id=15, name="track category", on_scroll=self.song.scroll_track_categories).add_action(
            EncoderAction(
                func=lambda: self.song.selected_category_tracks.play_stop,
                modifier_type=EncoderModifierEnum.PLAY_STOP,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_category_tracks.toggle_solo,
                modifier_type=EncoderModifierEnum.SOLO,
            )
        )

        # 15 : SCENe encoder
        self.add_encoder(
            id=16,
            name="scene",
            on_press=lambda: self.song.selected_scene.play_stop,
            on_scroll=self.song.scroll_scenes,
        ).add_action(
            EncoderAction(func=lambda: self.song.selected_scene.play_stop, modifier_type=EncoderModifierEnum.PLAY_STOP)
        ).add_action(
            EncoderAction(func=lambda: self.song.selected_scene.toggle_solo, modifier_type=EncoderModifierEnum.SOLO)
        )
