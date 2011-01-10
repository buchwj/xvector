# xVector Engine Client
# Copyright (c) 2010 James Buchwald

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
Contains various constants used throughout the client.

This module consists mostly of constants related to client version
information; however, it also contains some configuration variables
that should not (and do not need to be) modified except by developers.
"""

APP_NAME = _("xVector Engine Client")
"""The human-readable name of the application.  Used in title bars, etc."""


VERSION_MAJOR = 0
"""The major version of the client (the part before the dot)."""


VERSION_MINOR = 1
"""The minor version of the client (the number after the dot)."""


VERSION_MOD = 'a1'
"""The modtype of the client (the string after the version number)."""


def GetVersionString():
    """
    Returns the full version of the client as a string.
    """
    return str(VERSION_MAJOR) + '.' + str(VERSION_MINOR) + VERSION_MOD
