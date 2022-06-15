# python3.7

"""Python REPL mixin class for Command objects.
"""

from __future__ import annotations

import sys
import code
import readline

from elicit import completer


class PythonMixin:

    def _get_ns(self):
        if hasattr(self, "_obj"):
            try:
                name = self._obj.__class__.__name__.split(".")[-1].lower()
            except:  # noqa
                name = "object"
            return {name: self._obj, "environ": self._environ}
        else:
            return globals()

    def python(self, arguments):
        """Enter an interactive interpreter.

        Usage:
            python
        """
        ns = self._get_ns()
        console = code.InteractiveConsole(ns)
        console.raw_input = self._ui.user_input
        try:
            saveps1, saveps2 = sys.ps1, sys.ps2
        except AttributeError:
            saveps1, saveps2 = ">>> ", "... "
        sys.ps1, sys.ps2 = "%GPython%N> ", "more> "
        oc = readline.get_completer()
        readline.set_completer(completer.Completer(ns).complete)
        try:
            console.interact(banner="You are now in Python. ^D exits.",
                             exitmsg="Resuming command shell.")
        finally:
            readline.set_completer(oc)
            sys.ps1, sys.ps2 = saveps1, saveps2
