from protocol0.config import BAR_LENGTHS
from protocol0.utils.decorators import save_to_song_data, song_synchronizable_class
from protocol0.utils.utils import scroll_values


@song_synchronizable_class
class InterfaceState(object):
    SELECTED_RECORDING_BAR_LENGTH = 4

    RECORD_CLIP_TAILS = False  # records one more bar of audio to make editing easier
    SELECTED_CLIP_TAILS_BAR_LENGTH = 1

    PROTECTED_MODE_ACTIVE = True  # protected mode prevents certain actions to be made

    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False

    @classmethod
    @save_to_song_data
    def toggle_record_clip_tails(cls):
        # type: () -> None
        cls.RECORD_CLIP_TAILS = not cls.RECORD_CLIP_TAILS
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Record clip tails %s (%s)" % ("ON" if cls.RECORD_CLIP_TAILS else "OFF", cls.SELECTED_CLIP_TAILS_BAR_LENGTH))

    @classmethod
    @save_to_song_data
    def scroll_clip_tails_bar_lengths(cls, go_next):
        # type: (bool) -> None
        cls.RECORD_CLIP_TAILS = True
        cls.SELECTED_CLIP_TAILS_BAR_LENGTH = scroll_values(
            BAR_LENGTHS, cls.SELECTED_CLIP_TAILS_BAR_LENGTH, go_next
        )
        cls.show_selected_bar_length("CLIP TAIL", cls.SELECTED_CLIP_TAILS_BAR_LENGTH)

    @classmethod
    @save_to_song_data
    def toggle_protected_mode(cls):
        # type: () -> None
        cls.PROTECTED_MODE_ACTIVE = not cls.PROTECTED_MODE_ACTIVE
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Protected mode %s" % ("ON" if cls.PROTECTED_MODE_ACTIVE else "OFF"))

    @classmethod
    @save_to_song_data
    def scroll_recording_bar_lengths(cls, go_next):
        # type: (bool) -> None
        cls.SELECTED_RECORDING_BAR_LENGTH = scroll_values(
            BAR_LENGTHS, cls.SELECTED_RECORDING_BAR_LENGTH, go_next
        )
        cls.show_selected_bar_length("RECORDING", cls.SELECTED_RECORDING_BAR_LENGTH)

    @classmethod
    def show_selected_bar_length(cls, title, bar_length):
        # type: (str, int) -> None
        bar_display_count = "%s bar%s" % (bar_length, "s" if abs(bar_length) != 1 else "")
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Selected %s : %s" % (title, bar_display_count))
