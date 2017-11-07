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

There are also some simple user-input helpers for selecting from lists.

Includes an enhanced debugger that uses the CLI toolkit for a better debugging
experience.

Some notable features:

* Implicit paged output (like _more_).
* Concise prompt string specification, similar to a shell (percent [%] expansions).
* Colored output formatting and input prompts.
* Support 256 colors.


## Command Lines

Just override the `elicit.ui.BaseCommands` class. Any methods defined with doc
strings become a command that can be called. The command gets an _arguments_
parameter that is a docopt-style pre-parsed dictionary of arguments parsed
according to the *Usage:* line in the doc string.

For example:

```py
from elicit import commands

class BasicCommands(commands.BaseCommands):

    def mycommand(self, arguments):
        """Perform some function.

        Usage:
            mycommand [-o]
        """
        self._ui.print("got arguments:", arguments)
```

This defines a new command, _mycommand_, with a option *-o*.

## Presentations

The `elicit.present` subpackage has some functionality useful for interactive
presentatations using the Python REPL.

Thanks to David Beazley for the inspiration.

## Debugger

An enhanced debugger that uses this CLI toolkit is also provided.

