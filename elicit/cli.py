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
Provides a standard command line interpreter for programs needing one.
Supports different command contexts, customizable user interface, generic
object CLI's, and other neat stuff.

"""

import sys
import os
import functools
import getopt
import code
from types import MethodType

try:
    import readline  # readline is very, very important to us...
except ImportError:
    readline = None  # ...but try to live without it if it is not available.

from .ui import UserInterface, FSM, ANY


class CLIException(Exception):
    def __init__(self, value=None):
        self.value = value


class CLISyntaxError(CLIException):
    """You may raise this if parsing argv doesn't make sense to you. """


class CommandQuit(CLIException):
    """An exception that is used to signal quiting from a command object. """


class CommandExit(CLIException):
    """An exception that is used to signal exiting from the command object. The
    command is not popped.  """


class NewCommand(CLIException):
    """Used to signal the parser to push a new command object.
    Raise this with an instance of BaseCommands as a value."""


class CommandController:
    def __init__(self, ui, cmd):
        self._commands = cmd
        self._completion_scopes = {}
        self._completers = []
        self._command_list = None
        self._set_userinterface(ui)

    def _set_userinterface(self, ui):
        self._ui = ui
        self._environ = ui._env

    # overrideable exception hook method - do something with command exceptions.
    def except_hook(self, ex, val, tb):
        self._ui.error("{}: {}".format(ex.__name__, val))

    # override this if your subcommand passes something useful back
    # via a parameter to the CommandQuit exception.
    def handle_subcommand(self, value):
        pass

    # completer management methods
    def add_completion_scope(self, name, complist):
        self._completion_scopes[name] = list(complist)

    def get_completion_scope(self, name="commands"):
        return self._completion_scopes.get(name, [])

    def remove_completion_scope(self, name):
        del self._completion_scopes[name]

    def push_completer(self, namespace):
        if readline:
            orig = readline.get_completer()
            if orig is not None:
                self._completers.append(orig)
            readline.set_completer(Completer(namespace).complete)

    def pop_completer(self):
        if readline:
            if self._completers:
                c = self._completers.pop()
                readline.set_completer(c)

    def getarg(self, argv, index, default=None):
        return argv[index] if len(argv) > index else default

    # dispatch commands by calling the instance
    def call(self, argv):
        if not argv or not argv[0] or argv[0].startswith("_"):
            return 2
        argv = self._expand_aliases(argv)
        # special escape characters...
        if argv[0].startswith("!"):  # bang-escape reads pipe
            argv[0] = argv[0][1:]
            argv.insert(0, "pipe")
        elif argv[0].startswith("%"):  # percent-escape spawns pty
            argv[0] = argv[0][1:]
            argv.insert(0, "spawn")
        elif argv[0].startswith("#"):  # A comment
            return 0
        # ok, now fetch the real method...
        try:
            meth = getattr(self._commands, argv[0])
        except AttributeError:
            meth = self._commands.default_command
        # ...and exec it.
        try:
            rv = meth(argv)  # call the method
        except (NewCommand, CommandQuit, CommandExit, KeyboardInterrupt):
            raise  # pass these through to parser
        except CLISyntaxError as err:
            self._ui.printf("%RSyntax error%N: {}".format(str(err.value)))
            self._ui.help_local(meth.__doc__)
        except IndexError:  # may have tried to get non-existent argv value.
            ex, val, tb = sys.exc_info()
            lev = 0
            t = tb
            while t.tb_next is not None:
                t = t.tb_next
                lev += 1
            if lev == 1:  # Happened inside the command method.
                self._ui.printf("%RInsufficient number of arguments.%N")
                self._ui.help_local(meth.__doc__)
            else:         # IndexError from something called by command method.
                self.except_hook(ex, val, tb)
        except getopt.GetoptError as err:
            self._ui.print("option %r: %s" % (err.opt, err.msg))
        except:
            ex, val, tb = sys.exc_info()
            self.except_hook(ex, val, tb)
        else:
            if rv is not None:
                try:
                    self._environ["?"] = int(rv)
                except (ValueError, TypeError, AttributeError):
                    self._environ["?"] = 0
                self._environ["_"] = rv
            return rv

    def _expand_aliases(self, argv):
        seen = {}
        while 1:
            alias = self._commands._aliases.get(argv[0], None)
            if alias:
                if alias[0] in seen:
                    break  # alias loop
                seen[alias[0]] = True
                # do the substitution
                del argv[0]
                rl = alias[:]
                rl.reverse()
                for arg in rl:
                    argv.insert(0, arg)
            else:
                break
        return argv

    def get_commands(self):
        if self._command_list is None:
            self._command_list = _get_command_list(self._commands)
        return self._command_list


def _command_filt(cmd, objname):
    if objname.startswith("_"):
        return 0
    obj = getattr(cmd, objname)
    if type(obj) is MethodType and obj.__doc__:
        return 1
    else:
        return 0


def _get_command_list(cmd):
    hashfilter = {}
    for name in filter(functools.partial(_command_filt, cmd), dir(cmd)):
        # this filters out aliases (same function id)
        meth = getattr(cmd, name)
        hashfilter[id(meth.__func__)] = meth.__func__.__name__
    command_list = list(hashfilter.values())
    command_list.sort()
    return command_list


class BaseCommands:
    """Base class for all commands. Commands are methods with docstrings here.
    """

    def __init__(self, ui, aliases=None, instance=None, prompt="> "):
        self._ui = ui
        self._environ = ui._env
        self._obj = None
        self._aliases = aliases or {}
        self._setup(instance, prompt)

    def _setup(self, obj, prompt):
        self._obj = obj  # an object to call methods on, if needed
        self._environ.setdefault("PS1", str(prompt))

    @staticmethod
    def getopt(argv, shortopts):
        return getopt.getopt(argv[1:], shortopts)

    def clone(self, cliclass=None, theme=None):
        if cliclass is None:
            cliclass = self.__class__
        newui = self._ui.clone(theme)
        return cliclass(newui, aliases=self._aliases, instance=self._obj)

    # override this for default actions
    def default_command(self, argv):
        self._ui.error("unknown command: {!r}".format(argv[0]))
        return 2

    def printf(self, argv):
        """printf [<format>] <args>....
        Print the arguments according to the format,
        or all arguments if first is not a format string. Format string has Python format syntax
        ({} style expansions) combined with Pycopia UI expansions."""
        fmt = argv[1]
        try:
            ns = vars(self._obj)
        except:
            ns = globals()
        args, kwargs = breakout_args(argv[2:], ns)
        self._ui.printf(fmt.format(*args, **kwargs))

    def exit(self, argv):
        """exit
        Exits this command interpreter instance.  """
        raise CommandQuit("exit")

    def printenv(self, argv):
        """printenv [name ...]
        Shows the CLI environment that processes will run with.  """
        if len(argv) == 1:
            names = list(self._environ.keys())
            names.sort()
            ms = functools.reduce(max, map(len, names))
            for name in names:
                value = self._environ[name]
                self._ui.print("{:{maxsize}s} = {}".format(name, repr(value), maxsize=ms))
        else:
            s = []
            for name in argv[1:]:
                try:
                    s.append("{} = {}".format(name, repr(self._environ[name])))
                except KeyError:
                    pass
            self._ui.print("\n".join(s))

    def history(self, argv):
        """history [<index>]
        Display the current readline history buffer."""
        if not readline:
            self._ui.print("The readline library is not available.")
            return
        if len(argv) > 1:
            idx = int(argv[1])
            self._ui.print(readline.get_history_item(idx))
        else:
            for i in range(readline.get_current_history_length()):
                self._ui.print(readline.get_history_item(i))

    def export(self, argv):
        """export NAME=VAL
        Sets environment variable that new processes will inherit.
        """
        for arg in argv[1:]:
            try:
                self._environ.export(arg)
            except:
                ex, val = sys.exc_info()[:2]
                self._ui.print("** could not set value: %s (%s)" % (ex, val))

    def unset(self, argv):
        """unset <envar>
        Unsets the environment variable."""
        try:
            del self._environ[argv[1]]
        except:
            return 1

    def setenv(self, argv):
        """setenv NAME VALUE
        Sets the environment variable NAME to VALUE, like C shell.  """
        if len(argv) < 3:
            self._ui.print(self.setenv.__doc__)
            return
        self._environ[argv[1]] = argv[2]
        return self._environ["_"]

    def echo(self, argv):
        """echo ...
        Echoes arguments back.  """
        self._ui.printf(" ".join(argv[1:]))
        return self._environ["_"]

    def help(self, argv):
        """help [<commandname>]...
        """
        args = argv[1:]
        if not args:
            args = _get_command_list(self)
        for name in args:
            try:
                doc = getattr(self, name).__doc__
            except AttributeError:
                self._ui.print("No command named {!r} found.".format(name))
                continue
            self._ui.print(doc)

    def alias(self, argv):
        """alias [newalias]
        With no argument prints the current set of aliases. With an argument of the
        form alias ..., sets a new alias.  """
        if len(argv) == 1:
            for name, val in self._aliases.items():
                self._ui.print("alias %s='%s'" % (name, " ".join(val)))
            return 0
        elif len(argv) == 2 and '=' not in argv[1]:
            name = argv[1]
            try:
                self._ui.print("%s=%s" % (name, " ".join(self._aliases[name])))
            except KeyError:
                self._ui.print("undefined alias.")
            return 0
        try:  # Flexibly handle different permutations of where the '=' is.
            argv.pop(0)  # discard 'alias'
            name = argv.pop(0)
            if "=" in name:
                name, rh = name.split("=", 1)
                argv.insert(0, rh)
            elif argv[0].startswith("="):
                if len(argv[0]) > 1:  # if argv[1] is '=something'
                    argv[0] = argv[0][1:]
                else:
                    del argv[0]  # remove the '='
            self._aliases[name] = argv
        except:
            ex, val = sys.exc_info()[:2]
            self._ui.error("{}: {}".format(ex.__name__, val))
            self._ui.print("alias: Could not set alias. Usage: alias name=value")
            return 1

    def unalias(self, argv):
        """unalias <alias>
        Remove the named alias from the alias list."""
        if len(argv) < 2:
            self._ui.print(self.unalias.__doc__)
            return
        try:
            del self._aliases[argv[1]]
        except:
            self._ui.print("unalias: %s: not found" % argv[1])

    def _get_ns(self):
        try:
            name = self._obj.__class__.__name__.split(".")[-1].lower()
        except:
            name = "object"
        return {name: self._obj, "environ": self._environ}

    def python(self, argv):
        """python
        Start a Python REPL. The environment will have the wrapped instance available, if supplied.
        """
        ns = self._get_ns()
        console = code.InteractiveConsole(ns)
        console.input = self._ui.user_input
        try:
            saveps1, saveps2 = sys.ps1, sys.ps2
        except AttributeError:
            saveps1, saveps2 = ">>> ", "... "
        if self._obj is not None:
            ps1 = "%GPython%N:{}> ".format(self._obj.__class__.__name__,)
        else:
            ps1 = "%GPython%N> "
        sys.ps1 = self._ui.prompt_format(ps1)
        sys.ps2 = self._ui.prompt_format(" %ymore> %N")
        if readline:
            oc = readline.get_completer()
            readline.set_completer(Completer(ns).complete)
        console.interact("You are now in Python. ^D exits.")
        if readline:
            readline.set_completer(oc)
        sys.ps1, sys.ps2 = saveps1, saveps2


def breakout_args(argv, namespace=None):
    """convert a list of string arguments (with possible keyword=arg pairs) to
    the most likely objects."""
    args = []
    kwargs = {}
    if namespace:
        assert isinstance(namespace, dict), "namespace must be dict"
        pass
    else:
        namespace = locals()
    for argv_arg in argv:
        if argv_arg.find("=") > 0:
            [kw, kwarg] = argv_arg.split("=")
            kwargs[kw.strip()] = _convert(kwarg, namespace)
        else:
            args.append(_convert(argv_arg, namespace))
    return tuple(args), kwargs


def _convert(val, namespace):
    try:
        return eval(val, globals(), namespace)
    except:
        return val


class Completer:
    def __init__(self, namespace):
        assert type(namespace) is dict, "namespace must be a dict type"
        self.namespace = namespace
        self.globalNamespace = Completer.get_globals()
        self.globalNamespace.extend(str(k) for k in namespace.keys())
        self.matches = []

    def complete(self, text, state):
        if state == 0:
            self.matches = []
            if "." in text:
                for name, obj in self.namespace.items():
                    for key in dir(obj):
                        if key.startswith("__"):
                            continue
                        lname = "%s.%s" % (name, key)
                        if lname.startswith(text):
                            self.matches.append(lname)
            else:
                for key in self.globalNamespace:
                    if key.startswith(text):
                        self.matches.append(key)
        try:
            return self.matches[state]
        except IndexError:
            return None

    @staticmethod
    def get_globals():
        import keyword
        try:
            import __builtin__
        except ImportError:
            import builtins as __builtin__
        rv = keyword.kwlist + dir(__builtin__)
        return list(set(rv))  # Remove duplicates

    @staticmethod
    def get_class_members(klass, rv=None):
        if rv is None:
            rv = dir(klass)
        else:
            rv.extend(dir(klass))
        if hasattr(klass, '__bases__'):
            for base in klass.__bases__:
                Completer.get_class_members(base, rv)
        return rv


def _reset_readline():
    if readline:
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set horizontal-scroll-mode on")
        readline.parse_and_bind("set page-completions on")
        readline.set_completer_delims(" ")
        readline.set_history_length(500)


class CommandParser:
    """Reads an IO stream and parses input similar to POSIX shell syntax.
    Calls command methods for each line. Handles readline completer.
    """

    VARCHARS = r'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_?'
    _SPECIAL = {"r": "\r", "n": "\n", "t": "\t", "b": "\b"}

    def __init__(self, controller=None, historyfile=None):
        if historyfile:
            self._historyfile = os.path.expanduser(os.path.expandvars(str(historyfile)))
        else:
            self._historyfile = None
        if readline and self._historyfile:
            try:
                readline.read_history_file(self._historyfile)
            except:
                pass
        self.initialize()
        self.reset(controller)

    def _rl_completer(self, text, state):
        if state == 0:
            curr = readline.get_line_buffer()
            b = readline.get_begidx()
            if b == 0:
                complist = self._controller.get_completion_scope("commands")
            else:  # complete based on scope keyed on previous word
                word = curr[:b].split()[-1]
                complist = self._controller.get_completion_scope(word)
            self._complist = filter(lambda s: s.startswith(text), complist)
        try:
            return self._complist[state]
        except IndexError:
            return None

    def close(self):
        self.reset()

    def __del__(self):
        if readline and self._historyfile:
            try:
                readline.write_history_file(self._historyfile)
            except:
                pass

    def reset(self, newcontroller=None):
        self._cmds = []
        self._controller = None
        self.arg_list = []
        self._buf = ""
        if newcontroller:
            self.push_command(newcontroller)

    def push_command(self, newcontroller):
        lvl = int(newcontroller._environ.setdefault("SHLVL", 0))
        newcontroller._environ["SHLVL"] = lvl+1
        self._cmds.append(newcontroller)
        self._controller = newcontroller  # current command holder
        cmdlist = newcontroller.get_commands()
        newcontroller.add_completion_scope("commands", cmdlist)
        newcontroller.add_completion_scope("help", cmdlist)

    def pop_command(self, returnval=None):
        self._cmds.pop()
        if self._cmds:
            self._controller = self._cmds[-1]
            if returnval is not None:
                self._controller.handle_subcommand(returnval)
        else:
            raise CommandQuit("last command object quit.")

    def parse(self, url):
        import urllib
        fo = urllib.urlopen(url)
        self.parseFile(fo)
        fo.close()

    def parseFile(self, fo):
        data = fo.read(4096)
        while data:
            self.feed(data)
            data = fo.read(4096)

    def interact(self, cmd=None):
        _reset_readline()
        if cmd and isinstance(cmd, BaseCommands):
            self.push_command(cmd)
        if readline:
            oc = readline.get_completer()
            readline.set_completer(self._rl_completer)
        try:
            try:
                while 1:
                    ui = self._controller._ui
                    try:
                        line = ui.user_input()
                        if not line:
                            continue
                        while self.feed(line+"\n"):
                            line = ui.more_user_input()
                    except EOFError:
                        self._controller._ui.print()
                        self.pop_command()
            except (CommandQuit, CommandExit):  # last command does this
                pass
        finally:
            if readline:
                readline.set_completer(oc)
                if self._historyfile:
                    try:
                        readline.write_history_file(self._historyfile)
                    except:
                        pass

    def feed(self, text):
        text = self._buf + text
        i = 0
        for c in text:
            i += 1
            try:
                self._fsm.process(c)
                while self._fsm.stack:
                    self._fsm.process(self._fsm.pop())
            except EOFError:
                self.pop_command()
            except CommandQuit:
                val = sys.exc_info()[1]
                self.pop_command(val.value)
            except NewCommand as cmdex:
                self.push_command(cmdex.value)
        if self._fsm.current_state:  # non-zero, stuff left
            self._buf = text[i:]
        return self._fsm.current_state

    def initialize(self):
        f = FSM(0)
        f.arg = ""
        f.add_default_transition(self._error, 0)
        # normally add text to args
        f.add_transition(ANY, 0, self._addtext, 0)
        f.add_transitions(" \t", 0, self._wordbreak, 0)
        f.add_transitions(";\n", 0, self._doit, 0)
        # slashes
        f.add_transition("\\", 0, None, 1)
        f.add_transition("\\", 3, None, 6)
        f.add_transition(ANY, 1, self._slashescape, 0)
        f.add_transition(ANY, 6, self._slashescape, 3)
        # vars
        f.add_transition("$", 0, self._startvar, 7)
        f.add_transition("{", 7, self._vartext, 9)
        f.add_transitions(self.VARCHARS, 7, self._vartext, 7)
        f.add_transition(ANY, 7, self._endvar, 0)
        f.add_transition("}", 9, self._endvar, 0)
        f.add_transition(ANY, 9, self._vartext, 9)
        # vars in singlequote
        f.add_transition("$", 3, self._startvar, 8)
        f.add_transition("{", 8, self._vartext, 10)
        f.add_transitions(self.VARCHARS, 8, self._vartext, 8)
        f.add_transition(ANY, 8, self._endvar, 3)
        f.add_transition("}", 10, self._endvar, 3)
        f.add_transition(ANY, 10, self._vartext, 10)

        # single quotes quote all
        f.add_transition("'", 0, None, 2)
        f.add_transition("'", 2, self._singlequote, 0)
        f.add_transition(ANY, 2, self._addtext, 2)
        # double quotes allow embedding word breaks and such
        f.add_transition('"', 0, None, 3)
        f.add_transition('"', 3, self._doublequote, 0)
        f.add_transition(ANY, 3, self._addtext, 3)
        # single-quotes withing double quotes
        f.add_transition("'", 3, None, 5)
        f.add_transition("'", 5, self._singlequote, 3)
        f.add_transition(ANY, 5, self._addtext, 5)
        self._fsm = f

    def _startvar(self, c, fsm):
        fsm.varname = c

    def _vartext(self, c, fsm):
        fsm.varname += c

    def _endvar(self, c, fsm):
        if c == "}":
            fsm.varname += c
        else:
            fsm.push(c)
        try:
            val = self._controller._environ.expand(fsm.varname)
        except:
            ex, val, tb = sys.exc_info()
            self._controller._ui.error("Could not expand variable "
                                       "{!r}: {} ({})".format(fsm.varname, ex, val))
        else:
            if val is not None:
                fsm.arg += str(val)

    def _error(self, input_symbol, fsm):
        self._controller._ui.error('Syntax error: {}\n{!r}'.format(input_symbol, fsm.stack))
        fsm.reset()

    def _addtext(self, c, fsm):
        fsm.arg += c

    def _wordbreak(self, c, fsm):
        if fsm.arg:
            self.arg_list.append(fsm.arg)
            fsm.arg = ''

    def _slashescape(self, c, fsm):
        fsm.arg += CommandParser._SPECIAL.get(c, c)

    def _singlequote(self, c, fsm):
        self.arg_list.append(fsm.arg)
        fsm.arg = ''

    def _doublequote(self, c, fsm):
        self.arg_list.append(fsm.arg)
        fsm.arg = ''

    def _doit(self, c, fsm):
        if fsm.arg:
            self.arg_list.append(fsm.arg)
            fsm.arg = ''
        args = self.arg_list
        self.arg_list = []
        self._controller.call(args)


def globargv(argv):
    if len(argv) > 2:
        import glob
        l = []
        map(lambda gl: l.extend(gl),
            map(lambda arg: glob.has_magic(arg) and glob.glob(arg) or [arg], argv[2:]))
        argv = argv[0:2] + l
    return argv[1:]


if __name__ == "__main__":
    from .console import ConsoleIO
    uio = ConsoleIO()
    ui = UserInterface(uio)
    cmd = BaseCommands(ui)
    ctl = CommandController(ui, cmd)
    parser = CommandParser(ctl)
    parser.interact()

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
