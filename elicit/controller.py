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
Controller component module.
"""


class CommandController:
    def __init__(self, ui, cmd, env):
        self._commands = cmd
        self._completion_scopes = {}
        self._completers = []
        self._command_list = None
        self._ui = ui
        self.environ = env

    # Overrideable exception hook method - do something with command exceptions.
    def except_hook(self, ex, val, tb):
        self._ui.error("{}: {}".format(ex.__name__, val))

    # Override this if your subcommand passes something useful back
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

    def push_completer(self, completer):
        orig = readline.get_completer()
        if orig is not None:
            self._completers.append(orig)
        readline.set_completer(completer)

    def pop_completer(self):
        if self._completers:
            c = self._completers.pop()
            readline.set_completer(c)

    def getarg(self, argv, index, default=None):
        return argv[index] if len(argv) > index else default

    def call(self, argv):
        """Dispatch command method by calling with an argv that has the method
        name as first element.
        """
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
                    self.environ["?"] = int(rv)
                except (ValueError, TypeError, AttributeError):
                    self.environ["?"] = 0
                self.environ["_"] = rv
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

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
