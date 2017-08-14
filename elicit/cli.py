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
import readline
from types import MethodType

from . import exceptions


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
        Print the arguments according to the format, or all arguments if first
        is not a format string. Format string has Python format syntax ({} style
        expansions) combined with CLI-style expansions.  """
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
        raise exceptions.CommandQuit("exit invoked")

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
        except (IndexError, KeyError):
            self._ui.print("unalias: %s: not found" % argv[1])

    def _get_ns(self):
        try:
            name = self._obj.__class__.__name__.split(".")[-1].lower()
        except:
            name = "object"
        return {name: self._obj, "environ": self._environ}


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


def _command_filt(cmd, objname):
    if objname.startswith("_"):
        return 0
    obj = getattr(cmd, objname)
    if type(obj) is MethodType and obj.__doc__:
        return 1
    else:
        return 0


def _get_command_list(commands):
    hashfilter = {}
    for name in filter(functools.partial(_command_filt, commands), dir(commands)):
        # this filters out aliases (same function id)
        meth = getattr(commands, name)
        hashfilter[id(meth.__func__)] = meth.__func__.__name__
    command_list = list(hashfilter.values())
    command_list.sort()
    return command_list

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
