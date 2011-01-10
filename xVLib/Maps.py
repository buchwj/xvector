# xVector Engine Core Library
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
Contains classes that represent maps and parts of maps.
"""

import struct
from xVLib import Heap, General, BinaryStructs

#
# MAPS
#
# The map file format is a custom binary format managed
# using Python's struct.pack()/unpack() API.  Each map
# file begins with the "magic number" that identifies
# the file as an xVector map file; it is immediately followed
# by a 4-byte integer that indicates the version of map
# file in use.  The remainder of the file varies with
# the format version.
#
# Detailed descriptions of the map file formats are stored
# in the documentation.  Check docs/mapfile for the complete
# set of map format documentation.
#


# Some constants related to map files
CURRENT_MAP_VERSION = 1
"""Latest version identifier of the map file format."""

MAP_MAGIC = 0xB0501
"""\"Magic\" number that appears at the beginning of every map file."""

TILE_WIDTH = 32
"""Width, in pixels, of a single tile."""

TILE_HEIGHT = 32
"""Height, in pixels, of a single tile."""


# Internal flags used by the map files
FLAG_TILE_BLOCKED = 1
"""XOR flag set at the tile level when a tile is blocked."""

FLAG_LAYER_ANIMATED = 1
"""XOR flag set at the layer level when a layer is an animation."""

FLAG_CONTENT_STRIPPED = 1
"""XOR flag set in the header when the map has been stripped down."""


class MapError(Exception): pass
"""Raised when an error related to a map file operation occurs."""


class Tile(object):
    """
    Represents a single tile in a map.
    """

    def __init__(self, **kwargs):
        """
        Creates a new tile with the given layers.  A value of -1 for any layer
        indicates an empty layer.
        
        @keyword blocked: If C{True}, this tile is impassable.
        """
        # Create empty heaps of layers.
        self.layers_negative = Heap.Heap()
        """A heap of the negative layers sorted by their depths."""
        
        self.layers_positive = Heap.Heap()
        """A heap of the positive layers sorted by their depths."""

        # Now check the flags.
        self.blocked = False
        """If C{True}, signals that this tile is impassable."""
        
        if "blocked" in kwargs:
            self.blocked = kwargs["blocked"]
    
    def Serialize(self, fileobj, x, y):
        """
        Outputs a tile to a file using the latest mapfile version.
        
        @type fileobj: file
        @param fileobj: A file object with write capability to output to
        
        @type x: integer
        @param x: X coordinate of this tile
        
        @type y: integer
        @param y: Y coordinate of this tile
        """
        pass    # TODO: Implement
    
    def Deserialize(self, fileobj, x, y, formatver=CURRENT_MAP_VERSION):
        """
        Reads in a tile from a file using the appropriate mapfile version.
        
        @type fileobj: file
        @param fileobj: A file object with read capability to read from
        
        @type x: integer
        @param x: X coordinate of this tile
        
        @type y: integer
        @param y: Y coordinate of this tile
        
        @type formatver: integer
        @param formatver: Map file format version to parse the file as
        
        @return: A handle to this object.  This allows you to make calls
        such as C{Tile().Deserialize(...)} to create an object and read it
        in from a file in a single line of code.
        """
        return self    # TODO: Implement


class Layer(object):
    """
    A single graphical layer of a tile.  These are stored in the tile as an
    ordered set which can be iterated over; a lower value is drawn earlier,
    sprites and items are drawn at 0, and a higher value is drawn later.
    """

    def __init__(self, depth=-1, id=0, **kwargs):
        """
        Creates a layer and optionally sets the properties.

        @type depth: integer
        @param depth: Z position of the layer (less is lower)

        @type id: integer
        @param id: ID number of the content (eg. sprite id, etc.)

        @keyword animated: If C{True}, this layer contains an animation rather
        than a sprite
        """
        # set up some variables
        if depth == 0:
            raise MapError("0 is an invalid layer position")

        self.depth = depth
        """Z position of the layer.  A greater value is higher."""

        self.content_id = id
        """
        ID of whatever this layer corresponds to.  What this layer corresponds
        to is determined by the various flags that are set on the sprite
        (eg. animated).
        """

        self.animated = False
        """Whether this layer is an animated layer."""

        # check the flags
        if "animated" in kwargs:
            self.animated = kwargs["animated"]
    
    def __cmp__(self, other):
        """
        Compares this layer's depth to another value.
        """
        if hasattr(other, "depth"):
            # Other comparison object has depth, compare that
            if self.depth < other.depth: return -1
            elif self.depth == other.depth: return 0
            else: return 1
        else:
            # Other object does not have depth, fall back on __cmp__
            if self.depth < other: return -1
            elif self.depth == other: return 0
            else: return 1
    
    def Serialize(self, fileobj):
        """
        Outputs this layer to a file using the latest mapfile format version.
        
        @type fileobj: file
        @param fileobj: A file object with write capability to output the layer to
        """
        pass    # TODO: Implement
    
    def Deserialize(self, fileobj, formatver=CURRENT_MAP_VERSION):
        """
        Reads in this layer from a file using the given mapfile format version.
        
        @type fileobj: file
        @param fileobj: A file object with read capability to read the layer from
        
        @type formatver: integer
        @param formatver: Map file format version to parse the file as
        
        @return: A handle to this object.  This allows you to make calls
        such as C{Layer().Deserialize(...)} to create an object and read it
        in from a file in a single line of code.
        """
        return self    # TODO: Implement


# And here we have some lovely structures for the map file format!

STRUCT_MHEADER = struct.Struct('<II')
"""
Primary header of the map file.

THIS DOES NOT CHANGE WITH VERSION.  DO NOT MODIFY.
 * I, 0 - Magic number (constant, 0xB0501)
 * I, 1 - Map Format Version ID
"""

SZ_MHEADER = STRUCT_MHEADER.size
"""Size in bytes of the primary header of the map file."""

LATEST_STRUCT_TILE = struct.Struct('<II')
"""
Latest version of the tile structure of the map file.

 * I, 0 - Flags
 * I, 1 - Number of layers
"""

LATEST_SZ_TILE = LATEST_STRUCT_TILE.size
"""Size of the latest version of the tile structure of the map file."""

# Individual layer structures!
#   i - Position
#   I - flags
#   I - sprite ID
LATEST_STRUCT_LAYER = struct.Struct('<iII')
LATEST_SZ_LAYER = LATEST_STRUCT_LAYER.size

class BaseMap(object):
    """
    Represents a map within the game as a matrix of
    TileModels, as well as some assorted header info.
    This is essentially a client map in that it contains
    none of the server-specific data.
    """

    def __init__(self):
        """
        Creates an empty map with no size.
        """
        # predefine some variables
        self.header = MapHeader()
        """Main header of the map file."""

        self.tiles = {}
        """
        The collection of tile objects that forms the map.

        The structure of this collection is a dict which maps integer
        keys (the x-coordinates of the tiles) to another dict.  This
        second dict maps integer keys (the y-coordinates of the tiles)
        to the actual tile objects.  This allows individual tiles
        to be referred to by their coordinates as C{tiles[x][y]}.
        """

        self.version = CURRENT_MAP_VERSION
        """
        The mapfile format version this was loaded from.

        Note that this does not affect which format version the map
        will be saved as; map files are always saved as the latest
        version of the map file format.
        """

    def LoadMapFromFile(self, filepath):
        """
        Loads the map with the given filepath.

        @type filepath: string
        @param filepath: Filepath of the map file to be loaded
        """
        # open the map file
        try:
            mapfile = open(filepath, "rb")
            self.LoadFromOpenFile(mapfile)
        except IOError as err:
            # an error occurred while handling a file
            raise MapError("IOError: " + str(err))
        except MapError as err:
            # let it slip through to higher-up handlers
            pass
        except Exception as err:
            # an unexpected error occurred
            raise MapError("UNEXPECTED ERROR: " + str(err))

    def LoadFromOpenFile(self, fileobj):
        """
        Loads the map from an already-opened file object.

        @type fileobj: file
        @param fileobj: an open file object that contains the map
        """
        buf = fileobj.read(SZ_MHEADER)
        magic, formatver = STRUCT_MHEADER.unpack(buf)
        if magic != MAP_MAGIC:
            # not a valid map file
            raise MapError("map " + file.name + " is not valid (magic).")

        # load the rest by the correct version
        self._Load_Internal(fileobj, formatver)

    def _Load_Latest_Old(self, mapfile, serial_ver):
        """
        Loads the latest format of the map file from the specified
        file object.
        
        Assumes that the serial version info has already been read.
        As usual, the file format documentation is in the docs folder.
        
        @deprecated: Being refactored into another method.
        """
        # first up is the header.

        # prep the tile matrix
        for x in range(self.width):
            self.tiles[x] = {}

        # now we read in each tile
        for i in range(self.width * self.height):
            # break the index down into coordinates
            x = i % self.width
            y = i // self.width
            
            # read in the tile (WEEP IN TERROR AT THIS CODE)
            buf = mapfile.read(LATEST_SZ_TILE)
            tile_tuple = LATEST_STRUCT_TILE.unpack(buf)
            flags, layercount = tile_tuple
            
            blocked = False
            if flags & FLAG_TILE_BLOCKED: blocked = True
            curtile = Tile(blocked=blocked)
            self.tiles[x][y] = curtile
            for seq in range(layercount):
                # read in the layer
                buf = mapfile.read(LATEST_SZ_LAYER)
                depth, lflags, lid = LATEST_STRUCT_LAYER.unpack(buf)
                if depth == 0:
                    # invalid depth
                    msg = "layer at (%d,%d) has depth 0, ignoring" % (x,y)
                    General.Warn(msg)
                    continue
                animated = False
                if lflags & FLAG_LAYER_ANIMATED: animated = True
                this_layer = Layer(depth, lid, animated=animated)
                if depth < 0:
                    curtile.layers_negative.push(this_layer)
                else:
                    curtile.layers_positive.push(this_layer)
    
    def _Load_Internal(self, fileobj, formatver=CURRENT_MAP_VERSION):
        """
        Loads the latest format of the map file from the specified
        file object.
        
        Assumes that the serial version info has already been read.
        As usual, the file format documentation is in the docs folder.
        """
        # first up is the header.
        self.header.Deserialize()

        # prep the tile matrix
        for x in range(self.width):
            self.tiles[x] = {}

        # now we read in each tile
        for i in range(self.width * self.height):
            # break the index down into coordinates
            x = i % self.width
            y = i // self.width
            
            # read in the tile
            tileobj = Tile().Deserialize(fileobj, x, y, formatver)
    
    def SaveMapToFile(self, filepath):
        """
        Saves the map to the given filepath.
        
        You should be expecting this method to raise some sort of I/O related
        error; it is your responsibility to handle these errors.
        
        @type filepath: string
        @param filepath: filepath to save the map to
        """
        fileobj = open(filepath, "wb")
        self.SaveToOpenFile(fileobj)
        fileobj.close()
    
    def SaveToOpenFile(self, fileobj):
        """
        Writes the map to the file object.
        
        You should be expecting this method to raise some sort of I/O related
        error; it is your responsibility to handle these errors.
        
        
        """
        # write the meta-header
        mheader = STRUCT_MHEADER.pack(MAP_MAGIC, CURRENT_MAP_VERSION)
        fileobj.write(mheader)
        
        # write the header
        self.header.Serialize(fileobj)
        
        # write the tiles
        for tile in self.tiles:
            tile.Serialize(fileobj)


class MapHeader(object):
    """
    The main header of a map file.
    """
    
    def __init__(self):
        """
        Creates a new header with default values.
        """
        self.width = 0
        """Width of the map in tiles."""

        self.height = 0
        """Height of the map in tiles."""

        self.mapname = u""
        """Descriptive, human-readable name of the map."""

        self.northmap = u""
        """Name of the map that lies along the northern border."""

        self.eastmap = u""
        """Name of the map that lies along the eastern border."""

        self.southmap = u""
        """Name of the map that lies along the southern border."""

        self.westmap = u""
        """Name of the map that lies along the western border."""
        
        self.stripped = False
        """If true, the server has removed data from this map."""
    
    def Serialize(self, fileobj):
        """
        Encodes and writes the header to a stream (usually a file).
        
        This will always encode the header as the latest version of
        the map file format.
        
        @type fileobj: C{file}
        @param fileobj: open file object to serialize to
        """
        # nothing too special, just write everything in the right order
        BinaryStructs.SerializeUTF8String(fileobj, self.mapname)
        tmpstr = BinaryStructs.UintStruct.pack(self.width)
        fileobj.write(tmpstr)
        tmpstr = BinaryStructs.UintStruct.pack(self.height)
        fileobj.write(tmpstr)
        BinaryStructs.SerializeUTF8String(fileobj, self.northmap)
        BinaryStructs.SerializeUTF8String(fileobj, self.eastmap)
        BinaryStructs.SerializeUTF8String(fileobj, self.southmap)
        BinaryStructs.SerializeUTF8String(fileobj, self.westmap)
        
        # pack the content flags
        contentFlags = 0
        if self.stripped:
            contentFlags = contentFlags or FLAG_CONTENT_STRIPPED
        tmpstr = BinaryStructs.UintStruct.pack(contentFlags)
        fileobj.write(tmpstr)
    
    def Deserialize(self, fileobj, formatver=CURRENT_MAP_VERSION):
        """
        Reads and decodes the header from a stream (usually a file).
        
        @type fileobj: C{file}
        @param fileobj: File object to read the header from.
        
        @type formatver: integer
        @param formatver: version of the map file format to process
        """
        # which version are we reading from?
        if formatver == CURRENT_MAP_VERSION:
            # latest version of the header format!
            # again, we're just reading everything in the right order
            # first up is the basic file information
            self.mapname = BinaryStructs.DeserializeUTF8String(fileobj)
            self.mapname.strip()
            tmpstr = fileobj.read(BinaryStructs.UintStruct.size)
            self.width = BinaryStructs.UintStruct.unpack(tmpstr)
            tmpstr = fileobj.read(BinaryStructs.UintStruct.size)
            self.height = BinaryStructs.UintStruct.unpack(tmpstr)
            
            # now we read in the links
            self.northmap = BinaryStructs.DeserializeUTF8String(fileobj)
            self.northmap.strip()
            self.eastmap = BinaryStructs.DeserializeUTF8String(fileobj)
            self.eastmap.strip()
            self.southmap = BinaryStructs.DeserializeUTF8String(fileobj)
            self.southmap.strip()
            self.westmap = BinaryStructs.DeserializeUTF8String(fileobj)
            self.westmap.strip()
            
            # and then we read in the content flags...
            contentflags = BinaryStructs.DeserializeUint(fileobj)
            self.stripped = contentflags & FLAG_CONTENT_STRIPPED
            
        else:
            # unrecognized version
            raise MapError("unrecognized format version")


class FullMap(BaseMap):
    """
    The most complete form of the map file.

    These are created directly by the map editor and used by the server.
    Only the BaseMap information, however, is sent to the client; in this
    way we can control how much the client knows.  The more the client knows,
    the easier it is for a hacker to take advantage of the system.
    """
    pass        # for now, there's nothing special about the FullMap
