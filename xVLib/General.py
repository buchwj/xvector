# xVector Engine Core Library
# Copyright (c) 2010 James Buchwald
# (Except for the code in this file that is borrowed, as noted.)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""
Provides miscellaneous functionality used throughout the engine.
"""

import sys

# First up, we have some decorators.

# We begin with an enhanced "property" decorator courtesy of ActiveState.
# http://code.activestate.com/recipes/410698/
def Property(function):
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probeFunc(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k,locals.get(k)) for k in keys))
            sys.settrace(None)
        return probeFunc
    sys.settrace(probeFunc)
    function()
    return property(**func_locals)


# Some very basic error reporting stuff
def Warn(message):
    final = "[warning] " + message + "\n"
    sys.stderr.write(final)
