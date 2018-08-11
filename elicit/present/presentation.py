#!/usr/bin/env python3.6 -i

"""
An unusual way to give a presentation using Python.

Assumes a unicode enabled terminal.
"""

import os
import re
import sys
import base64
import signal
import tempfile
import builtins
import textwrap
import readline
import subprocess

from elicit import colors


__all__ = ['imgcat', 'divider', 'cowsay', 'dedent', 'error', 'head', 'warning',
           'bullet', 'para', 'get_resource', 'print_image', 'debugger', 'init',
           'clear', 'print_url', 'URL', 'open_resource', 'SlideController']


WIDTH = LINES = _text_wrapper = _bullet_wrapper = _old_handler = PWD = None


def _reset_size(sig, tr):
    global WIDTH, LINES, _text_wrapper, _bullet_wrapper, _old_handler
    try:
        WIDTH, LINES = os.get_terminal_size()
    except OSError:
        WIDTH, LINES = 80, 24
    _text_wrapper = textwrap.TextWrapper(width=WIDTH - 10,
                                         initial_indent=" " * 4,
                                         subsequent_indent=" " * 4,
                                         replace_whitespace=True,
                                         max_lines=LINES - 4)
    _bullet_wrapper = textwrap.TextWrapper(width=WIDTH - 10,
                                           initial_indent=" " * 4,
                                           subsequent_indent=" " * 6,
                                           replace_whitespace=True,
                                           max_lines=LINES - 4)
    if callable(_old_handler):
        _old_handler(sig, tr)


_reset_size(signal.SIGWINCH, None)
_old_handler = signal.signal(signal.SIGWINCH, _reset_size)

clear = colors.clear

def xterm_divider():
    lines = os.get_terminal_size().columns - 6
    line = '  ◀' + '═' * lines + '▶\n'
    sys.stdout.write(line)


def iterm_divider():
    img = get_resource("separator-1.png")
    sys.stdout.buffer.write(
        b'\x1b]1337;File=inline=1;width=100%;height=1;preserveAspectRatio=0:' +
        base64.b64encode(img) + b'\x07')


def xterm_imgcat(imgdata):
    fd, name = tempfile.mkstemp(suffix=".png")
    os.write(fd, imgdata)
    os.close(fd)
    # img2txt is from the caca-utils package
    cmd = ["img2txt", "-f", "utf8", "-W", str(WIDTH - 20), name]
    try:
        subprocess.call(cmd)
    finally:
        os.unlink(name)


def iterm_imgcat(imgdata):
    sys.stdout.buffer.write(b'\x1b]1337;File=inline=1:' +
                            base64.b64encode(imgdata) + b'\x07\n')


def iterm_print_url(text, url):
    sys.stdout.buffer.write(
        b'\x1b]8;;%s\x07%s\x1b]8;;\x07' % (url.encode("utf-8"), text.encode("utf-8"))
    )


def open_resource(name):
    """Open a data resource in the appropriate application using a command."""
    fname = os.path.join(PWD, "data", name)
    subprocess.check_output(["open" if sys.platform == "darwin" else "xdg-open", fname])


def iterm_URL(text, url):
    return '\x1b]8;;{}\x07{}\x1b]8;;\x07'.format(url, text)


def xterm_URL(text, url):
    return f"{text} ({url})"


def xterm_print_url(text, url):
    sys.stdout.write(f"{text} ({url})")


def print_image(imgname):
    img = get_resource(imgname)
    imgcat(img)


def head(line):
    colors.white(line.center(WIDTH - 2))
    print("\n")


def para(text):
    print(_text_wrapper.fill(dedent(text)))
    print()


def bullet(text):
    print(_bullet_wrapper.fill(f"{colors.WHITE}• {colors.NORMAL}" + dedent(text)))


def cowsay(text):
    colors.box(text, 2, color=colors.GREEN)
    print(r"""        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
""")


_DEDENT_RE = re.compile(r'\n([ \t]+)')


def dedent(text):
    return _DEDENT_RE.sub(r" ", text)


def error(text):
    colors.box(text, 2, color=colors.RED)
    print(r"""   \   ,__,
    \  (oo)____
       (__)    )\
          ||--|| *
""")


def warning(text):
    colors.box(text, 2, color=colors.YELLOW)
    print(r"""  \
   \   \
        \ /\
        ( )
      .( o ).
""")


def get_resource(name):
    fn = os.path.join(PWD, "data", name)
    return open(fn, "rb").read()


class DisplayHook:

    def __init__(self, textstream):
        self.stream = textstream

    def __call__(self, value):
        if value is None:
            return
        _ = builtins._
        builtins._ = None
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
    elif exc is SyntaxError:
        error("Eh? " + value.args[1][3].strip())
    elif exc in (IndentationError, KeyboardInterrupt):
        sys.__excepthook__(exc, value, tb)
    else:
        debugger.post_mortem(tb, exc, value)


class SlideController:

    def __init__(self, pages):
        self.pages = pages
        self._page_i = 0

    def nextpage(self):
        page = self.pages[self._page_i]
        page()
        self._page_i = (self._page_i + 1) % len(self.pages)

    def prevpage(self):
        self._page_i = (self._page_i - 2) % len(self.pages)
        page = self.pages[self._page_i]
        page()

    def goto(self, page):
        self._page_i = max(min(page, len(self.pages)), 0)
        page = self.pages[self._page_i]
        page()


class PresoObject:

    def __init__(self, cls, text):
        self.cls = cls
        self.text = text

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)

    def __repr__(self):
        return self.text


def init(argv):
    global PWD
    PWD = os.path.realpath(os.path.dirname(argv[0]))
    builtins._ = PWD
    sys.excepthook = debugger_hook
    sys.displayhook = DisplayHook(sys.stdout)
    sys.ps1 = "{}~~😄{} ➤ ".format(colors.PROMPT_GREEN, colors.PROMPT_NORMAL)
    sys.ps2 = "...more..> "


if sys.platform == "darwin":
    readline.parse_and_bind("^I rl_complete")
    tp = os.environ.get("TERM_PROGRAM")
    if tp and "iterm" in tp.lower():
        imgcat = iterm_imgcat
        divider = iterm_divider
        print_url = iterm_print_url
        URL = iterm_URL
    else:
        imgcat = xterm_imgcat
        divider = xterm_divider
        print_url = xterm_print_url
        URL = xterm_URL
else:
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind('"\M-?": possible-completions')
    imgcat = xterm_imgcat
    divider = xterm_divider
    if "256" not in os.environ.get("TERM", "xterm"):
        warning("Colors my not display correctly.")

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab:fileencoding=utf-8
