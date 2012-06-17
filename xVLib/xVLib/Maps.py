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
import logging
import traceback
from xVLib import BinaryStructs

mainlog = logging.getLogger("")

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
    EndOfTilesFlag = 1073741824
    '''Flag which signals that there are no more tiles in the map file.'''

    def __init__(self, coords=(0,0,0)):
        """
        Creates a new tile with the given layers.  A value of -1 for any layer
        indicates an empty layer.
        
        @type coords: tuple
        @param coords: Coordinates of the new tile as (x,y,z)
        """
        # Set default values
        self.x = 0
        '''X-coordinate of tile'''
        self.y = 0
        '''Y-coordinate of tile'''
        self.z = 0
        '''Depth (layer) of tile'''
        self.tileid = 0
        '''ID of the tile sprite to draw.'''
        
        self.x, self.y, self.z = coords
    
    def Serialize(self, fileobj):
        """
        Outputs a tile to a file using the latest mapfile version.
        
        @type fileobj: file
        @param fileobj: An open file object (or compatible stream) for writing
        """
        # pack all of the flags
        flags = 0
        try:
            BinaryStructs.SerializeUint32(fileobj, flags)
        except:
            msg = "An error occurred while writing to the map file.\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
            raise IOError(msg)
        
        # write the coordinates
        try:
            BinaryStructs.SerializeUint32(fileobj, self.x)
            BinaryStructs.SerializeUint32(fileobj, self.y)
            BinaryStructs.SerializeUint32(fileobj, self.z)
        except:
            msg = "An error occurred while writing to the map file.\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
            raise IOError(msg)
        
        # write the tile information
        try:
            BinaryStructs.SerializeUint32(fileobj, self.tileid)
        except:
            msg = "An error occurred while writing to the map file.\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
            raise IOError(msg)
    
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
            msg = "Unsupported future version of the map file format.\n"
            msg += "Check if a newer version of the program is available."
            mainlog.error(msg)
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
            flags = BinaryStructs.DeserializeUint32(fileobj)
        except Exception as e:
            raise MapError("invalid/corrupt map file", e)
        # Check for the end-of-tiles flag.
        if flags & self.EndOfTilesFlag:
            # End of tiles.
            raise EndOfSectionException
        
        # Read in the rest of the title data.
        # Validation should happen in the map deserialization (since it has
        # access to the map header for dimensional validation).  Just store
        # the values for now.
        try:
            self.x = BinaryStructs.DeserializeUint32(fileobj)
            self.y = BinaryStructs.DeserializeUint32(fileobj)
            self.z = BinaryStructs.DeserializeUint32(fileobj)
            self.tileid = BinaryStructs.DeserializeUint32(fileobj)
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

    def __init__(self, width=1, height=1, depth=5, playerdepth=2):
        """
        Creates an empty map with the given dimensions.
        
        @type width: integer
        @param width: Width of the new map.  Must be greater than 0.
        
        @type height: integer
        @param height: Height of the new map.  Must be greater than 0.
        
        @type depth: integer
        @param depth: Number of layers in the new map.  Must be greater than 0.
        
        @type playerdepth: integer
        @param playerdepth: Layer at which objects are rendered.
        """
        # check the dimensions
        if width <= 0 or height <= 0:
            raise IndexError("map dimensions must be greater than 0")
        
        # predefine some variables
        self.header = MapHeader()
        """Main header of the map file."""
        self.header.Width = width
        self.header.Height = height
        self.header.Depth = depth

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
        
        @type Width: integer
        @param Width: Width of new map to initialize
        
        @type Height: integer
        @param Height: Height of new map to initialize
        
        @type Depth: integer
        @param Depth: Depth of new map to initialize
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
    def MapName(self):
        '''
        Convenience property connected to the map name.
        The actual value is stored in the header.
        '''
        return self.header.MapName
    
    @MapName.setter
    def MapName(self, newname):
        self.header.MapName = newname
    
    @property
    def Width(self):
        """
        Convenience property that abstracts the Width out of the header.
        """
        return self.header.Width
    
    @Width.setter
    def Width(self, width):
        self.header.Width = width
    
    @property
    def Height(self):
        """
        Convenience property that abstracts the Height out of the header.
        """
        return self.header.Height
    
    @Height.setter
    def Height(self, height):
        self.header.Height = height
    
    @property
    def Depth(self):
        '''
        Convenience property that abstracts the Depth out of the header.
        '''
        return self.header.Depth
    
    @Depth.setter
    def Depth(self, depth):
        self.header.Depth = depth
    
    @property
    def PlayerDepth(self):
        '''
        Convenience property that gets PlayerDepth from the header.
        '''
        return self.header.PlayerDepth
    
    @PlayerDepth.setter
    def PlayerDepth(self, playerdepth):
        self.header.PlayerDepth = playerdepth
    
    @property
    def NorthMap(self):
        """
        Convenience property connected to the north-bordered map name.
        This value is actually stored in the header.
        """
        return self.header.NorthMap
    
    @NorthMap.setter
    def NorthMap(self, northmap):
        self.header.NorthMap = northmap
        
    @property
    def EastMap(self):
        """
        Convenience property connected to the east-bordered map name.
        This value is actually stored in the header.
        """
        return self.header.EastMap
    
    @EastMap.setter
    def EastMap(self, eastmap):
        self.header.EastMap = eastmap
        
    @property
    def SouthMap(self):
        """
        Convenience property connected to the south-bordered map name.
        This value is actually stored in the header.
        """
        return self.header.SouthMap
    
    @SouthMap.setter
    def SouthMap(self, southmap):
        self.header.SouthMap = southmap
    
    @property
    def WestMap(self):
        """
        Convenience property connected to the west-bordered map name.
        This value is actually stored in the header.
        """
        return self.header.WestMap
    
    @WestMap.setter
    def WestMap(self, westmap):
        self.header.WestMap = westmap

    @property
    def BackgroundImage(self):
        '''
        Convenience property connected to the background image.
        This value is actually stored in the header.
        '''
        return self.header.BackgroundImage
    
    @BackgroundImage.setter
    def BackgroundImage(self, newimage):
        self.header.BackgroundImage = newimage

    def LoadMapFromFile(self, filepath):
        """
        Loads the map with the given filepath.
        
        @warning
        You should expect exceptions to be raised by this method.  MapError
        and IOError are common, but there's some others, too.

        @type filepath: string
        @param filepath: Filepath of the map file to be loaded
        """
        # open the map file
        mapfile = open(filepath, "rb")
        self.LoadFromOpenFile(mapfile)

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
        self._InitBlankMap(self.Width, self.Height, self.Depth)

        # now we read in each tile
        try:
            # we can only have a maximum tilecount of w*h*d...
            # (it's kinda like the Pauli Exclusion Principle...)
            # ALL TILES MUST HAVE UNIQUE QUANTUM STATES!!!
            for tilenum in xrange(self.Width * self.Height * self.Depth):
                # read in the next tile
                try:
                    tile = Tile().Deserialize(fileobj, formatver)
                except IOError as e:
                    raise MapError("Invalid/corrupt map file", e)
                # validate the tile
                if tile.x < 0 or tile.x >= self.Width:
                    # invalid tile
                    msg = "invalid tile found: x-coordinate out of bounds"
                    raise MapError(msg)
                elif tile.y < 0 or tile.y >= self.Height:
                    # invalid tile
                    msg = "invalid tile found: y-coordinate out of bounds"
                    raise MapError(msg)
                elif tile.z < 0 or tile.z >= self.Depth:
                    # invalid tile
                    msg = "invalid tile found: z-coordinate out of bounds"
                    raise MapError(msg)
                elif tile.tileid < 0:
                    # invalid tile
                    raise MapError("invalid tile found: negative sprite index")
                # store the tile
                self.tiles[tile.z][tile.x][tile.y] = tile
        except EndOfSectionException:
            # This is raised when the tiles section ends; it's a good thing.
            pass
    
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
        for z in range(self.Depth):
            for x in range(self.Width):
                for y in range(self.Height):
                    self.tiles[z][x][y].Serialize(fileobj)
        
        # store the end-of-section flag
        BinaryStructs.SerializeUint32(fileobj, Tile.EndOfTilesFlag)
    
    def Resize(self, width, height, depth):
        """
        Resizes a map to the given dimensions.
        
        @type Width: integer
        @param Width: New Width, in tiles, of the map.
        
        @type Height: integer
        @param Height: New Height, in tiles, of the map.
        """
        # Do we need to change the height?
        if height < self.Height:
            # Shrink the columns.
            for z in range(self.Depth):
                for x in range(self.Width):
                    self.tiles[z][x] = self.tiles[z][x][:height]
        elif height > self.Height:
            # Grow the columns.
            for z in range(self.Depth):
                for x in range(self.Width):
                    for y in range(len(self.tiles[z][x]), height):
                        newtile = Tile((x,y,z))
                        self.tiles[z][x].append(newtile)
        self.Height = height
        
        # Do we need to change the width?
        if width < self.Width:
            # Shrink the rows.
            for z in range(self.Depth):
                self.tiles[z] = self.tiles[z][:width]
        elif width > self.Width:
            # Grow the rows.
            for z in range(self.Depth):
                for x in range(len(self.tiles[z]), width):
                    newrow = []
                    for y in range(self.Height):
                        newtile = Tile((x,y,z))
                        newrow.append(newtile)
                    self.tiles[z].append(newrow)
        self.Width = width
        
        # Do we need to change the depth?
        if depth < self.Depth:
            # Annihilate some layers.
            self.tiles = self.tiles[:depth]
        elif depth > self.Depth:
            # Make some new layers.
            for z in range(len(self.tiles), depth):
                newlayer = []
                for x in range(self.Width):
                    newrow = []
                    for y in range(self.Height):
                        newtile = Tile((x,y,z))
                        newrow.append(newtile)
                    newlayer.append(newrow)
                self.tiles.append(newlayer)
        self.Depth = depth
    
    def CoordinatesInBounds(self, coords):
        '''
        Determines if a pair of tile coordinates are in bounds or not.
        
        @return: Boolean value.
        '''
        x, y = coords
        return (0 <= x < self.Width) and (0 <= y < self.Height)


class MapHeader(object):
    """
    The main header of a map file.
    """
    
    Flag_ContentStripped = 1
    """XOR flag set in the header when the map has been Stripped down."""
    
    def __init__(self):
        """
        Creates a new header with default values.
        """
        self.Width = 1
        """Width of the map in tiles."""

        self.Height = 1
        """Height of the map in tiles."""
        
        self.Depth = 5
        '''Number of layers in the map.'''
        
        self.PlayerDepth = 2
        '''Layer at which objects and players are rendered.''' 

        self.MapName = u""
        """Descriptive, human-readable name of the map."""

        self.NorthMap = u""
        """Name of the map that lies along the northern border."""

        self.EastMap = u""
        """Name of the map that lies along the eastern border."""

        self.SouthMap = u""
        """Name of the map that lies along the southern border."""

        self.WestMap = u""
        """Name of the map that lies along the western border."""
        
        self.BackgroundImage = u""
        '''Optional background image to display behind the map.'''
        
        self.Stripped = False
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
            BinaryStructs.SerializeUTF8(fileobj, self.MapName)
            BinaryStructs.SerializeUint32(fileobj, self.Width)
            BinaryStructs.SerializeUint32(fileobj, self.Height)
            BinaryStructs.SerializeUint32(fileobj, self.Depth)
            BinaryStructs.SerializeUint32(fileobj, self.PlayerDepth)
            BinaryStructs.SerializeUTF8(fileobj, self.NorthMap)
            BinaryStructs.SerializeUTF8(fileobj, self.EastMap)
            BinaryStructs.SerializeUTF8(fileobj, self.SouthMap)
            BinaryStructs.SerializeUTF8(fileobj, self.WestMap)
            BinaryStructs.SerializeUTF8(fileobj, self.BackgroundImage)
        except Exception as e:
            raise IOError("error while writing to map file", e)
        
        # pack the content flags
        try:
            contentFlags = 0
            if self.Stripped:
                contentFlags |= self.Flag_ContentStripped
            BinaryStructs.SerializeUint32(fileobj, contentFlags)
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
                self.MapName = BinaryStructs.DeserializeUTF8(fileobj)
                self.MapName.strip()
                self.Width = BinaryStructs.DeserializeUint32(fileobj)
                self.Height = BinaryStructs.DeserializeUint32(fileobj)
                self.Depth = BinaryStructs.DeserializeUint32(fileobj)
                self.PlayerDepth = BinaryStructs.DeserializeUint32(fileobj)
            except:
                msg = "Map file is invalid/corrupt.\n" 
                msg += traceback.format_exc()
                mainlog.error(msg)
                raise
            
            # validate the basic file information
            if self.Width < 1 or self.Height < 1 or self.Depth < 1:
                # invalid dimensions
                raise MapError("Map file is invalid/corrupt: dimensions")
            if self.PlayerDepth < 0 or self.PlayerDepth >= self.Depth:
                # render depth out of bounds
                raise MapError("Player/object render depth out of bounds.")
            
            # now we read in the links
            try:
                self.NorthMap = BinaryStructs.DeserializeUTF8(fileobj)
                self.NorthMap.strip()
                self.EastMap = BinaryStructs.DeserializeUTF8(fileobj)
                self.EastMap.strip()
                self.SouthMap = BinaryStructs.DeserializeUTF8(fileobj)
                self.SouthMap.strip()
                self.WestMap = BinaryStructs.DeserializeUTF8(fileobj)
                self.WestMap.strip()
                self.BackgroundImage = BinaryStructs.DeserializeUTF8(fileobj)
                self.BackgroundImage.strip()
            except Exception as e:
                raise MapError("Map file is invalid/corrupt.", e)
            
            # and then we read in the content flags...
            try:
                contentflags = BinaryStructs.DeserializeUint32(fileobj)
            except Exception as e:
                raise MapError("Map file is invalid/corrupt.", e)
            self.Stripped = contentflags & self.Flag_ContentStripped
            
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
    pass
