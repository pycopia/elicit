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
Miscellaneous utility functions.
"""

import os
import glob


def globargv(argv):
    """Expand all arguments in argv, all of glob charaters, environment
    variables, and user shorthand. Return a new list with what can be exanded so
    expanded, and those that can't are added as-is.
    """
    if len(argv) > 1:
        newargv = [argv[0]]
        for rawarg in argv[1:]:
            arg = os.path.expandvars(os.path.expanduser(rawarg))
            gl = glob.has_magic(arg) and glob.glob(arg) or [arg]
            newargv.extend(gl)
        return newargv
    else:
        return argv
