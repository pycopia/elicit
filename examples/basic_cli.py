#!/usr/bin/env python3

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
Basic *elicit* CLI example.
"""

import sys

from elicit import commands
from elicit import console
from elicit import controller
from elicit import env
from elicit import parser
from elicit import themes
from elicit import ui


class BasicCommands(commands.BaseCommands):

    def mycommand(self, arguments):
        """Perform some function.

        Usage:
            mycommand [-o]
        """
        self._ui.print("got arguments:", arguments)

    def nestedusage(self, arguments):
        """Check nested optional usage.

        Usage:
            nestedusage [<one> [<two>]]
        """
        self._ui.print("got arguments:", arguments)


def basic_cli():
    """Construct a basic, default CLI to play with."""
    # Create some basic parts
    uio = console.ConsoleIO()
    environment = env.Environ.from_system()
    theme = themes.DefaultTheme()
    # Assemble the compound parts
    theui = ui.UserInterface(uio, environment, theme)
    cmd = BasicCommands(theui)
    ctl = controller.CommandController(cmd)
    p = parser.CommandParser(ctl)
    # run the CLI using the parser
    p.interact()


if __name__ == "__main__":
    # main(sys.argv)
    basic_cli()

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
