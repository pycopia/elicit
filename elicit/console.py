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
Input/Output objects.
"""

__all__ = ['ConsoleIO']

import sys
import os
import signal
import tty

from . import exceptions


class ConsoleIO:
    """Read and write standard I/O from one object.

    Implicitly pages output if too many lines are printed (like *more*).
    """
    def __init__(self, pagerprompt=None):
        self.set_pagerprompt(pagerprompt)
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.mode = "w"
        self.stderr = sys.stderr.buffer
        self.closed = 0
        self.softspace = 0
        self._writtenlines = 0
        if self.stdout.isatty():  # page only if output is a tty
            self.set_size()
            self._oldhandler = signal.getsignal(signal.SIGWINCH)
            signal.signal(signal.SIGWINCH, self._winch_handler)
            self.write = self.paged_write
            self.writelines = self.paged_writelines
        else:
            self.columns, self.rows = 80, 24
            self.write = self.stdout.write
            self.writelines = self.stdout.writelines
        self.read = self.stdin.read
        self.readline = self.stdin.readline
        self.readlines = self.stdin.readlines
        self.flush = self.stdout.flush

    def set_size(self):
        self.columns, self.rows = os.get_terminal_size()

    def set_pagerprompt(self, pagerprompt):
        self.pagerprompt = pagerprompt or "-- more (press any key to continue) --"
        lpp = len(self.pagerprompt)
        self.prompterase = "\r" + " " * lpp + "\r"

    def _winch_handler(self, sig, st):
        self.set_size()

    def input(self, prompt="> "):
        self._writtenlines = 1  # reset paging when input requested
        return input(prompt)

    def print(self, *args, **kwargs):
        kwargs.pop("file", None)
        print(*args, **kwargs, file=self.stdout)

    def close(self):
        if not self.closed:
            self.stdout = None
            self.stdin = None
            signal.signal(signal.SIGWINCH, self._oldhandler)
            del self.read, self.readlines, self.write
            del self.flush, self.writelines
            del self._oldhandler
            self.closed = 1

    def fileno(self):
        return self.stdin.fileno()

    def isatty(self):
        return self.stdin.isatty() and self.stdout.isatty()

    def error(self, text):
        self.stderr.write(text.encode("latin1") + b"\n")  # 1:1 bytes
        self.stderr.flush()

    def paged_write(self, data):
        written = 0
        ld = len(data)
        rows = self.rows - 2
        needed = rows - self._writtenlines
        i = 0
        while i < ld:
            b = i
            i, lines = self._get_index(data, needed, i)
            written += self.stdout.write(data[b:i])
            self._writtenlines += lines
            if self._writtenlines >= rows:
                c = self._pause()
                if c in "qQ":
                    raise exceptions.PageQuit("User quit output")
                elif c == "\r":
                    rows = needed = 1
                elif c == chr(3):
                    raise KeyboardInterrupt("User exit")
                elif c == chr(4):
                    raise EOFError("User end input")
                else:
                    rows = needed = self.rows - 1
        return written

    def paged_writelines(self, lines):
        for line in lines:
            self.paged_write(line)

    # get the index into the data string that will give you the needed number
    # of lines, also taking into account implicit wrapping.
    def _get_index(self, data, needed, i):
        cols = self.columns
        line = n = 0
        ld = len(data)
        while 1:
            n = data.find("\n", i)
            n = ((n < 0 and ld) or n) + 1
            line += 1 + ((n - i) // cols)
            if line >= needed or n >= ld:
                return n, line
            i = n

    def _pause(self):
        c = ""
        self._writtenlines = 0
        savestate = tty.tcgetattr(self.stdin)
        self.stdout.write("\033[s\n")  # save cursor and start new line
        self.stdout.write(self.pagerprompt)
        self.stdout.flush()
        try:
            tty.setraw(self.stdin)
            while 1:
                try:
                    c = self.stdin.read(1)
                    break
                except InterruptedError:
                    continue
        finally:
            tty.tcsetattr(self.stdin, tty.TCSAFLUSH, savestate)
        self.stdout.write(self.prompterase)
        self.stdout.write("\033[u\033[1A")  # resture cursor and go up 1 line
        return c


if __name__ == "__main__":
    io = ConsoleIO()
    if io.isatty():
        io.write("hello, type something\n")
        io.flush()
        print(io.readline())
        io.print("Test print")
        io.error("An error.\n")

    lines = []
    for i in range(200):
        lines.append("{}. Now is the time for all good men...".format(i))
    lines.append("\n")
    text = "\n".join(lines)
    io.write(text)
    io.write("------\n")
    for i in range(200):
        io.write("{}. Now is the time to write lines...\n".format(i))

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
