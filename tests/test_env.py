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
Unit tests for elicit.env module.
"""

from elicit import env

import pytest


@pytest.fixture
def anenv():
    return env.Environ.from_system()


def test_from_environ(anenv):
    assert len(anenv.keys()) > 0
    assert len(anenv["HOME"]) > 0

def test_export():
    d = env.Environ()
    d.export("HOME=/home/user")
    assert d["HOME"] == "/home/user"
    d.export("PKGHOME=/opt/pkg")
    assert d["PKGHOME"] == "/opt/pkg"
    d.export("PATH=$HOME/bin")
    assert d["PATH"] == "/home/user/bin"
    d.export("PATH=$PATH:${PKGHOME}/bin")
    path = d.expand("$PATH")
    assert path == "/home/user/bin:/opt/pkg/bin"

def test_symbol():
    d = env.Environ()
    d["?"] = 0
    assert d.expand("$?") == "0"
    assert d["?"] == 0

