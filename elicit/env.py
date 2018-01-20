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

"""An dictionary that supports environment-style operations.
"""

__all__ = ['Environ']

import os

import re
_var_re = re.compile(r'\$([a-zA-Z0-9_\?]+|\{[^}]*\})')
del re


class Environ(dict):
    """Environ is a dictionary-like object that does automatic variable
    expansion when setting new elements.

    It supports an extra method called 'export' that takes strings of the form
    'name=value' that may be used to set assign variable names.  The 'expand'
    method will return a string with variables expanded from the values
    contained in this object.
    """

    @classmethod
    def from_system(cls, **kwargs):
        """Constructor that returns Environ instance pre-populated with values
        from the process environment.
        """
        env = cls(**kwargs)
        env.inherit()
        return env

    def inherit(self, env=None):
        """Works like the 'update' method, but defaults to updating from the
        system environment (os.environ).
        """
        if env is None:
            env = os.environ
        self.update(env)

    def set(self, name, val):
        self.__setitem__(name, self.expand(str(val)))

    def export(self, nameval):
        """Similar to the _export_ command in the bash shell.

        It assigns the name on the left of the equals sign to the value on the
        right, performing variable expansion if necessary.
        """
        name, val = nameval.split("=", 1)
        self.__setitem__(name, self.expand(str(val)))
        return name

    def __str__(self):
        s = ["%s=%s" % (nv[0], nv[1]) for nv in self.items()]
        s.sort()
        return "\n".join(s)

    def expand(self, value):
        """Pass in a string that might have variable expansion to be performed
        (e.g. a section that has $NAME embedded), and return the expanded
        string.
        """
        i = 0
        while 1:
            m = _var_re.search(value, i)
            if not m:
                return value
            i, j = m.span(0)
            vname = m.group(1)
            if vname[0] == '{':
                vname = vname[1:-1]
            tail = value[j:]
            tv = self.get(vname)
            if tv is not None:  # exand to empty if not found or val is None
                value = value[:i] + str(tv)
            else:
                value = value[:i]
            i = len(value)
            value = value + tail

    def copy(self):
        return Environ(self)

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
