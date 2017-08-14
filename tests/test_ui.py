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
Test the UI module.
"""

from elicit import console
from elicit import themes
from elicit import env
from elicit import ui

import pytest

def get_userinterface():
    cio = console.ConsoleIO()
    theme = themes.ANSITheme()
    environment = env.Environ.from_system()
    return ui.UserInterface(cio, environment, theme)

@pytest.fixture
def myui():
    return get_userinterface()


@pytest.mark.skip(reason="Interactive test")
def test_ui(myui):
    myui.printf("Hello %Gworld!%N")
    inp = myui.user_input("Type something> ")
    myui.print("You typed:", inp)
    inp = myui.user_input("%u@%h > ")
    inp = myui.user_input("%T%t > ")
    inp = myui.user_input("Some %[223]color%N> ")
    inp = myui.user_input("Some %[223]%[B20]yellow back blue%N> ")

    lines = []
    for i in range(200):
        lines.append("{}. Now is the time for all good UI to...".format(i))
    lines.append("\n")
    myui.write("\n".join(lines))

    print(myui.prompt_format("%T %t"))
    print(myui.prompt_format("%Ibright%N"))

    print(myui.prompt_format("%rred%N"))
    print(myui.prompt_format("%ggreen%N"))
    print(myui.prompt_format("%yyellow%N"))
    print(myui.prompt_format("%bblue%N"))
    print(myui.prompt_format("%mmagenta%N"))
    print(myui.prompt_format("%ccyan%N"))
    print(myui.prompt_format("%wwhite%N"))

    print(myui.prompt_format("%Rred%N"))
    print(myui.prompt_format("%Ggreen%N"))
    print(myui.prompt_format("%Yyellow%N"))
    print(myui.prompt_format("%Bblue%N"))
    print(myui.prompt_format("%Mmagenta%N"))
    print(myui.prompt_format("%Ccyan%N"))
    print(myui.prompt_format("%Wwhite%N"))

    print(myui.prompt_format("%Ddefault%N"))
    print(myui.prompt_format("wrapped%ntext"))
    print(myui.prompt_format("%l tty %l"))
    print(myui.prompt_format("%h hostname %h"))
    print(myui.prompt_format("%u username %u"))
    print(myui.prompt_format("%$ priv %$"))
    print(myui.prompt_format("%d cwd %d"))
    print(myui.prompt_format("%L SHLVL %L"))
    print(myui.prompt_format("%{PS4}"))


if __name__ == "__main__":
    myui = get_userinterface()
    test_ui(myui)
