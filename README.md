# Elicit

Library for writing console (command oriented) user interfaces. It depends only
on the Python standard library.

The package makes it easy and quick to create an interactive command oriented
tool. The style is similar to embedded systems, such as routers, and POSIX
shells. This is not an alternate Python REPL, such as IPython or bpython. You
can use it to implement a custom command interface for your application that
gets customizable command parsing, custom prompts, help system, and output
paging.

The [docopt](http://docopt.org/) module is built-in, so no additional packages
need to be installed.

Some notable features:

* Commands are defined as class methods.
* Command classes group commands, and can be nested, providing
  context-sensitive commands.
* Implicit paged output (like _more_).
* Command completion.
* Concise prompt string specification, similar to a shell (percent [%] expansions).
* Colored output formatting and input prompts.
* Built-in options parsing.
* Built-in *help*, that uses the command-method docstring.
* Wrap any object to interact with it.
* Modular design. Any component can be subclassed and enhanced.

Also includes some bonus modules:

* presentation - helper module for using Python in interactive presentations.
* debugger - enhanced debugger that uses the framework for the user interface.


## Command Lines

Just override the `elicit.ui.BaseCommands` class. Any methods defined with doc
strings become a command that can be called. The command gets an _arguments_
parameter that is a docopt-style pre-parsed dictionary of arguments parsed
according to the *Usage:* line in the doc string.

Here's a working example:

```py
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

    # Add as many more commands as you need.


def basic_cli():
    # Create The IO module.
    uio = console.ConsoleIO()

    environment = env.Environ.from_system()
    theme = themes.DefaultTheme()  # The built-in colored theme.

    # Assemble the IO in user interface.
    theui = ui.UserInterface(uio, environment, theme)

    # Create the top-level command set, with the user interface.
    cmd = BasicCommands(theui)

    # Add it to a controller, and command parser.
    ctl = controller.CommandController(cmd)
    p = parser.CommandParser(ctl)

    # Run the CLI using the parser.
    p.interact()
```

This defines a new command, _mycommand_, with a singo option *-o*.

## Presentations

The `elicit.present` subpackage has some functionality useful for interactive
presentatations using the Python REPL. Exposes some iTerm features on MacOS.

Thanks to David Beazley for the inspiration.

To invoke interactively, for testing, use:

```sh
python3 -iq -m elicit.present.presentation
```

## Debugger

An enhanced debugger that uses this CLI toolkit is also provided. A tool,
*eldb*, is also provided that you can use instead of *python3* to run a script,
or module, that will enter the debugger if an uncaught exception occurs.

```sh
eldb path/to/script.py
```

or, if you have a package with an *if ... \_\_main\_\_:* section:

```sh
eldb mypackage.mymodule
```

You can also import the `elicit.debugger` module in your code and call the
`post_mortem` function, as with *pdb*.

Some notable features:

* Colorized UI - stacktrace, prompt, etc.
* More informative reports, prompt shows current position in stack.
* Invoke your editor at current point.
* REPL-like evaluator
* Enter sub-REPL if desired.
* Display opcodes.


