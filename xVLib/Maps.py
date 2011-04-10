# -*- coding: utf-8 -*-

# xVector Engine Core Library
# Copyright (c) 2011 James Buchwald

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
from xVLib import Heap, BinaryStructs

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
CurrentMapVersion = 1
"""Latest version identifier of the map file format."""

TileWidth = 32
"""Width, in pixels, of a single tile."""

TileHeight = 32
"""Height, in pixels, of a single tile."""


class MapError(Exception): pass
"""Raised when an error related to a map file operation occurs."""


class FutureFormatException(MapError): pass
"""Raised when a map with an unsupported future map format is loaded."""


class Tile(object):
    """
    Represents a single tile in a map.
    """

    def __init__(self):
        """
        Creates a new tile with the given layers.  A value of -1 for any layer
        indicates an empty layer.
        
        @keyword blocked: If C{True}, this tile is impassable.
        """
        # Create empty heaps of layers.
        self.layers = Heap.Heap()
    
    
    def Serialize(self, fileobj):
        """
        Outputs a tile to a file using the latest mapfile version.
        
        @type fileobj: file
        @param fileobj: An open file object (or compatible stream) for writing
        """
        # first up, the flags (we currently have none)
        flags = 0
        try:
            BinaryStructs.SerializeUint(fileobj, flags)
        except Exception as e:
            raise IOError("error while writing to map file", e)
        
        # now the layer count
        layercount = len(self.layers_negative) + len(self.layers_positive)
        try:
            BinaryStructs.SerializeUint(fileobj, layercount)
        except Exception as e:
            raise IOError("error while writing to map file", e)
        
        # go through the layers and get them all
        while True:
            try:
                # get the lowest remaining layer
                layer = self.layers.pop()
            except:
                # nothing left in the heap
                break
            layer.Serialize(fileobj)
    
    def Deserialize(self, fileobj, formatver=CurrentMapVersion):
        """
        Reads in a tile from a file using the appropriate mapfile version.
        
        @type fileobj: file
        @param fileobj: A file object with read capability to read from
        
        @type formatver: integer
        @param formatver: Map file format version to parse the file as
        
        @return: A handle to this object.  This allows you to make calls
        such as C{Tile().Deserialize(...)} to create an object and read it
        in from a file in a single line of code.
        """
        # do we support this version?
        if formatver == CurrentMapVersion:
            # current version... let's go!
            self._Deserialize_CurrentVer(fileobj)
        elif formatver > CurrentMapVersion:
            # unsupported future version
            msg = "Unsupported future version of the map file format. "
            msg += "Check if a newer version of the program is available."
            raise FutureFormatException(msg)
        return self
    
    def _Deserialize_CurrentVer(self, fileobj):
        """
        Deserializes a tile in the current map file format.
        
        @type fileobj: C{file}
        @param fileobj: File (or compatible stream) to read from.
        """
        # first: the flags
        try:
            flags = BinaryStructs.DeserializeUint(fileobj)
        except:
            raise MapError("invalid/corrupt map file")
        # Of course, we don't have any flags to handle, so... yeah.
        
        # next up, the layers
        try:
            numlayers = BinaryStructs.DeserializeUint(fileobj)
        except:
            raise MapError("invalid/corrupt map file")
        for i in range(numlayers):
            try:
                layer = Layer().Deserialize(fileobj)
            except:
                raise MapError("invalid/corrupt map file")
            self.layers.push(layer)


class Layer(object):
    """
    A single graphical layer of a tile.  These are stored in the tile as an
    ordered set which can be iterated over; a lower value is drawn earlier.
    """
    
    Flag_Blocked = 1
    '''Layer flag set when a layer is blocked/impassable.'''

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
        self.depth = depth
        """Z position of the layer.  A greater value is higher."""

        self.tile_id = id
        """
        ID of the tile drawn for this layer.
        """

        self.blocked = False
        '''True if this layer is blocked/impassable.'''

        # check the flags
        if "blocked" in kwargs:
            self.blocked = kwargs["blocked"]
    
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
        # first, the depth
        try:
            BinaryStructs.SerializeUint(fileobj, self.depth)
        except Exception as e:
            raise IOError("error while writing to map file", e)
        
        # next, the flags
        flags = 0
        if self.blocked:
            flags |= self.Flag_Blocked
        try:
            BinaryStructs.SerializeUint(fileobj, flags)
        except Exception as e:
            raise IOError("error while writing to map file", e)
        
        # finally, the tile
        try:
            BinaryStructs.SerializeUint(fileobj, self.tile_id)
        except Exception as e:
            raise IOError("error while writing to map file", e)
    
    def Deserialize(self, fileobj, formatver=CurrentMapVersion):
        """
        Reads in this layer from a file using the given mapfile format version.
        
        @type fileobj: file
        @param fileobj: An open file object to read the layer from.
        
        @type formatver: integer
        @param formatver: Map file format version to parse the file as
        
        @return: A handle to this object.  This allows you to make calls
        such as C{Layer().Deserialize(...)} to create an object and read it
        in from a file in a single line of code.
        """
        # check the map file version
        if formatver == CurrentMapVersion:
            # latest version... let's go!
            self._Deserialize_CurrentVer(fileobj)
        else:
            # unsupported future version
            msg = "Unsupported future version of the map file format. "
            msg += "Check if a newer version of the program is available."
            raise FutureFormatException(msg)

    def _Deserialize_CurrentVer(self, fileobj):
        """
        Reads a layer from the file using the current map file format.
        
        @type fileobj: C{file} or compatible stream
        @param fileobj: File to read the layer from.
        """
        # first up, read the depth
        try:
            self.depth = BinaryStructs.DeserializeUint(fileobj)
        except:
            raise MapError("invalid/corrupt map file")
        
        # next, read the flags
        try:
            flags = BinaryStructs.DeserializeUint(fileobj)
        except:
            raise MapError("invalid/corrupt map file")
        self.blocked = bool(flags & self.Flag_Blocked)
        
        # finally, read the content
        try:
            self.tile_id = BinaryStructs.DeserializeUint(fileobj)
        except:
            raise MapError("invalid/corrupt map file")


class BaseMap(object):
    """
    Represents a map within the game as a matrix of TileModels, as well as 
    some assorted header info.  This is essentially a client-side map in that 
    it contains none of the server-specific data.
    """

    MetaheaderStruct = struct.Struct('<II')
    """
    Primary header of the map file.
    
    THIS DOES NOT CHANGE WITH VERSION.  DO NOT MODIFY.
     * I, 0 - Magic number (constant, 0xB0501)
     * I, 1 - Map Format Version ID
    """
    
    MagicNumber = 0xB0501
    '''"Magic" number that appears at the beginning of every map file.'''

    def __init__(self, width=1, height=1):
        """
        Creates an empty map with the given dimensions.
        
        @type width: integer
        @param width: Width of the new map.  Must be greater than 0.
        
        @type height: integer
        @param height: Height of the new map.  Must be greater than 0.
        """
        # check the dimensions
        if width <= 0 or height <= 0:
            raise IndexError("map dimensions must be greater than 0")
        
        # predefine some variables
        self.header = MapHeader()
        """Main header of the map file."""
        self.header.width = width
        self.header.height = height

        self.tiles = []
        """
        The collection of tile objects that forms the map.

        The structure of this collection is a dict which maps integer
        keys (the x-coordinates of the tiles) to another dict.  This
        second dict maps integer keys (the y-coordinates of the tiles)
        to the actual tile objects.  This allows individual tiles
        to be referred to by their coordinates as C{tiles[x][y]}.
        """
        
        # prep the tiles
        for x in range(width):
            self.tiles.append([])
            for y in range(height):
                self.tiles[x].append(Tile())

        self.version = CurrentMapVersion
        """
        The mapfile format version this was loaded from.

        Note that this does not affect which format version the map
        will be saved as; map files are always saved as the latest
        version of the map file format.
        """
        
    @property
    def width(self):
        """
        Convenience property that abstracts the width out of the header.
        """
        return self.header.width
    
    @width.setter
    def width(self, width):
        self.header.width = width
    
    @property
    def height(self):
        """
        Convenience property that abstracts the height out of the header.
        """
        return self.header.height
    
    @height.setter
    def height(self, height):
        self.header.height = height
    
    @property
    def northmap(self):
        """
        Convenience property connected to the north-bordered map name.
        This value is actually stored in the header.
        """
        return self.header.northmap
    
    @northmap.setter
    def northmap(self, northmap):
        self.header.northmap = northmap
        
    @property
    def eastmap(self):
        """
        Convenience property connected to the east-bordered map name.
        This value is actually stored in the header.
        """
        return self.header.eastmap
    
    @eastmap.setter
    def eastmap(self, eastmap):
        self.header.eastmap = eastmap
        
    @property
    def southmap(self):
        """
        Convenience property connected to the south-bordered map name.
        This value is actually stored in the header.
        """
        return self.header.southmap
    
    @southmap.setter
    def southmap(self, southmap):
        self.header.southmap = southmap
    
    @property
    def westmap(self):
        """
        Convenience property connected to the west-bordered map name.
        This value is actually stored in the header.
        """
        return self.header.westmap
    
    @westmap.setter
    def westmap(self, westmap):
        self.header.westmap = westmap

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
        buf = fileobj.read(self.MetaheaderStruct.size)
        magic, formatver = self.MetaheaderStruct.unpack(buf)
        if magic != self.MagicNumber:
            # not a valid map file
            raise MapError("map " + file.name + " is not valid (magic).")

        # load the rest by the correct version
        if formatver == CurrentMapVersion:
            self._Load_CurrentVer(fileobj, formatver)
        else:
            # unrecognized future format
            msg = "Unsupported future version of the map file format. "
            msg += "Check if a newer version of the program is available."
            raise FutureFormatException(msg)
    
    def _Load_CurrentVer(self, fileobj, formatver=CurrentMapVersion):
        """
        Loads the latest format of the map file from the specified
        file object.
        
        Assumes that the serial version info has already been read.
        As usual, the file format documentation is in the docs folder.
        """
        # first up is the header.
        self.header.Deserialize(fileobj, formatver)

        # resize the map as needed
        self.Resize(self.header.width, self.header.height)

        # now we read in each tile
        for y in range(self.header.height):
            for x in range(self.header.width):
                self.tiles[x][y] = Tile().Deserialize(fileobj)
    
    def SaveMapToFile(self, filepath):
        """
        Saves the map to the given filepath.
        
        You should be expecting this method to raise some sort of I/O related
        error; it is your responsibility to handle these errors.
        
        @type filepath: string
        @param filepath: Filepath to save the map to
        """
        fileobj = open(filepath, "wb")
        self.SaveToOpenFile(fileobj)
        fileobj.close()
    
    def SaveToOpenFile(self, fileobj):
        """
        Writes the map to the file object.
        
        You should be expecting this method to raise some sort of I/O related
        error; it is your responsibility to handle these errors.
        
        @type fileobj: C{file}
        @param fileobj: An open file object (or compatible stream) to
        write the map to.
        """
        # write the meta-header
        try:
            mheader = self.MetaheaderStruct.pack(self.MagicNumber, CurrentMapVersion)
            fileobj.write(mheader)
        except Exception as e:
            raise IOError("error while writing map file", e)
        
        # write the header
        self.header.Serialize(fileobj)
        
        # write the tiles
        for tileY in range(self.header.height):
            for tileX in range(self.header.width):
                self.tiles[tileX][tileY].Serialize(fileobj)
    
    def Resize(self, width, height):
        """
        Resizes a map to the given dimensions.
        
        @type width: integer
        @param width: New width, in tiles, of the map.
        
        @type height: integer
        @param height: New height, in tiles, of the map.
        """
        # check the width and height
        if width <= 0 or height <= 0:
            # invalid dimensions
            raise IndexError("map dimensions must be greater than 0")
        # are we increasing in width?
        if width > self.header.width:
            # add and fill new X components
            for x in range(self.header.width, width):
                self.tiles[x] = []
                for y in range(self.header.height):
                    # insert a new blank tile
                    self.tiles[x][y] = Tile()
        # if not, then are we decreasing in width?
        elif width < self.header.width:
            # destroy the X components
            for i in range(width, self.header.width):
                del self.tiles[i]
        
        # now check the height - is it increasing?
        if height > self.header.height:
            # add new Y components
            for y in range(self.header.height, height):
                for x in range(width):
                    self.tiles[x][y] = Tile()
        # if not, are we decreasing in height?
        elif height < self.header.height:
            # destroy some Y components
            for y in range(height, self.header.height):
                for x in range(width):
                    del self.tiles[x][y]
        
        # update the dimensions in the header
        self.header.width = width
        self.header.height = height


class MapHeader(object):
    """
    The main header of a map file.
    """
    
    Flag_ContentStripped = 1
    """XOR flag set in the header when the map has been stripped down."""
    
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
        try:
            BinaryStructs.SerializeUTF8String(fileobj, self.mapname)
            tmpstr = BinaryStructs.UintStruct.pack(self.width)
            fileobj.write(tmpstr)
            tmpstr = BinaryStructs.UintStruct.pack(self.height)
            fileobj.write(tmpstr)
            BinaryStructs.SerializeUTF8String(fileobj, self.northmap)
            BinaryStructs.SerializeUTF8String(fileobj, self.eastmap)
            BinaryStructs.SerializeUTF8String(fileobj, self.southmap)
            BinaryStructs.SerializeUTF8String(fileobj, self.westmap)
        except Exception as e:
            raise IOError("error while writing to map file", e)
        
        # pack the content flags
        try:
            contentFlags = 0
            if self.stripped:
                contentFlags = contentFlags | self.Flag_ContentStripped
            tmpstr = BinaryStructs.UintStruct.pack(contentFlags)
            fileobj.write(tmpstr)
        except Exception as e:
            raise IOError("error while writing to map file", e)
    
    def Deserialize(self, fileobj, formatver=CurrentMapVersion):
        """
        Reads and decodes the header from a stream (usually a file).
        
        @type fileobj: C{file}
        @param fileobj: File object to read the header from.
        
        @type formatver: integer
        @param formatver: version of the map file format to process
        """
        # which version are we reading from?
        if formatver == CurrentMapVersion:
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
            self.stripped = contentflags & self.Flag_ContentStripped
            
        else:
            # unrecognized future version
            raise FutureFormatException("unrecognized format version")


class Map(BaseMap):
    """
    The most complete form of the map file.

    These are created directly by the map editor and used by the server.
    Only the BaseMap information, however, is sent to the client; in this
    way we can control how much the client knows.  The more the client knows,
    the easier it is for a hacker to take advantage of the system.
    """
    pass        # for now, there's nothing special about the Map
