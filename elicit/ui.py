#!/usr/bin/python3

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
User Interface base classes and themes.
"""

import sys
import os
import time
import textwrap
from pprint import PrettyPrinter

from . import simpleui
from . import console
from . import env

# set the PROMPT ignore depending on whether or not readline module is
# available.
try:
    import readline
    PROMPT_START_IGNORE = '\001'
    PROMPT_END_IGNORE = '\002'
except ImportError:
    readline = None
    PROMPT_START_IGNORE = ''
    PROMPT_END_IGNORE = ''


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


class UserInterface:
    """An ANSI terminal user interface for CLIs.  """
    def __init__(self, io, environment=None, theme=None):
        self._io = io
        self._env = environment or env.Environ.from_system()
        assert hasattr(self._env, "get")
        self._env["_"] = None
        self._cache = {}
        self.set_theme(theme)
        self._initfsm()
        self._printer = PrettyPrinter(indent=1, width=self._io.columns,
                                      depth=None, stream=self._io, compact=False)

    def close(self):
        if self._io is not None:
            self._io.close()
            self._io = None

    def set_theme(self, theme):
        self._theme = theme or DefaultTheme()
        assert isinstance(self._theme, Theme), "must supply a Theme object."
        self._env.setdefault("PS1", self._theme.ps1)
        self._env.setdefault("PS2", self._theme.ps2)
        self._env.setdefault("PS3", self._theme.ps3)
        self._env.setdefault("PS4", self._theme.ps4)

    def clone(self, theme=None):
        return self.__class__(self._io, self._env.copy(), theme or self._theme)

    def print(self, *objs):
        try:
            self._io.print(*objs)
        except console.PageQuit:
            return

    def pprint(self, obj):
        self._printer.pprint(obj)

    def print_obj(self, obj, nl=1):
        self._io.write(str(obj))
        if nl:
            self._io.write("\n")
        self._io.flush()

    def print_list(self, clist, indent=0):
        if clist:
            width = self._io.columns - 9
            indent = min(max(indent, 0), width)
            ps = " " * indent
            try:
                for c in clist[:-1]:
                    cs = "%s, " % (c,)
                    if len(ps) + len(cs) > width:
                        self.print_obj(ps)
                        ps = "%s%s" % (" " * indent, cs)
                    else:
                        ps += cs
                self.print_obj("{}{}".format(ps, clist[-1]))
            except console.PageQuit:
                pass

    def write(self, text):
        try:
            self._io.write(text)
        except console.PageQuit:
            return

    def printf(self, text):
        "Print text run through the expansion formatter."
        self.print(self.prompt_format(text))

    def error(self, text):
        self.printf("%r{}%N".format(text))

    def warning(self, text):
        self.printf("%Y{}%N".format(text))

    # user input
    def _get_prompt(self, name, prompt=None):
        return self._input_prompt_format(prompt or self._env[name])

    def _input_prompt_format(self, ps):
        self._fsm.process_string(ps)
        return self._getarg()

    def user_input(self, prompt=None):
        return self._io.input(self._get_prompt("PS1", prompt))

    def more_user_input(self):
        return self._io.input(self._get_prompt("PS2"))

    def choose(self, somelist, defidx=0, prompt=None):
        return simpleui.choose(somelist,
                               defidx,
                               self._get_prompt("PS3", prompt),
                               input=self._io.input,
                               error=self.error)

    def choose_value(self, somemap, default=None, prompt=None):
        return simpleui.choose_value(somemap,
                                     default,
                                     self._get_prompt("PS3", prompt),
                                     input=self._io.input,
                                     error=self.error)

    def choose_key(self, somemap, default=None, prompt=None):
        return simpleui.choose_key(somemap,
                                   default,
                                   self._get_prompt("PS3", prompt),
                                   input=self._io.input,
                                   error=self.error)

    def choose_multiple(self, somelist, chosen=None, prompt=None):
        return simpleui.choose_multiple(somelist,
                                        chosen,
                                        self._get_prompt("PS3", prompt),
                                        input=self._io.input,
                                        error=self.error)

    def choose_multiple_from_map(self, somemap, chosen=None, prompt=None):
        return simpleui.choose_multiple_from_map(somemap,
                                                 chosen,
                                                 self._get_prompt("PS3", prompt),  # noqa
                                                 input=self._io.input,
                                                 error=self.error)

    def get_text(self, msg=None):
        return simpleui.get_text(self._get_prompt("PS4"), msg,
                                 input=self._io.input)

    def get_value(self, prompt, default=None):
        return simpleui.get_input(self.prompt_format(prompt), default,
                                  self._io.input)

    def edit_text(self, text, prompt=None):
        return simpleui.edit_text(text, self._get_prompt("PS4", prompt))

    def get_int(self, prompt="", default=None):
        return simpleui.get_int(prompt, default, input=self._io.input,
                                error=self.error)

    def get_float(self, prompt="", default=None):
        return simpleui.get_float(prompt, default, input=self._io.input,
                                  error=self.error)

    def get_bool(self, prompt="", default=None):
        return simpleui.get_bool(prompt, default,
                                 input=self._io.input,
                                 error=self.error)

    def yes_no(self, prompt, default=True):
        while 1:
            yesno = simpleui.get_input(self.prompt_format(prompt),
                                       "Y" if default else "N",
                                       self._io.input)
            yesno = yesno.upper()
            if yesno.startswith("Y"):
                return True
            elif yesno.startswith("N"):
                return False
            else:
                self.print("Please enter yes or no.")

    def _format_doc(self, s, color):
        i = s.find("\n")
        if i > 0:
            return (color + s[:i] +
                    self._theme.NORMAL + textwrap.indent(textwrap.dedent(self.prompt_format(s[i:])), "  ") + "\n")
        else:
            return color + s + self._theme.NORMAL + "\n"

    def print_doc(self, doc):
        self.print(self._format_doc(doc, self._theme.help_text))

    def prompt_format(self, ps):
        "Expand percent-exansions in a string and return the result."
        self._ffsm.process_string(ps)
        if self._ffsm.arg:
            arg = self._ffsm.arg
            self._ffsm.arg = ''
            return arg
        else:
            return None

    def format_wrap(self, obj, formatstring):
        return FormatWrapper(obj, self, formatstring)

    def register_expansion(self, key, func):
        """Register a percent-expansion function.
        The function must take one argument, and return a string. The argument is
        the character expanded on.
        """
        key = str(key)[0]
        if key not in self._PROMPT_EXPANSIONS:
            self._PROMPT_EXPANSIONS[key] = func
            self._FORMAT_EXPANSIONS[key] = func
        else:
            raise ValueError("expansion key !r{} already exists.".format(key))

    def unregister_expansion(self, key):
        key = str(key)[0]
        try:
            del self._PROMPT_EXPANSIONS[key]
            del self._FORMAT_EXPANSIONS[key]
        except KeyError:
            pass

    # FSM for prompt expansion
    def _initfsm(self):
        # maps percent-expansion items to some value.
        theme = self._theme
        # Used in prompt strings given to readline library.
        self._PROMPT_EXPANSIONS = {
            "I": PROMPT_START_IGNORE + theme.BRIGHT + PROMPT_END_IGNORE,
            "N": PROMPT_START_IGNORE + theme.NORMAL + PROMPT_END_IGNORE,
            "D": PROMPT_START_IGNORE + theme.DEFAULT + PROMPT_END_IGNORE,
            "R": PROMPT_START_IGNORE + theme.BRIGHTRED + PROMPT_END_IGNORE,
            "G": PROMPT_START_IGNORE + theme.BRIGHTGREEN + PROMPT_END_IGNORE,
            "Y": PROMPT_START_IGNORE + theme.BRIGHTYELLOW + PROMPT_END_IGNORE,
            "B": PROMPT_START_IGNORE + theme.BRIGHTBLUE + PROMPT_END_IGNORE,
            "M": PROMPT_START_IGNORE + theme.BRIGHTMAGENTA + PROMPT_END_IGNORE,
            "C": PROMPT_START_IGNORE + theme.BRIGHTCYAN + PROMPT_END_IGNORE,
            "W": PROMPT_START_IGNORE + theme.BRIGHTWHITE + PROMPT_END_IGNORE,
            "r": PROMPT_START_IGNORE + theme.RED + PROMPT_END_IGNORE,
            "g": PROMPT_START_IGNORE + theme.GREEN + PROMPT_END_IGNORE,
            "y": PROMPT_START_IGNORE + theme.YELLOW + PROMPT_END_IGNORE,
            "b": PROMPT_START_IGNORE + theme.BLUE + PROMPT_END_IGNORE,
            "m": PROMPT_START_IGNORE + theme.MAGENTA + PROMPT_END_IGNORE,
            "c": PROMPT_START_IGNORE + theme.CYAN + PROMPT_END_IGNORE,
            "w": PROMPT_START_IGNORE + theme.WHITE + PROMPT_END_IGNORE,
            "n": "\n",
            "l": self._tty,
            "h": self._hostname,
            "u": self._username,
            "$": self._priv,
            "d": self._cwd,
            "L": self._shlvl,
            "t": self._time,
            "T": self._date,
        }

        self._FORMAT_EXPANSIONS = {
            "I": theme.BRIGHT,
            "N": theme.NORMAL,
            "D": theme.DEFAULT,
            "R": theme.BRIGHTRED,
            "G": theme.BRIGHTGREEN,
            "Y": theme.BRIGHTYELLOW,
            "B": theme.BRIGHTBLUE,
            "M": theme.BRIGHTMAGENTA,
            "C": theme.BRIGHTCYAN,
            "W": theme.BRIGHTWHITE,
            "r": theme.RED,
            "g": theme.GREEN,
            "y": theme.YELLOW,
            "b": theme.BLUE,
            "m": theme.MAGENTA,
            "c": theme.CYAN,
            "w": theme.WHITE,
            "n": "\n",
            "l": self._tty,
            "h": self._hostname,
            "u": self._username,
            "$": self._priv,
            "d": self._cwd,
            "L": self._shlvl,
            "t": self._time,
            "T": self._date,
        }

        fp = FSM(0)
        self._fsmstates(fp)
        self._fsm = fp

        ff = FSM(0)
        self._fsmstates(ff)
        self._ffsm = ff


    def _fsmstates(self, fsm):
        fsm.add_default_transition(self._error, 0)
        # add text to args
        fsm.add_transition(ANY, 0, self._addtext, 0)
        # percent escapes
        fsm.add_transition("%", 0, None, 1)
        fsm.add_transition("%", 1, self._addtext, 0)
        fsm.add_transition("{", 1, self._startvar, 2)
        fsm.add_transition("}", 2, self._endvar, 0)
        fsm.add_transition("[", 1, None, 3)
        fsm.add_transition("F", 3, self._startfg, 4)
        fsm.add_transition("B", 3, self._startbg, 5)
        fsm.add_transitions("0123456789", 3, self._startfgd, 4)
        fsm.add_transitions("0123456789", 4, self._fgnum, 4)
        fsm.add_transitions("0123456789", 5, self._bgnum, 5)
        fsm.add_transition("]", 4, self._setfg, 0)
        fsm.add_transition("]", 5, self._setbg, 0)
        fsm.add_transition(ANY, 2, self._vartext, 2)
        fsm.add_transition(ANY, 1, self._prompt_expand, 0)
        fsm.arg = ''

    def _startvar(self, c, fsm):
        fsm.varname = ""

    def _vartext(self, c, fsm):
        fsm.varname += c

    def _endvar(self, c, fsm):
        fsm.arg += str(self._env.get(fsm.varname, fsm.varname))

    def _startbg(self, c, fsm):
        fsm.bgcol = ""

    def _startfg(self, c, fsm):
        fsm.fgcol = ""

    def _startfgd(self, c, fsm):
        fsm.fgcol = c

    def _fgnum(self, c, fsm):
        fsm.fgcol += c

    def _bgnum(self, c, fsm):
        fsm.bgcol += c

    def _setfg(self, c, fsm):
        fsm.arg += (PROMPT_START_IGNORE + "\x1b[38;5;" + fsm.fgcol + "m" + PROMPT_END_IGNORE)

    def _setbg(self, c, fsm):
        fsm.arg += (PROMPT_START_IGNORE + "\x1b[48;5;" + fsm.bgcol + "m" + PROMPT_END_IGNORE)

    def _prompt_expand(self, c, fsm):
        return self._expand(c, fsm, self._PROMPT_EXPANSIONS)

    def _format_expand(self, c, fsm):
        return self._expand(c, fsm, self._FORMAT_EXPANSIONS)

    def _expand(self, c, fsm, mapping):
        try:
            arg = self._cache[c]
        except KeyError:
            try:
                arg = mapping[c]
            except KeyError:
                arg = c
            else:
                if callable(arg):
                    arg = str(arg(c))
        fsm.arg += arg

    def _username(self, c):
        un = os.environ.get("USERNAME") or os.environ.get("USER")
        if un:
            self._cache[c] = un
        return un

    def _shlvl(self, c):
        return str(self._env.get("SHLVL", ""))

    def _hostname(self, c):
        hn = os.uname()[1]
        self._cache[c] = hn
        return hn

    def _priv(self, c):
        if os.getuid() == 0:
            arg = "#"
        else:
            arg = ">"
        self._cache[c] = arg
        return arg

    def _tty(self, c):
        n = os.ttyname(self._io.fileno())
        self._cache[c] = n
        return n

    def _cwd(self, c):
        return os.getcwd()

    def _time(self, c):
        return time.strftime("%H:%M:%S", time.localtime())

    def _date(self, c):
        return time.strftime("%m/%d/%Y", time.localtime())

    def _error(self, input_symbol, fsm):
        self._io.errlog(
            'Prompt string error: {}\n{!r}'.format(input_symbol))
        fsm.reset()

    def _addtext(self, c, fsm):
        fsm.arg += c

    def _getarg(self):
        if self._fsm.arg:
            arg = self._fsm.arg
            self._fsm.arg = ''
            return arg
        else:
            return None


class FormatWrapper:
    """Wrap any object with a prompt_format.

    The prompt_format string should have an '%O' component that will be expanded to
    the stringified object given here.
    """
    def __init__(self, obj, ui, prompt_format):
        self.value = obj
        self._ui = ui
        self._format = prompt_format

    def __str__(self):
        self._ui.register_expansion("O", self._str_value)
        try:
            return self._ui.prompt_format(self._format)
        finally:
            self._ui.unregister_expansion("O")

    def _str_value(self, c):
        return str(self.value)

    def __len__(self):
        return len(str(self.value))

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        if type(other) is FormatWrapper:
            return self.value == other.value
        else:
            return self.value == other


ANY = -1

class FSM:

    ANY = ANY

    def __init__(self, initial_state=0):
        self._transitions = {}   # Map (input_symbol, state) to (action, next_state).
        self.default_transition = None
        self.RESET = initial_state
        self.initial_state = self.RESET
        self._reset()

    def _reset(self):
        self.stack = []
        self.current_state = self.initial_state

    def reset(self):
        self._reset()

    def push(self, obj):
        self.stack.append(obj)

    def pop(self):
        self.stack.pop()

    def add_default_transition(self, action, next_state):
        if action == None and next_state == None:
            self.default_transition = None
        else:
            self.default_transition = (action, next_state)

    def add_transition(self, input_symbol, state, action, next_state):
        self._transitions[(input_symbol, state)] = (action, next_state)

    def add_transitions(self, symbols, state, action, next_state):
        for c in symbols:
            self.add_transition(c, state, action, next_state)

    def get_transition(self, input_symbol, state):
        try:
            return self._transitions[(input_symbol, state)]
        except KeyError:
            try:
                return self._transitions[(ANY, state)]
            except KeyError:
                try:
                    return self._transitions[(SREType, state)]
                except KeyError:
                    # no expression matched, so check for default
                    if self.default_transition is not None:
                        return self.default_transition
                    else:
                        raise FSMError('Transition {!r} is undefined.'.format(input_symbol))

    def process(self, input_symbol):
        action, next_state = self.get_transition(input_symbol, self.current_state)
        if action is not None:
            action(input_symbol, self)
        if next_state is not None:
            self.current_state = next_state

    def process_string(self, s):
        for c in s:
            self.process(c)


def get_userinterface(environment=None, theme=None, pagerprompt=None):
    uio = console.ConsoleIO(pagerprompt=pagerprompt)
    theme = theme or ANSITheme()
    ui = UserInterface(uio, environment=environment, theme=theme)
    return ui


if __name__ == "__main__":
    ui = get_userinterface()
    ui.printf("Hello %Gworld!%N")
    inp = ui.user_input("Type something> ")
    ui.print("You typed:", inp)
    inp = ui.user_input("%u@%h > ")
    inp = ui.user_input("%T%t > ")
    inp = ui.user_input("Some %[223]color%N> ")
    inp = ui.user_input("Some %[223]%[B20]yellow back blue%N> ")

    lines = []
    for i in range(200):
        lines.append("{}. Now is the time for all good UI to...".format(i))
    lines.append("\n")
    ui.write("\n".join(lines))

    print(ui.prompt_format("%T %t"))
    print(ui.prompt_format("%Ibright%N"))

    print(ui.prompt_format("%rred%N"))
    print(ui.prompt_format("%ggreen%N"))
    print(ui.prompt_format("%yyellow%N"))
    print(ui.prompt_format("%bblue%N"))
    print(ui.prompt_format("%mmagenta%N"))
    print(ui.prompt_format("%ccyan%N"))
    print(ui.prompt_format("%wwhite%N"))

    print(ui.prompt_format("%Rred%N"))
    print(ui.prompt_format("%Ggreen%N"))
    print(ui.prompt_format("%Yyellow%N"))
    print(ui.prompt_format("%Bblue%N"))
    print(ui.prompt_format("%Mmagenta%N"))
    print(ui.prompt_format("%Ccyan%N"))
    print(ui.prompt_format("%Wwhite%N"))

    print(ui.prompt_format("%Ddefault%N"))
    print(ui.prompt_format("wrapped%ntext"))
    print(ui.prompt_format("%l tty %l"))
    print(ui.prompt_format("%h hostname %h"))
    print(ui.prompt_format("%u username %u"))
    print(ui.prompt_format("%$ priv %$"))
    print(ui.prompt_format("%d cwd %d"))
    print(ui.prompt_format("%L SHLVL %L"))
    print(ui.prompt_format("%{PS4}"))

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
