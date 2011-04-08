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
import Sprite

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
    column = x // Maps.TILE_WIDTH
    row = y // Maps.TILE_HEIGHT
    tlx = column * Maps.TILE_WIDTH
    tly = row * Maps.TILE_HEIGHT
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
    trx = tlx + Maps.TILE_WIDTH - 1
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
    bly = tly + Maps.TILE_HEIGHT - 1
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
    brx = tlx + Maps.TILE_WIDTH - 1
    bry = tly + Maps.TILE_HEIGHT - 1
    return (brx,bry)


class MapRenderError(Exception): pass
"""Raised when an error occurs while rendering the map."""


class MapRenderer(object):
    """
    Renders the basic contents of any map to a surface.

    This is certainly not the end-all class to map rendering, or even to
    the basic contents of the maps.  Note that this class does not handle
    neighboring maps (C{BaseMap.northmap}, C{BaseMap.southmap}, etc).  An
    object of this class can only render one map at a time.
    """

    def __init__(self, map=None):
        """
        Initializes a new renderer.

        @type map: L{Maps.BaseMap}
        @param map: Optional map to use in this renderer.
        """
        # set up our attributes
        self.map = map
        """Map object that this renderer is connected to."""

    def _GetTileMajorXY(self, minor_x, minor_y):
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
        major_x = minor_x // Maps.TILE_WIDTH
        major_y = minor_y // Maps.TILE_HEIGHT
        return (major_x, major_y)

    def RenderNegative(self, painter, src_rect=None, dst_rect=None):
        """
        Renders the negative layers of the map in the region given by
        C{src_rect}.

        You do not need to worry about this method changing the properties
        of C{painter}; the painter will emerge from this method with the
        same properties it had when the method was called.

        If no destination rect is passed, this method will, by default,
        render the map to point (0,0).  If no source rect is passed,
        the entire map will be rendered beginning with point (0,0) in the map.

        @type painter: QtGui.QPainter
        @param painter: Painter to use for rendering

        @type src_rect: C{QtCore.QRect}
        @param src_rect: Area of the map that needs to be rendered, in pixels.

        @type dst_rect: C{QtCore.QRect}
        @param dst_rect: Area to render the map to, in pixels.

        @raise MapRenderError: Raised if the map is not valid or not set.
        @raise TypeError: Raised if a parameter has an invalid type.
        """
        # typecheck the parameters
        if not isinstance(painter, QtGui.QPainter):
            raise TypeError("painter must be of type QtGui.QPainter")
        if src_rect != None and not isinstance(src_rect, QtCore.QRect):
            raise TypeError("rect must be of type QtCore.QRect")
        if dst_rect != None and not isinstance(dst_rect, QtCore.QRect):
            raise TypeError("rect must be of type QtCore.QRect")
        
        # check if we even have a map model to use
        if not self.map:
            raise MapRenderError("no map attached to renderer")

        # pre-process our rects
        source = None
        if src_rect == None:
            # create a default rect that covers the full map
            source = QtCore.QRect(0,0,0,0)
            source.setWidth(self.map.width * Maps.TILE_WIDTH)
            source.setHeight(self.map.height * Maps.TILE_HEIGHT)
        else:
            # a rect was passed in
            source = src_rect

        dest = None
        if dst_rect == None:
            # create a default rect of the maximum possible size
            dest = QtCore.QRect(0,0,0,0)
            idealWidth = self.map.width * Maps.TILE_WIDTH
            idealHeight = self.map.height * Maps.TILE_HEIGHT
            if idealWidth > painter.width():
                dest.setWidth(painter.width())
            else:
                dest.setWidth(idealWidth)
            if idealHeight > painter.height():
                dest.setHeight(painter.height())
            else:
                dest.setHeight(idealHeight)
        elif isinstance(dst_rect, QtCore.QRect):
            dest = dst_rect

        # calculate our major ranges
        ul_tx, ul_ty = self._GetTileMajorXY(source.x(), source.y())
        brx = source.x() + source.width()
        bry = source.y() + source.height()
        br_tx, br_ty = self._GetTileMajorXY(brx, bry)

        # backup the painter's state
        painter.save()
        painter.setClipRect(dest)

        # iterate through our tiles
        for MajX in range(ul_tx, br_tx):
            for MajY in range(ul_ty, br_ty):
                # find the actual target region
                naive_target = QtCore.QRect(0,0,0,0)
                naive_target.setX(MajX * Maps.TILE_WIDTH)
                naive_target.setY(MajY * Maps.TILE_HEIGHT)
                naive_target.setWidth(Maps.TILE_WIDTH)
                naive_target.setHeight(Maps.TILE_HEIGHT)
                
                real_target = naive_target.intersected(dest)
                if real_target.isNull():
                    # this tile will be entirely clipped; skip it
                    continue

                # render the tile
                self._RenderNegativeTile(painter, MajX, MajY, naive_target)

        # restore the painter's state
        painter.load()

    def _RenderNegativeTile(self, painter, major_x, major_y, dst_rect):
        """
        Renders the negative-depth layers of a tile to the target.

        Be warned that this method may alter the state of the painter.
        If you need to keep settings, call C{painter.save()} and
        C{painter.load()} around the call to this method.

        @type painter: C{QtGui.QPainter}
        @param painter: painter object to use for rendering

        @type major_x: integer
        @param major_x: tile's X coordinate in the tile grid

        @type major_y: integer
        @param major_y: tile's Y coordinate in the tile grid

        @type dst_rect: C{QtCore.QRect}
        @param dst_rect: Rect of the target surface to draw to

        @raise IndexError: Raised if the coordinates are out-of-bounds.
        @raise MapRenderError: Raised if the tile is invalid within the map.
        """
        # check the specified coordinates
        if major_x < 0 or major_y < 0:
            raise IndexError("major coordinates are out-of-bounds")
        elif major_x >= self.map.width() or major_y >= self.map.height():
            raise IndexError("major coordinates are out-of-bounds")

        # grab our tile
        tile = self.map.tiles[major_x][major_y]
        if not isinstance(tile, Maps.Tile):
            # invalid tile
            err = "invalid tile at (%d, %d)" % (major_x, major_y)
            raise MapRenderError(err)

        # walk through each layer
        for depth, layer in sorted(tile.layers.items()):
            # check the depth
            if depth > 0:
                # this is now out of our domain
                break
            # render the layer
            self._RenderSingleLayer(layer, painter, dst_rect)
    
    def _RenderPositiveTile(self, painter, major_x, major_y, dst_rect):
        """
        Renders the positive-depth layers of a tile to the target.

        Be warned that this method may alter the state of the painter.
        If you need to keep settings, call C{painter.save()} and
        C{painter.load()} around the call to this method.

        @type painter: C{QtGui.QPainter}
        @param painter: painter object to use for rendering

        @type major_x: integer
        @param major_x: tile's X coordinate in the tile grid

        @type major_y: integer
        @param major_y: tile's Y coordinate in the tile grid

        @type dst_rect: C{QtCore.QRect}
        @param dst_rect: Rect of the target surface to draw to

        @raise IndexError: Raised if the coordinates are out-of-bounds.
        @raise MapRenderError: Raised if the tile is invalid within the map.
        """
        # check the specified coordinates
        if major_x < 0 or major_y < 0:
            raise IndexError("major coordinates are out-of-bounds")
        elif major_x >= self.map.width() or major_y >= self.map.height():
            raise IndexError("major coordinates are out-of-bounds")

        # grab our tile
        tile = self.map.tiles[major_x][major_y]
        if not isinstance(tile, Maps.Tile):
            # invalid tile
            err = "invalid tile at (%d, %d)" % (major_x, major_y)
            raise MapRenderError(err)
        
        # check which layers are left to render
        

        # walk through each layer
        for depth, layer in sorted(tile.layers.items()):
            # check the depth
            if depth > 0:
                # this is now out of our domain
                break
            # render the layer
            self._RenderSingleLayer(layer, painter, dst_rect)
            
    def _RenderSingleLayer(self, layer, painter, dst_rect):
        """
        Renders a single layer of the map to the target.
        
        @type layer: L{xVLib.Maps.Layer}
        @param layer: Layer to render.
        
        @type painter: C{QtGui.QPainter}
        @param painter: Painter object to use for rendering.
        
        @type dst_rect: C{QtCore.QRect}
        @param dst_rect: Target rect to render to.
        """
        # what type of layer is this?
        if layer.animated:
            # animation layer
            pass    # TODO: Implement

        else:
            # static layer
            sprite = Sprite.GetSpriteSet("tiles")[layer.content_id]
            painter.drawPixmap(dst_rect, sprite.img)
