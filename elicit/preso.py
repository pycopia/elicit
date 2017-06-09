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
Python based presentations!

Thanks to Dave Beazley for the inspiration.
"""

from __future__ import generator_stop

import sys


class PresoObject:

    def __init__(self, cls, text):
        self.cls = cls
        self.text = text

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)

    def __repr__(self):
        return self.text


class DisplayHook:

    def __call__(self, obj):
        if obj is not None:
            print(repr(obj))
            setattr(sys.modules["__main__"], "_", obj)


if __name__ == "__main__":
    h = DisplayHook()
    sys.displayhook = h
    dict = PresoObject(dict, '... dict slide text ...')
    tuple = PresoObject(tuple, '... tuple slide text ...')
    set = PresoObject(set, '... set slide text ...')


# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
