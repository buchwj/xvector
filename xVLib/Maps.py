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

class EndOfSectionException(Exception): pass
'''Raised when the end of a section is reached in the map file.'''


class Tile(object):
    """
    Represents a single tile in a map.
    """
    
    # Tile flags.
    BlockedFlag = 1
    '''Flag which signals that a tile is blocked.'''
    EndOfTilesFlag = 1073741824
    '''Flag which signals that there are no more tiles in the map file.'''

    def __init__(self):
        """
        Creates a new tile with the given layers.  A value of -1 for any layer
        indicates an empty layer.
        
        @keyword blocked: If C{True}, this tile is impassable.
        """
        # Set default values
        self.x = 0
        '''X-coordinate of tile'''
        self.y = 0
        '''Y-coordinate of tile'''
        self.z = 0
        '''Depth (layer) of tile'''
        self.blocked = False
        '''If true, tile is impassible.'''
        self.tileid = 0
        '''ID of the tile sprite to draw.'''
    
    
    def Serialize(self, fileobj):
        """
        Outputs a tile to a file using the latest mapfile version.
        
        @type fileobj: file
        @param fileobj: An open file object (or compatible stream) for writing
        """
        # pack all of the flags
        flags = 0
        if self.blocked:
            flags |= self.BlockedFlag
        try:
            BinaryStructs.SerializeUint(fileobj, flags)
        except Exception as e:
            raise IOError("error while writing to map file", e)
        
        # write the coordinates
        try:
            BinaryStructs.SerializeUint(fileobj, self.x)
            BinaryStructs.SerializeUint(fileobj, self.y)
            BinaryStructs.SerializeUint(fileobj, self.z)
        except Exception as e:
            raise IOError("error while writing to map file", e)
        
        # write the tile information
        try:
            BinaryStructs.SerializeUint(fileobj, self.tileid)
        except Exception as e:
            raise IOError("error while writing to map file", e)
    
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
        except Exception as e:
            raise MapError("invalid/corrupt map file", e)
        # Check for the end-of-tiles flag.
        if flags & self.EndOfTilesFlag:
            # End of tiles.
            raise EndOfSectionException()
        
        # And now the normal flags...
        self.blocked = bool(flags & self.BlockedFlag)
        
        # Read in the rest of the title data.
        # Validation should happen in the map deserialization (since it has
        # access to the map header for dimensional validation).  Just store
        # the values for now.
        try:
            self.x = BinaryStructs.DeserializeUint(fileobj)
            self.y = BinaryStructs.DeserializeUint(fileobj)
            self.z = BinaryStructs.DeserializeUint(fileobj)
            self.tileid = BinaryStructs.DeserializeUint(fileobj)
        except Exception as e:
            raise MapError("invalid/corrupt map file", e)
            

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

    def __init__(self, width=1, height=1, depth=1):
        """
        Creates an empty map with the given dimensions.
        
        @type width: integer
        @param width: Width of the new map.  Must be greater than 0.
        
        @type height: integer
        @param height: Height of the new map.  Must be greater than 0.
        
        @type depth: integer
        @param depth: Number of layers in the new map.  Must be greater than 0.
        """
        # check the dimensions
        if width <= 0 or height <= 0:
            raise IndexError("map dimensions must be greater than 0")
        
        # predefine some variables
        self.header = MapHeader()
        """Main header of the map file."""
        self.header.width = width
        self.header.height = height
        self.header.depth = depth

        self.tiles = []
        '''
        The collection of tiles that constitutes this map.
        
        This is essentially a three-dimensional matrix addressed by
        C{tiles[z][x][y]}.  The unusual ordering of the coordinates allows for
        fast access to individual layers.
        '''

        self.version = CurrentMapVersion
        """
        The mapfile format version this was loaded from.

        Note that this does not affect which format version the map
        will be saved as; map files are always saved as the latest
        version of the map file format.
        """
        
        # Go ahead and initialize the tile collection
        self._InitBlankMap(width, height, depth)
    
    def _InitBlankMap(self, width, height, depth):
        '''
        Initializes the map to a completely blank map.
        
        @type width: integer
        @param width: Width of new map to initialize
        
        @type height: integer
        @param height: Height of new map to initialize
        
        @type depth: integer
        @param depth: Depth of new map to initialize
        '''
        # validate parameters
        if width < 1 or height < 1 or depth < 1:
            raise MapError("Map must have positive dimensions to be initialized")
        
        # initialize blank tiles
        self.tiles = []
        for z in range(depth):
            self.tiles.append([])
            for x in range(width):
                self.tiles[z].append([])
                for y in range(height):
                    tile = Tile()
                    tile.x = x
                    tile.y = y
                    tile.z = z
                    self.tiles[z][x].append(tile)
        
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
    def depth(self):
        '''
        Convenience property that abstracts the depth out of the header.
        '''
        return self.header.depth
    
    @depth.setter
    def depth(self, depth):
        self.header.depth = depth
    
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

        # initialize the map to the correct dimensions
        self._InitBlankMap(self.width, self.height, self.depth)

        # now we read in each tile
        try:
            while True:
                # read in the next tile
                try:
                    tile = Tile().Deserialize(fileobj, formatver)
                except IOError as e:
                    raise MapError("Invalid/corrupt map file", e)
                # validate the tile
                if tile.x < 1 or tile.x > self.width:
                    # invalid tile
                    raise MapError("invalid tile found: x-coordinate out of bounds")
                elif tile.y < 1 or tile.y > self.height:
                    # invalid tile
                    raise MapError("invalid tile found: y-coordinate out of bounds")
                elif tile.z < 1 or tile.z > self.depth:
                    # invalid tile
                    raise MapError("invalid tile found: z-coordinate out of bounds")
                elif tile.tileid < 0:
                    # invalid tile
                    raise MapError("invalid tile found: negative sprite index")
                # store the tile
                self.tiles[tile.z][tile.x][tile.y] = tile
        except EndOfSectionException:
            # This is raised when the tiles section ends; it's a good thing.
            pass    # Continue loading the map.
    
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
        
        @raise IOError: Not directly raised, but you should expect these to
        occur and handle them accordingly.
        
        @type fileobj: C{file}
        @param fileobj: An open file object (or compatible stream) to
        write the map to.
        """
        # write the meta-header
        mheader = self.MetaheaderStruct.pack(self.MagicNumber, CurrentMapVersion)
        fileobj.write(mheader)
        
        # write the header
        self.header.Serialize(fileobj)
        
        # write the tiles
        for z in self.depth:
            for x in self.width:
                for y in self.height:
                    self.tiles[z][x][y].Serialize(fileobj)
    
    def Resize(self, width, height, depth):
        """
        Resizes a map to the given dimensions.
        
        @type width: integer
        @param width: New width, in tiles, of the map.
        
        @type height: integer
        @param height: New height, in tiles, of the map.
        """
        # check the dimensions
        if width <= 0 or height <= 0 or depth <= 0:
            # invalid dimensions
            raise IndexError("map dimensions must be greater than 0")
        
        # are we increasing in depth?
        if depth > self.header.depth:
            # add and fill new Z components
            for z in range(self.header.depth, depth):
                self.tiles[z].insert(z,[])
                for x in range(self.header.width):
                    self.tiles[z].insert(x,[])
                    for y in range(self.header.height):
                        # insert a new blank tile
                        self.tiles[z][x].insert(y,Tile())
        # if not, then are we decreasing in depth?
        elif depth < self.header.depth:
            # destroy the Z components
            for z in range(depth, self.header.depth):
                del self.tiles[z]
        
        # are we increasing in width?
        if width > self.header.width:
            # add and fill new X components
            for z in range(depth):
                for x in range(self.header.width, width):
                    self.tiles[z].insert(x,[])
                    for y in range(self.header.height):
                        # insert a new blank tile
                        self.tiles[z][x].insert(y,Tile())
        # if not, then are we decreasing in width?
        elif width < self.header.width:
            # destroy the X components
            for z in range(depth):
                for x in range(width, self.header.width):
                    del self.tiles[z][x]
        
        # now check the height - is it increasing?
        if height > self.header.height:
            # add new Y components
            for y in range(self.header.height, height):
                for x in range(width):
                    for z in range(depth):
                        self.tiles[z][x].insert(y,Tile())
        # if not, are we decreasing in height?
        elif height < self.header.height:
            # destroy some Y components
            for y in range(height, self.header.height):
                for x in range(width):
                    for z in range(depth):
                        del self.tiles[z][x][y]
        
        # update the dimensions in the header
        self.header.width = width
        self.header.height = height
        self.header.depth = depth


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
        self.width = 1
        """Width of the map in tiles."""

        self.height = 1
        """Height of the map in tiles."""
        
        self.depth = 1
        '''Number of layers in the map.'''

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
            BinaryStructs.SerializeUint(fileobj, self.width)
            BinaryStructs.SerializeUint(fileobj, self.height)
            BinaryStructs.SerializeUint(fileobj, self.depth)
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
                contentFlags |= self.Flag_ContentStripped
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
            try:
                self.mapname = BinaryStructs.DeserializeUTF8String(fileobj)
                self.mapname.strip()
                self.width = BinaryStructs.DeserializeUint(fileobj)
                self.height = BinaryStructs.DeserializeUint(fileobj)
                self.depth = BinaryStructs.DeserializeUint(fileobj)
            except Exception as e:
                raise MapError("Map file is invalid/corrupt.", e)
            
            # validate the basic file information
            if self.width < 1 or self.height < 1 or self.depth < 1:
                # invalid dimensions
                raise MapError("Map file is invalid/corrupt: dimensions")
            
            # now we read in the links
            try:
                self.northmap = BinaryStructs.DeserializeUTF8String(fileobj)
                self.northmap.strip()
                self.eastmap = BinaryStructs.DeserializeUTF8String(fileobj)
                self.eastmap.strip()
                self.southmap = BinaryStructs.DeserializeUTF8String(fileobj)
                self.southmap.strip()
                self.westmap = BinaryStructs.DeserializeUTF8String(fileobj)
                self.westmap.strip()
            except Exception as e:
                raise MapError("Map file is invalid/corrupt.", e)
            
            # and then we read in the content flags...
            try:
                contentflags = BinaryStructs.DeserializeUint(fileobj)
            except Exception as e:
                raise MapError("Map file is invalid/corrupt.", e)
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
    def __init__(self, width=1, height=1, depth=1):
        '''
        Creates an empty map with the given dimensions.
        
        @type width: integer
        @param width: Width of the new map.  Must be greater than 0.
        
        @type height: integer
        @param height: Height of the new map.  Must be greater than 0.
        
        @type depth: integer
        @param depth: Number of layers in the new map.  Must be greater than 0.
        '''
        # initialize the base map
        super(Map, self).__init__(width, height, depth)
