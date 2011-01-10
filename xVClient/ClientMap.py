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
Wrapper around the map classes to make them easier to use client-side.
"""

from xVClient import ClientPaths
from xVLib import Maps

#
# MAPS
#
# The map file format is a custom binary format managed
# using Python's struct.pack()/unpack() API.  Each map
# file begins with the "magic number" that identifies
# the file as a Muon map file; it is immediately followed
# by a 4-byte integer that indicates the version of map
# file in use.  The remainder of the file varies with
# the format version.
#
# Detailed descriptions of the map file formats are stored
# in the documentation.  Check docs/mapfile for the complete
# set of map format documentation.
#

class ClientMap(Maps.BaseMap):
    """
    Extension of the BaseMap class that adds client-specific
    support.  Of course, there isn't any client-specific stuff,
    since the client ALWAYS has the least information (we don't
    want to give them any information about hidden objects, after
    all, that would allow easy creation of a cheat that would reveal
    hidden traps and other goodies), so all this really adds is
    an autoconverter from map name to filepath.
    """

    def __init__(self, app):
        # pass off initialization to the base map class
        super(ClientMap, self).__init__(app)

    def LoadMap(self, name):
        """
        Loads the map with the given name.
        This does NOT query the server for newer versions of the map;
        another class must do this.
        """
        # convert from mapname to filepath
        filepath = ClientPaths.GetMapFile(name + ".map")

        # load the map
        self.LoadMapFromFile(filepath)
