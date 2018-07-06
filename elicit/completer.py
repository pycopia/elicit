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
Completer module.
"""

import keyword
import builtins


class Completer:
    def __init__(self, namespace):
        assert isinstance(namespace, dict), "namespace must be a dict type"
        self.namespace = namespace
        self._globals = get_globals()
        self._globals.extend(str(k) for k in namespace.keys())
        self.matches = []

    def complete(self, text, state):
        if state == 0:
            self.matches = []
            if "." in text:
                for name, obj in self.namespace.items():
                    for key in dir(obj):
                        if key.startswith("__"):
                            continue
                        lname = "%s.%s" % (name, key)
                        if lname.startswith(text):
                            self.matches.append(lname)
            else:
                for key in self._globals:
                    if key.startswith(text):
                        self.matches.append(key)
        try:
            return self.matches[state]
        except IndexError:
            return None


def get_class_members(klass, rv=None):
    if rv is None:
        rv = dir(klass)
    else:
        rv.extend(dir(klass))
    if hasattr(klass, '__bases__'):
        for base in klass.__bases__:
            get_class_members(base, rv)
    return rv


def get_globals():
    rv = keyword.kwlist + dir(builtins)
    return list(set(rv))  # Remove duplicates

# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
