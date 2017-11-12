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

__all__ = ['Theme', 'BasicTheme', 'ANSITheme']

from . import colors


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
        cls.NORMAL = cls.RESET = colors.RESET
        cls.BOLD = cls.BRIGHT = colors.BRIGHT
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
        cls.UNDERSCORE = colors.UNDERSCORE
        cls.BLINK = colors.BLINK
        cls.help_text = cls.WHITE


class ANSITheme(BasicTheme):
    """Defines tunable parameters for the UserInterface, to provide
    different color schemes and prompts.
    """

    @classmethod
    def _setcolors(cls):
        # ANSI escapes for color terminals
        cls.NORMAL = cls.RESET = colors.RESET
        cls.BOLD = cls.BRIGHT = colors.BRIGHT
        cls.BLACK = colors.BLACK
        cls.RED = colors.RED
        cls.GREEN = colors.GREEN
        cls.YELLOW = colors.YELLOW
        cls.BLUE = colors.BLUE
        cls.MAGENTA = colors.MAGENTA
        cls.CYAN = colors.CYAN
        cls.WHITE = colors.GREY
        cls.GREY = colors.GREY
        cls.BRIGHTRED = colors.LT_RED
        cls.BRIGHTGREEN = colors.LT_GREEN
        cls.BRIGHTYELLOW = colors.LT_YELLOW
        cls.BRIGHTBLUE = colors.LT_BLUE
        cls.BRIGHTMAGENTA = colors.LT_MAGENTA
        cls.BRIGHTCYAN = colors.LT_CYAN
        cls.BRIGHTWHITE = colors.WHITE
        cls.DEFAULT = colors.DEFAULT
        cls.UNDERSCORE = colors.UNDERSCORE
        cls.BLINK = colors.BLINK
        cls.help_text = cls.BRIGHTWHITE


DefaultTheme = ANSITheme
