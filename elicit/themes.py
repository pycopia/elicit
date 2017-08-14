#!/usr/bin/env python3.5
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Prompt and styled output themes.
"""

class Theme:
    NORMAL = RESET = ""
    BOLD = BRIGHT = ""
    BLACK = ""
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    MAGENTA = ""
    CYAN = ""
    WHITE = ""
    DEFAULT = ""
    GREY = ""
    BRIGHTRED = ""
    BRIGHTGREEN = ""
    BRIGHTYELLOW = ""
    BRIGHTBLUE = ""
    BRIGHTMAGENTA = ""
    BRIGHTCYAN = ""
    BRIGHTWHITE = ""
    UNDERSCORE = ""
    BLINK = ""
    help_text = WHITE

    def __init__(self, ps1="> ", ps2="more> ", ps3="choose", ps4="-> "):
        self._ps1 = ps1  # main prompt
        self._ps2 = ps2  # more input needed
        self._ps3 = ps3  # choose prompt
        self._ps4 = ps4  # input prompt
        self._setcolors()

    def _set_ps1(self, new):
        self._ps1 = str(new)

    def _set_ps2(self, new):
        self._ps2 = str(new)

    def _set_ps3(self, new):
        self._ps3 = str(new)

    def _set_ps4(self, new):
        self._ps4 = str(new)

    _setcolors = lambda c: None
    ps1 = property(lambda s: s._ps1, _set_ps1, None, "primary prompt")
    ps2 = property(lambda s: s._ps2, _set_ps2, None, "more input needed")
    ps3 = property(lambda s: s._ps3, _set_ps3, None, "choose prompt")
    ps4 = property(lambda s: s._ps4, _set_ps4, None, "text input prompt")


class BasicTheme(Theme):

    @classmethod
    def _setcolors(cls):
        "Base class for themes. Defines interface."
        cls.NORMAL = cls.RESET = "\x1b[0m"
        cls.BOLD = cls.BRIGHT = "\x1b[1m"
        cls.BLACK = ""
        cls.RED = ""
        cls.GREEN = ""
        cls.YELLOW = ""
        cls.BLUE = ""
        cls.MAGENTA = ""
        cls.CYAN = ""
        cls.WHITE = ""
        cls.DEFAULT = ""
        cls.GREY = ""
        cls.BRIGHTRED = ""
        cls.BRIGHTGREEN = ""
        cls.BRIGHTYELLOW = ""
        cls.BRIGHTBLUE = ""
        cls.BRIGHTMAGENTA = ""
        cls.BRIGHTCYAN = ""
        cls.BRIGHTWHITE = ""
        cls.UNDERSCORE = "\x1b[4m"
        cls.BLINK = "\x1b[5m"
        cls.help_text = cls.WHITE


class ANSITheme(BasicTheme):
    """Defines tunable parameters for the UserInterface, to provide
    different color schemes and prompts.
    """

    @classmethod
    def _setcolors(cls):
        # ANSI escapes for color terminals
        cls.NORMAL = cls.RESET = "\x1b[0m"
        cls.BOLD = cls.BRIGHT = "\x1b[01m"
        cls.BLACK = "\x1b[30m"
        cls.RED = "\x1b[31m"
        cls.GREEN = "\x1b[32m"
        cls.YELLOW = "\x1b[33m"
        cls.BLUE = "\x1b[34m"
        cls.MAGENTA = "\x1b[35m"
        cls.CYAN = "\x1b[36m"
        cls.WHITE = "\x1b[37m"
        cls.GREY = "\x1b[30;01m"
        cls.BRIGHTRED = "\x1b[31;01m"
        cls.BRIGHTGREEN = "\x1b[32;01m"
        cls.BRIGHTYELLOW = "\x1b[33;01m"
        cls.BRIGHTBLUE = "\x1b[34;01m"
        cls.BRIGHTMAGENTA = "\x1b[35;01m"
        cls.BRIGHTCYAN = "\x1b[36;01m"
        cls.BRIGHTWHITE = "\x1b[37;01m"
        cls.DEFAULT = "\x1b[39;49m"
        cls.UNDERSCORE = "\x1b[4m"
        cls.BLINK = "\x1b[5m"
        cls.help_text = cls.BRIGHTWHITE


DefaultTheme = ANSITheme

