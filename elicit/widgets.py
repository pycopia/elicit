#!/usr/bin/env python3.5

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
Simple forms and user inputs using curses module.
"""

import sys
import signal
import curses
import curses.ascii
import curses.textpad
import locale
from shutil import get_terminal_size


locale.setlocale(locale.LC_ALL, '')
LANG, ENCODING = locale.getlocale()
COLUMNS = LINES = None


def _reset_size(sig, tr):
    global COLUMNS, LINES
    COLUMNS, LINES = get_terminal_size()


_reset_size(signal.SIGWINCH, None)

signal.signal(signal.SIGWINCH, _reset_size)


def choose(somelist, defidx=0, prompt="choose", lines=LINES, columns=COLUMNS):
    return curses.wrapper(_choose, somelist, defidx, prompt, lines, columns)


def _choose(stdscr, somelist, defidx, prompt, lines, columns):
    oldcur = curses.curs_set(0)
    pad = curses.newpad(len(somelist) + 1, columns - 2)
    for line in somelist:
        pad.addstr(str(line))

    pminrow = defidx  # also somelist index
    pmincol = 0
    sminrow = (lines - 3) // 2
    smincol = 1
    smaxrow = lines - 3
    smaxcol = columns - 2

    topwin = stdscr.subwin(sminrow, columns - 2, 2, 1)

    # top context window
    # sminrow_top = sminrow - 1
    # smaxrow_top = sminrow - 1
    # Build form
    stdscr.clear()
    stdscr.addstr("{} (Press Enter to select)".format(prompt))
    curses.textpad.rectangle(stdscr, 1, 0, lines - 2, columns - 1)
    stdscr.refresh()
    pad.chgat(pminrow, 0, smaxcol - 1, curses.A_REVERSE)
    pad.refresh(pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol)
    J, K = [b'jk'[i] for i in range(2)]
    esc = False
    while 1:
        ch = stdscr.getch()
        if ch in (curses.KEY_DOWN, J):
            pminrow = min(len(somelist) - 1, max(0, pminrow + 1))
        elif ch in (curses.KEY_UP, K):
            pminrow = max(0, min(len(somelist), pminrow - 1))
        elif ch == curses.ascii.NL:
            break
        elif ch == curses.ascii.ESC:
            esc = True
            break

        if pminrow > 0:
            topwin.clear()
#            sminrow_top = sminrow - pminrow + 2
#            pad.noutrefresh(pminrow - sminrow, pmincol,
#                        sminrow_top, smincol,
#                        smaxrow_top, smaxcol)
#            pad.chgat(sminrow_top, 0, smaxcol - 1, curses.A_NORMAL)

        pad.chgat(pminrow + 1, 0, smaxcol - 1, curses.A_NORMAL)
        pad.chgat(pminrow, 0, smaxcol - 1, curses.A_REVERSE)
        pad.noutrefresh(pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol)
        curses.doupdate()

    curses.curs_set(oldcur)
    if esc:
        return None
    else:
        return somelist[pminrow]


def _test(argv):
    with open("/etc/protocols") as fo:
        lines = fo.readlines()

    print(choose(lines, defidx=3, prompt="Pick a service"))


if __name__ == "__main__":
    _test(sys.argv)

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
