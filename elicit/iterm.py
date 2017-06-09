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
Special helpers for iTerm2 on MacOS.
"""

from __future__ import generator_stop

import sys
import base64


def imgcat(imgdata):
    sys.stdout.buffer.write(b'\x1b]1337;File=inline=1:' + base64.b64encode(imgdata) + b'\x07\n')


def divider(img):
    sys.stdout.buffer.write(
        b'\x1b]1337;File=inline=1;width=100%;height=1;preserveAspectRatio=0:' + base64.b64encode(img) + b'\x07')


if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    imgcat(data)
    print("divider:")
    divider(data)

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
