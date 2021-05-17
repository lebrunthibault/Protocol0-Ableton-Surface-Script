import os
import subprocess
from functools import partial

from typing import Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import ROOT_DIR
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import log


class KeyBoardShortcutManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(KeyBoardShortcutManager, self).__init__(*a, **k)

    def _execute_python(self, filename, *args):
        # type: (str, Any) -> int
        parameters = [str(os.getenv("PYTHONW_EXE")), ROOT_DIR + "\\scripts\\python\\%s" % filename]
        for arg in args:
            parameters.append(str(arg))

        child = subprocess.Popen(parameters)
        child.communicate()
        return child.returncode

    def _execute_ahk(self, filename, *args):
        # type: (str, Any) -> int
        parameters = [str(os.getenv("AHK_EXE")), ROOT_DIR + "\\scripts\\ahk\\%s" % filename]
        for arg in args:
            parameters.append(str(arg))

        child = subprocess.Popen(parameters)
        child.communicate()
        return child.returncode

    @log
    def send_keys(self, keys, repeat=False):
        # type: (str, bool) -> Sequence
        seq = Sequence(silent=True)
        seq.add(self.parent.clyphxNavigationManager.focus_main)
        seq.add(partial(self._execute_python, "send_keys.py", keys))
        if repeat:
            # here trying to mitigate shortcuts not received by Live god knows why ..
            seq.add(wait=5)
            seq.add(partial(self._execute_python, "send_keys.py", keys))

        return seq.done()

    def focus_window(self, window_name):
        # type: (str) -> Sequence
        seq = Sequence(bypass_errors=True, silent=True)
        seq.add(self.parent.clyphxNavigationManager.focus_main)
        seq.add(partial(self._execute_python, "focus_window.py", window_name))

        return seq.done()

    def focus_logs(self):
        # type: () -> None
        self.focus_window("logs terminal")

    def send_click(self, x, y):
        # type: (int, int) -> None
        self._execute_python("send_click.py", x, y)

    def show_hide_plugins(self):
        # type: () -> None
        self.send_keys("^%p")

    def show_plugins(self):
        # type: () -> None
        self.send_keys("^{F1}")

    def hide_plugins(self):
        # type: () -> None
        self.send_keys("^{F2}")

    def click_clip_fold_notes(self):
        # type: () -> None
        self.send_click(418, 686)
        self.send_click(418, 686)

    def double_click_envelopes_show_box(self):
        # type: () -> None
        self.send_click(86, 1014)
        self.send_click(86, 1014)

    def toggle_device_button(self, x, y, activate=True):
        # type: (int, int, bool) -> None
        self._execute_python("toggle_ableton_button.py", str(x), str(y), "1" if activate else "0")

    def is_plugin_window_visible(self, plugin_name=""):
        # type: (str) -> bool
        """ we cannot do ctrl alt p and recheck inside of ahk because the sleeping prevents the window to show """
        self.parent.log_warning(plugin_name)
        return bool(self._execute_ahk("is_plugin_visible.ahk", str(plugin_name)))

    def show_and_activate_rev2_editor(self):
        # type: () -> None
        """ the activation button can be at 2 positions depending on idk what"""
        self.show_plugins()
        self.send_click(921, 550)  # click on activate (high position)
        self.send_click(856, 592)  # click on activate (high position)
        self.send_click(1416, 20)  # click on nothing (to not trigger and additional click)

    def group_track(self):
        # type: () -> None
        self.send_keys("^{F4}")

    def up(self):
        # type: () -> None
        self.send_keys("^{F5}", repeat=True)
