#!/usr/bin/env python3.5 -i

"""
Color builders for color terminals.
"""

import sys
from functools import partial


__all__ = ['color', 'color256', 'underline', 'inverse', 'box', 'clear']


RESET = NORMAL = "\x1b[0m"
CLEAR = "\x1b[H\x1b[2J"

ITALIC_ON = "\x1b[3m"
ITALIC_OFF = "\x1b[23m"

UNDERLINE_ON = "\x1b[4m"
UNDERLINE_OFF = "\x1b[24m"

INVERSE_ON = "\x1b[7m"
INVERSE_OFF = "\x1b[27m"

BLACK = "\x1b[30m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
MAGENTA = "\x1b[35m"
CYAN = "\x1b[36m"
GREY = "\x1b[37m"

LT_RED = "\x1b[31;01m"
LT_GREEN = "\x1b[32;01m"
LT_YELLOW = "\x1b[33;01m"
LT_BLUE = "\x1b[34;01m"
LT_MAGENTA = "\x1b[35;01m"
LT_CYAN = "\x1b[36;01m"
LT_GREY = WHITE = "\x1b[37;01m"
BRIGHT = "\x1b[01m"

RED_BACK = "\x1b[41m"
GREEN_BACK = "\x1b[42m"
YELLOW_BACK = "\x1b[43m"
BLUE_BACK = "\x1b[44m"
MAGENTA_BACK = "\x1b[45m"
CYAN_BACK = "\x1b[46m"
WHITE_BACK = "\x1b[47m"

UNDERSCORE = "\x1b[4m"
BLINK = "\x1b[5m"
DEFAULT = "\x1b[39;49m"

PROMPT_START_IGNORE = '\001'
PROMPT_END_IGNORE = '\002'

PROMPT_GREEN = PROMPT_START_IGNORE + GREEN + PROMPT_END_IGNORE
PROMPT_NORMAL = PROMPT_START_IGNORE + NORMAL + PROMPT_END_IGNORE

_FG_MAP = {
    "red": RED,
    "green": GREEN,
    "yellow": YELLOW,
    "blue": BLUE,
    "magenta": MAGENTA,
    "cyan": CYAN,
    "grey": GREY,
    "gray": GREY,
    "white": WHITE,
}


_LT_FG_MAP = {
    "red": LT_RED,
    "green": LT_GREEN,
    "yellow": LT_YELLOW,
    "blue": LT_BLUE,
    "magenta": LT_MAGENTA,
    "cyan": LT_CYAN,
    "white": WHITE,
}

_BG_MAP = {
    "red": RED_BACK,
    "green": GREEN_BACK,
    "yellow": YELLOW_BACK,
    "blue": BLUE_BACK,
    "magenta": MAGENTA_BACK,
    "cyan": CYAN_BACK,
    "white": WHITE_BACK,
    None: "",
}


def color(text, fg, bg=None, bold=False):
    try:
        c = _LT_FG_MAP[fg] if bold else _FG_MAP[fg]
        sys.stdout.write(c + _BG_MAP[bg] + text + RESET)
    except KeyError:
        raise ValueError("Bad color value: {},{}".format(fg, bg))


def color256(text: str, fg: int, bg: int=0):
    sys.stdout.write("\x1b[38;5;{};48;5;{}m".format(fg, bg))
    sys.stdout.write(text)
    sys.stdout.write(RESET)


red = partial(color, fg="red")
green = partial(color, fg="green")
blue = partial(color, fg="blue")
cyan = partial(color, fg="cyan")
magenta = partial(color, fg="magenta")
yellow = partial(color, fg="yellow")
grey = partial(color, fg="grey")
white = partial(color, fg="white")

lt_red = partial(color, fg="red", bold=True)
lt_green = partial(color, fg="green", bold=True)
lt_blue = partial(color, fg="blue", bold=True)
lt_cyan = partial(color, fg="cyan", bold=True)
lt_magenta = partial(color, fg="magenta", bold=True)
lt_yellow = partial(color, fg="yellow", bold=True)


def underline(text):
    sys.stdout.write(UNDERLINE_ON + text + UNDERLINE_OFF)


def inverse(text):
    sys.stdout.write(INVERSE_ON + text + INVERSE_OFF)


#                 UL  hor   vert  UR  LL   LR
_BOXCHARS = {1: ['┏', '━', '┃', '┓', '┗', '┛'],
             0: ['╔', '═', '║', '╗', '╚', '╝'],
             2: ['┌', '─', '│', '┐', '└', '┘']}


def box(text, level=0, color=GREY):
    UL, hor, vert, UR, LL, LR = _BOXCHARS[level]
    tt = "{}{}{}".format(UL, hor * (len(text) + 2), UR)
    bt = "{}{}{}".format(LL, hor * (len(text) + 2), LR)
    ml = "{} {}{}{} {}".format(vert, color, text, RESET, vert)
    sys.stdout.write("\n")
    sys.stdout.write("\n".join((tt, ml, bt)))
    sys.stdout.write("\n")


def clear():
    sys.stdout.write(CLEAR)


# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab:fileencoding=utf-8
