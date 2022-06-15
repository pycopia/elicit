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
The base command set. Inherit from BaseCommands and add methods. Any method that
has a docstring becomes a command with the same name. The docstring is the help
text, and also defines the command options.
"""

__all__ = ['BaseCommands', 'ObjectCommands']

import textwrap
import functools
import readline
from types import MethodType

from . import exceptions


class BaseCommands:
    """Base class for all commands. Commands are methods with docstrings here.
    """

    def __init__(self, ui, aliases=None, prompt="> "):
        self._ui = ui
        self._environ = ui.environ
        self._aliases = aliases or {}
        self._environ.setdefault("PS1", str(prompt))

    def clone(self, cliclass=None, theme=None):
        if cliclass is None:
            cliclass = self.__class__
        newui = self._ui.clone(theme)
        return cliclass(newui, aliases=self._aliases)

    @classmethod
    def clone_from(cls, other):
        newui = other._ui.clone()
        return cls(newui, aliases=other._aliases)

    def _get_namespace(self):
        return globals()

    def finalize(self):
        return NotImplemented

    def default_command(self, arguments):
        """Called when typed command wasn't found."""
        argv = arguments["argv"]
        self._ui.error("unknown command: {!r}".format(argv[0]))
        return 2

    def printf(self, arguments):
        """Print the arguments formatted.

        Format string has Python format syntax ({} style
        expansions) combined with CLI-style expansions.

        usage:
            printf <format> <args>...

        example:
            printf "This is %r{}%N\\n" red
        """
        fmt = arguments["<format>"]
        args, kwargs = evaluate_arguments(arguments["<args>"],
                                          self._get_namespace())
        self._ui.printf(fmt.format(*args, **kwargs))

    def exit(self, arguments):
        """Exits this command interpreter instance."""
        raise exceptions.CommandQuit("exit invoked")

    def printenv(self, arguments):
        """Shows the CLI environment that processes and commands will have.

        Usage:
            printenv [<name>...]
        """
        names = arguments["<name>"]
        if not names:
            names = list(self._environ.keys())
            names.sort()
            ms = functools.reduce(max, map(len, names))
            for name in names:
                value = self._environ[name]
                if not self._ui.write(
                        "{:{maxsize}s} = {}\n".format(
                        name, repr(value), maxsize=ms)):
                    break
        else:
            s = []
            for name in names:
                try:
                    s.append("{} = {}\n".format(name, repr(self._environ[name])))
                except KeyError:
                    s.append("'{}' not in environment.\n".format(name))
            self._ui.write("".join(s))

    def history(self, arguments):
        """Display the current readline history buffer.

        Usage:
            history [<index>]
        """
        index = arguments["<index>"]
        if index:
            idx = int(index)
            self._ui.print(readline.get_history_item(idx))
        else:
            for i in range(readline.get_current_history_length()):
                self._ui.print(readline.get_history_item(i))

    def export(self, arguments):
        """Sets environment variable that new processes will inherit.

        export NAME=VAL
        """
        argv = arguments["argv"]
        for arg in argv[1:]:
            try:
                self._environ.export(arg)
            except Exception as exc:  # noqa
                self._ui.print("** could not set value: (%s)" % (exc,))

    def unset(self, arguments):
        """Unsets the environment variable.

        Usage:
            unset <envar>
        """
        try:
            del self._environ[arguments["<envar>"]]
        except KeyError:
            self._ui.warning("No such environment variable.")
            return 1

    def setenv(self, arguments):
        """Sets the environment variable NAME to VALUE, like C shell.

        Usage:
            setenv NAME VALUE
        """
        self._environ[arguments["NAME"]] = arguments["VALUE"]
        return self._environ["_"]

    def echo(self, arguments):
        """Echoes arguments back.

        Usage:
            echo [-n] <words>...
        """
        self._ui.printf(" ".join(arguments["<words>"]))
        if not arguments["-n"]:
            self._ui.write("\n")
        return self._environ["_"]

    def help(self, arguments):
        """Print help text on command given, or all commands.

        Usage:
            help [<commandname>...]
        """
        args = arguments["<commandname>"]
        if not args:
            for name in get_command_list(self):
                doc = getattr(self, name).__doc__
                firstline = doc.split("\n")[0].strip()
                self._ui.printf("%W{}%N {}\n".format(name, firstline))
            return
        for name in args:
            try:
                doc = getattr(self, name).__doc__
            except AttributeError:
                self._ui.print("No command named {!r} found.".format(name))
                continue
            self._ui.printf("\n%W{}%N\n".format(name))
            self._ui.write(textwrap.dedent(doc))
            self._ui.write("\n")

    def alias(self, arguments):
        """Manage aliases.

        With no argument prints the current set of aliases. With an argument of
        the form `myalias=somecommand`, sets a new alias.

        Usage:
            alias [<newalias>]

        Where a <newalias> looks like `newname=othercommand`.
        """
        argv = arguments["argv"][:]
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
        except Exception as exc:  # noqa
            self._ui.error("{}: {}".format(exc.__name__, exc))
            self._ui.print("alias: Could not set alias. Usage: alias name=value")
            return 1

    def unalias(self, arguments):
        """Remove the named alias from the alias list.

        Usage:
            unalias <name>
        """
        try:
            del self._aliases[arguments["<name>"]]
        except (IndexError, KeyError):
            self._ui.print("unalias: {}: not found".format(arguments["<name>"]))


class ObjectCommands(BaseCommands):
    """Commands that wraps an object with methods that commands may call.
    """
    def __init__(self, ui, instance, aliases=None, prompt="> "):
        super().__init__(ui, aliases=aliases, prompt=prompt)
        self.setup(instance, prompt=prompt)

    def setup(self, newinstance, prompt=None):
        if prompt is None:
            prompt = "%Y{}%N> ".format(newinstance.__class__.__name__)
        self._environ["PS1"] = prompt
        self._obj = newinstance

    def clone(self, cliclass=None, theme=None):
        if cliclass is None:
            cliclass = self.__class__
        newui = self._ui.clone(theme)
        return cliclass(newui, self._obj, aliases=self._aliases)

    @classmethod
    def clone_from(cls, other):
        newui = other._ui.clone()
        return cls(newui, other._obj, aliases=other._aliases)

    def _get_namespace(self):
        try:
            ns = vars(self._obj)
        except:  # noqa
            ns = globals()
        return ns

    def ls(self, arguments):
        """List attributes of wrapped object.
        """
        for name in dir(self._obj):
            attr = getattr(self._obj, name)
            self._ui.print(name, ":", repr(attr))

    def call(self, arguments):
        """Call a method on the wrapped object.

        Usage:
            call <methodname> [<args>...]
        """
        name = arguments["<methodname>"]
        args, kwargs = evaluate_arguments(arguments["<args>"],
                                          self._get_namespace())
        meth = getattr(self._obj, name)
        r = meth(*args, **kwargs)
        self._ui.print(repr(r))
        return r


def evaluate_arguments(argv, namespace=None):
    """convert a list of string arguments (with possible keyword=arg pairs) to
    the most likely objects."""
    args = []
    kwargs = {}
    if namespace:
        assert isinstance(namespace, dict), "namespace must be dict"
    else:
        namespace = globals()
    for argv_arg in argv:
        if argv_arg.find("=") > 0:
            kw, kwarg = argv_arg.split("=", 1)
            kwargs[kw.strip()] = _convert(kwarg, namespace)
        else:
            args.append(_convert(argv_arg, namespace))
    return tuple(args), kwargs


def get_command_list(commands):
    hashfilter = {}
    for name in filter(functools.partial(_command_filt, commands), dir(commands)):
        # this filters out aliased names (same function id)
        meth = getattr(commands, name)
        hashfilter[id(meth.__func__)] = meth.__func__.__name__
    command_list = list(hashfilter.values())
    command_list.sort()
    return command_list


def _convert(val, namespace):
    try:
        return eval(val, globals(), namespace)
    except:  # noqa
        return val


def _command_filt(cmd, objname):
    if objname.startswith("_"):
        return 0
    obj = getattr(cmd, objname)
    if type(obj) is MethodType and obj.__doc__:
        return 1
    else:
        return 0

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
