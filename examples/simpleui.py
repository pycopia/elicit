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
Use the simple UI elements from a script.

"""

import sys

from elicit import simpleui


def choose1():
    choice = simpleui.choose(["one", "two", "three"])
    print("choice 1 was {}".format(choice))

def choose2():
    print("choice 2:", simpleui.choose(["one", "two", "three", "four"]))

def choose1withprompt():
    print("choice 3:", simpleui.choose(["one", "two", "three", "four"], prompt="Choose ONE "))

def main(argv):
    choose1()
    choose2()
    choose1withprompt()


if __name__ == "__main__":
    main(sys.argv)
