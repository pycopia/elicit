#!/usr/bin/python3.6

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
Importing this module sets up the Python interpreter to enter the elicit debugger
on an uncaught exception, rather than exiting.

Example:

    def main(argv):
       # ...
       return 0

    # ...
    if __name__ == "__main__":
        from elicit import autodebug
        sys.exit(main(sys.argv))

Normally, if any exception is not caught it results in a stracktrace being
printed at the terminal and the program ending.

After this import, an interactive debugger prompt will be started instead.

The debugger will be the enhanced debugger from this package. Unless you are
using it on Windows, in which case it will be the stock, pdb, debugger.
"""

import sys

debugger_hook = sys.__excepthook__

if sys.platform == "win32":
    import pdb

    def debugger_hook(exc, value, tb):
        if (not hasattr(sys.stderr, "isatty") or
            not sys.stderr.isatty() or exc in (SyntaxError, IndentationError, KeyboardInterrupt)):
            sys.__excepthook__(exc, value, tb)
        else:
            pdb.post_mortem(tb)
else:
    from elicit import debugger

    def debugger_hook(exc, value, tb):
        if (not hasattr(sys.stderr, "isatty") or
            not sys.stderr.isatty() or exc in (SyntaxError, IndentationError, KeyboardInterrupt)):
            # We don't have a tty-like device, or it was a SyntaxError, so
            # call the default hook.
            sys.__excepthook__(exc, value, tb)
        else:
            debugger.post_mortem(tb, exc, value)

sys.excepthook = debugger_hook

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
