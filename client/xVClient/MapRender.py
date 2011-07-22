# -*- coding: utf-8 -*-

# xVector Engine Client
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
Contains code for rendering the basics of a map to a surface.

The code in this module does not render the entire map; rather, it
renders requested portions of the tiles, while at the same time
managing their animations.  By isolating this rendering code into
a separate module, we can render map tiles with consistent results
in both the client and the map editor; in addition, this allows us
to display animated tiles in both the client and the map editor,
making it easier for mappers to picture how their maps will look in
the engine.
"""

from PyQt4 import QtCore, QtGui
from xVLib import Maps

# First up, we have a set of functions that calculate tile coordinates.
def GetTileTL(x, y):
    """
    Finds the top-left corner of a tile.

    Given an (x,y) coordinate pair of a point within a tile, this
    method calculates the (x,y) coordinate pair of the top-left
    corner of the tile.  These are returned as a tuple.
    
    @type x: integer
    @param x: X-coordinate of the point to check
    
    @type y: integer
    @param y: Y-coordinate of the point to check
    
    @returns: The (x,y) coordinates in tuple form.
    """
    # Validity check of the (x,y) coordinate pair
    if x < 0 or y < 0:
        raise IndexError("(x,y) coordinate pair out of bounds")

    # Calculate the top-left coordinates
    column = x // Maps.TileWidth
    row = y // Maps.TileHeight
    tlx = column * Maps.TileWidth
    tly = row * Maps.TileHeight
    return (tlx, tly)


def GetTileTR(x, y):
    """
    Finds the top-right corner of a tile.

    Given an (x,y) coordinate pair of a point within a tile, this
    method calculates the (x,y) coordinate pair of the top-right
    corner of the tile.  These are returned as a tuple.
    
    @type x: integer
    @param x: X-coordinate of the point to check
    
    @type y: integer
    @param y: Y-coordinate of the point to check
    
    @returns: The (x,y) coordinates in tuple form.
    """
    # Validity check of the (x,y) coordinate pair
    if x < 0 or y < 0:
        raise IndexError("(x,y) coordinate pair out of bounds")

    # Calculate the bottom-right coordinates
    tlx, tly = GetTileTL(x,y)
    trx = tlx + Maps.TileWidth - 1
    return (trx,tly)


def GetTileBL(x, y):
    """
    Finds the bottom-left corner of a tile.

    Given an (x,y) coordinate pair of a point within a tile, this
    method calculates the (x,y) coordinate pair of the bottom-left
    corner of the tile.  These are returned as a tuple.
    
    @type x: integer
    @param x: X-coordinate of the point to check
    
    @type y: integer
    @param y: Y-coordinate of the point to check
    
    @returns: The (x,y) coordinates in tuple form.
    """
    # Validity check of the (x,y) coordinate pair
    if x < 0 or y < 0:
        raise IndexError("(x,y) coordinate pair out of bounds")

    # Calculate the bottom-right coordinates
    tlx, tly = GetTileTL(x,y)
    bly = tly + Maps.TileHeight - 1
    return (tlx,bly)


def GetTileBR(x, y):
    """
    Finds the bottom-right corner of a tile.

    Given an (x,y) coordinate pair of a point within a tile, this
    method calculates the (x,y) coordinate pair of the bottom-right
    corner of the tile.  These are returned as a tuple.
    
    @type x: integer
    @param x: X-coordinate of the point to check
    
    @type y: integer
    @param y: Y-coordinate of the point to check
    
    @returns: The (x,y) coordinates in tuple form.
    """
    # Validity check of the (x,y) coordinate pair
    if x < 0 or y < 0:
        raise IndexError("1 - (x,y) coordinate pair out of bounds")

    # Calculate the bottom-right coordinates
    tlx, tly = GetTileTL(x,y)
    brx = tlx + Maps.TileWidth - 1
    bry = tly + Maps.TileHeight - 1
    return (brx,bry)


class MapRenderError(Exception): pass
"""Raised when an error occurs while rendering the map."""


class MapRenderer(object):
    """
    Renders the basic contents of any map to a surface.

    This is certainly not the end-all class to map rendering, or even to
    the basic contents of the maps.  Note that this class does not handle
    neighboring maps (C{BaseMap.northmap}, C{BaseMap.southmap}, etc).  An
    object of this class can only render one map at a time.  For a renderer which
    handles neighboring maps, see the FullMapRenderer class.
    """

    def __init__(self, sprites, map=None):
        """
        Initializes a new renderer.

        @type sprites: Sprite.SpritesManager
        @param sprites: Sprite manager to use for rendering.

        @type map: L{Maps.BaseMap}
        @param map: Optional map to use in this renderer.
        """
        # set up our attributes
        self.Sprites = sprites
        '''Sprite manager to use for rendering.'''
        
        self.map = map
        """Map object that this renderer is connected to."""

    def GetTileMajorXY(self, minor_x, minor_y):
        """
        Gets the major X-coordinate of a tile given the coordinates
        of the tile.

        A major X-coordinate is the X coordinate with tile-level
        accuracy; that is, it is the X-coordinate of a tile within a grid
        of other tiles, with no concern for the underlying pixels.

        @type minor_x: integer
        @param minor_x: X coordinate of a pixel in the tile

        @type minor_y: integer
        @param minor_y: Y coordinate of a pixel in the tile

        @return: the X and Y major coordinates of the tile
        @rtype: tuple
        """
        major_x = minor_x // Maps.TileWidth
        major_y = minor_y // Maps.TileHeight
        return (major_x, major_y)

    def RenderMap(self, surface, target_coords, source_coords, target_offset,
                  width, height):
        '''
        Draws a portion of the map to the given surface.
        
        @type surface: C{QtGui.QPaintDevice}
        @param surface: Target surface to render to
        
        @type target_coords: integer tuple (coordinates, (x,y))
        @param target_coords: Upper-left corner of target surface to render to
        
        @type source_coords: integer tuple (coordinates, (x,y))
        @param source_coords: Absolute upper-left corner of map to render from
        
        @type target_offset: integer tuple (coordinates, (x,y))
        @param target_offset: The position in the target surface of the point
        on the map given by (0,0).
        
        @type width: integer
        @param width: Width of map section to render (pixels)
        
        @type Height: integer
        @param Height: Height of map section to render (pixels)
        '''
        # Validate parameters
        stlx,stly = source_coords
        if stlx < 0 or stly < 0 or stlx > self.map.Width * Maps.TileWidth     \
            or stly > self.map.Height * Maps.TileHeight:
            raise IndexError("source coordinates out of bounds")
        if width < 1 or height < 1:
            raise MapRenderError("Rendered region dimensions must be >= 1")
        
        # Wipe the surface.
        painter = QtGui.QPainter()
        painter.begin(surface)
        painter.setPen(QtCore.Qt.NoPen)
        whiteBrush = QtGui.QBrush(QtCore.Qt.white)
        painter.setBrush(whiteBrush)
        
        targetBaseX, targetBaseY = target_coords
        targetRect = QtCore.QRect(targetBaseX, targetBaseY, width, height)
        painter.fillRect(targetRect, whiteBrush)
        
        painter.end()
        
        # Walk through each layer and render, from lowest Depth to highest
        for z in range(self.map.Depth):
            self.RenderLayer(surface, target_coords, source_coords,
                             target_offset, width, height, z)
    
    def RenderLayer(self, surface, target_coords, source_coords, target_offset,
                    width, height, layer, alpha=255):
        '''
        Draws a portion of a single Depth layer of the map to the given surface.
        
        This method will not wipe the surface prior to rendering.  If there is
        garbage below, it will remain visible through any transparent render.
        This is useful if one layer is being rendered atop another.
        
        @warning: If alpha is set to any value other than 255 or 0, there will
        be a massive performance hit.  It is STRONGLY RECOMMENDED that the alpha
        setting not be used in the client; this feature is mainly provided to
        give the map editor a nice appearance.
        
        @raise IndexError: Raised if the supplied source coordinates are out
        of bounds.
        
        @raise MapRenderError: Raised if other supplied parameters are not
        valid for this map.
        
        @type surface: C{QtGui.QPaintDevice}
        @param surface: Target surface to render to
        
        @type target_coords: integer tuple (coordinates, (x,y))
        @param target_coords: Upper-left corner of target surface to render to
        
        @type source_coords: integer tuple (coordinates, (x,y))
        @param source_coords: Absolute upper-left corner of map to render from
        
        @type target_offset: integer tuple (coordinates, (x,y))
        @param target_offset: The position in the target surface of the point
        on the map given by (0,0).
        
        @type width: integer
        @param width: Width of map section to render (pixels)
        
        @type height: integer
        @param height: Height of map section to render (pixels)
        
        @type layer: integer
        @param layer: Layer number to render
        
        @type alpha: integer
        @param alpha: Alpha to blend this layer with (255 = opaque)
        '''
        # First of all, do we even have to draw this?
        if alpha == 0:
            # Totally transparent
            return
        
        # Validate parameters
        stlx,stly = source_coords
        if (stlx < 0 or stly < 0 or stlx > self.map.Width * Maps.TileWidth
            or stly > self.map.Height * Maps.TileHeight):
            raise IndexError("source coordinates out of bounds")
        if width < 1 or height < 1:
            raise MapRenderError("Rendered region dimensions must be >= 1")
        if layer < 0 or layer > self.map.Depth:
            raise MapRenderError("Cannot render a layer which does not exist.")
        
        # Prepare the surface
        painter = QtGui.QPainter()
        painter.begin(surface)
        painter.setPen(QtCore.Qt.NoPen)
        if alpha != 255:
            painter.setOpacity(alpha / 255.0)
        
        # Set the clipping rectangle
        targetBaseX, targetBaseY = target_coords
        targetRect = QtCore.QRect(targetBaseX, targetBaseY, width, height)
        painter.setClipRect(targetRect)
        
        # Adjust our render to the correct point on the surface.
        targetStartX, targetStartY = target_offset
        
        # Figure out what we're rendering
        current_layer = self.map.tiles[layer]
        startX, startY = GetTileTL(stlx,stly)
        endX, endY = GetTileTL(stlx + width, stly + height)
        startX //= Maps.TileWidth
        startY //= Maps.TileHeight
        endX = endX // Maps.TileWidth + 1
        endY = endY // Maps.TileHeight + 1
        if endX > self.map.Width: endX = self.map.Width
        if endY > self.map.Height: endY = self.map.Height
        
        # Render
        for x in range(startX, endX):
            for y in range(startY, endY):
                # acquire the tile
                try:
                    tile = current_layer[x][y]
                except IndexError:
                    # tile not found; skipif endY > self.map.Height: endY = self.map.Height
                    print "[warning] tried to render tile out of bounds"
                    print "\tcoordinates:", x, ",", y
                    continue
                # do we have the sprite?
                if tile.tileid == 0:
                    # blank tile, don't bother drawing it
                    continue
                try:
                    sprite = self.Sprites['tiles'][tile.tileid]
                except KeyError:
                    # we don't have the sprite for this tile; skip
                    print "[warning] tile", tile.tileid, "not found, skipping"
                    continue
                # render the sprite
                targetX = x * Maps.TileWidth + targetStartX
                targetY = y * Maps.TileHeight + targetStartY
                painter.drawPixmap(targetX, targetY, sprite.img)
        
        # Clean up.
        painter.end()
