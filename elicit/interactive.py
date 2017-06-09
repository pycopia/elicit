#!/usr/bin/env python3.6 -i

"""
An unusual way to give a presentation using Python and iTerm2. :-o
"""

import os
import re
import sys
import base64
import signal
import builtins
import textwrap
import readline
import locale
from shutil import get_terminal_size
from functools import partial


WIDTH = LINES = _text_wrapper = None
LANG, ENCODING = locale.getlocale()

def _reset_size(sig, tr):
    global WIDTH, LINES, _text_wrapper
    WIDTH, LINES = get_terminal_size()
    _text_wrapper = textwrap.TextWrapper(width=WIDTH - 10,
                                         initial_indent=" "*4,
                                         subsequent_indent=" "*4,
                                         replace_whitespace=True,
                                         max_lines=LINES - 4)
_reset_size(signal.SIGWINCH, None)
signal.signal(signal.SIGWINCH, _reset_size)


RESET = NORMAL = "\x1b[0m"
CLEAR = "\x1b[H\x1b[2J"

ITALIC_ON = "\x1b[3m"
ITALIC_OFF = "\x1b[23m"

UNDERLINE_ON = "\x1b[4m"
UNDERLINE_OFF = "\x1b[24m"

INVERSE_ON = "\x1b[7m"
INVERSE_OFF = "\x1b[27m"

RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
MAGENTA = "\x1b[35m"
CYAN = "\x1b[36m"
GREY = "\x1b[37m"

LT_RED = "\x1b[31:01m"
LT_GREEN = "\x1b[32:01m"
LT_YELLOW = "\x1b[33;01m"
LT_BLUE = "\x1b[34;01m"
LT_MAGENTA = "\x1b[35;01m"
LT_CYAN = "\x1b[36;01m"
WHITE = BRIGHT = "\x1b[01m"

RED_BACK = "\x1b[41m"
GREEN_BACK = "\x1b[42m"
YELLOW_BACK = "\x1b[43m"
BLUE_BACK = "\x1b[44m"
MAGENTA_BACK = "\x1b[45m"
CYAN_BACK = "\x1b[46m"
WHITE_BACK = "\x1b[47m"

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
    "white": BRIGHT,
}


_LT_FG_MAP = {
    "red": LT_RED,
    "green": LT_GREEN,
    "yellow": LT_YELLOW,
    "blue": LT_BLUE,
    "magenta": LT_MAGENTA,
    "cyan": LT_CYAN,
    "white": BRIGHT,
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

PWD = None

def color(text, fg, bg=None, bold=False):
    try:
        c = _LT_FG_MAP[fg] if bold else _FG_MAP[fg]
        sys.stdout.write(c + _BG_MAP[bg] + text + RESET)
    except KeyError:
        raise ValueError("Bad color value: {},{}".format(fg, bg))


red = partial(color, fg="red")
green = partial(color, fg="green")
blue = partial(color, fg="blue")
cyan = partial(color, fg="cyan")
magenta = partial(color, fg="magenta")
yellow = partial(color, fg="yellow")
white = partial(color, fg="white")


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
    tt = "{}{}{}".format(UL, hor*(len(text)+2), UR)
    bt = "{}{}{}".format(LL, hor*(len(text)+2), LR)
    ml = "{} {}{}{} {}".format(vert, color, text, RESET, vert)
    sys.stdout.write("\n".join((tt, ml, bt)))
    sys.stdout.write("\n")


def imgcat(imgdata):
    sys.stdout.buffer.write(b'\x1b]1337;File=inline=1:' + base64.b64encode(imgdata) + b'\x07\n')


def divider(img):
    sys.stdout.buffer.write(
        b'\x1b]1337;File=inline=1;width=100%;height=1;preserveAspectRatio=0:' + base64.b64encode(img) + b'\x07')


def cowsay(text):
    box(text, 2, color=GREEN)
    print(r"""        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
""")

def clear():
    sys.stdout.write(CLEAR)


_DEDENT_RE = re.compile(r'\n([ \t]+)')

def dedent(text):
    return _DEDENT_RE.sub(r" ", text)


def error(text):
    box(text, 2, color=RED)
    print(r"""   \   ,__,
    \  (oo)____
       (__)    )\
          ||--|| *
""")

def warning(text):
    box(text, 2, color=YELLOW)
    print(r"""  \
   \   \
        \ /\
        ( )
      .( o ).
""")


def para(text):
    print()
    print(_text_wrapper.fill(dedent(text)))
    print()


def get_resource(name):
    return open(os.path.join(PWD, name), "rb").read()


class DisplayHook:

    def __init__(self, textstream):
        self.stream = textstream

    def __call__(self, value):
        if value is None:
            return
        _ = builtins._
        builtins._ = None
        if callable(value):
            value = value()
        if value is None:
            builtins._ = _
            return
        text = repr(value)
        try:
            self.stream.write(text)
        except UnicodeEncodeError:
            bs = text.encode(self.stream.encoding, 'backslashreplace')
            self.stream.buffer.write(bs)
        self.stream.write("\n")
        builtins._ = value


class _MakeDebugger(object):
    def __getattr__(self, name):
        global debugger
        modname = os.environ.get("PYTHON_DEBUGGER", "pdb")
        __import__(modname)
        debugger = sys.modules[modname]
        return getattr(debugger, name)

debugger = _MakeDebugger()


def debugger_hook(exc, value, tb):
    if exc is NameError:
        error(value.args[0])
    elif exc is SyntaxError:  # treat it as a shell command
        os.system(value.args[1][3].strip())
    elif exc in (IndentationError, KeyboardInterrupt):
        sys.__excepthook__(exc, value, tb)
    else:
        debugger.post_mortem(tb, exc, value)


def init(argv):
    global PWD
    PWD = os.path.realpath(os.path.dirname(argv[0]))
    builtins._ = PWD
    sys.excepthook = debugger_hook
    sys.displayhook = DisplayHook(sys.stdout)
    sys.ps1 = "🐍  > "
    sys.ps2 = "more> "
    readline.parse_and_bind("^I rl_complete")

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab:fileencoding=utf-8
