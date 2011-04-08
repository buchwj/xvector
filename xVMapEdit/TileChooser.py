# xVector Engine Map Editor
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
Contains classes for the tile selectors on the left side of the editor.
"""

from PyQt4 import QtCore, QtGui
from xVClient import Sprite, MapRender
from xVLib import Maps

class TileChooserModel(object):
    """
    Model class for a set of tiles in the map editor.
    
    The backend model of a set of tile-like entities in the map editor
    (ie. tiles, items, etc.).  Keeps track of which is selected.

    Even though the editor uses Qt 4 as the GUI, we're not actually
    bothering with a QtAbstractItemModel implementation here; it's
    way overcomplicated for our purposes, and since we're going ahead
    with writing our own View class anyway, it doesn't make sense.
    """

    def __init__(self, spriteset=None):
        # Typecheck
        if spriteset != None and not isinstance(spriteset,Sprite.SpriteSet):
            raise TypeError("spriteset must be of type Sprite.SpriteSet")

        # Declare the attributes
        self.spriteset = spriteset
        """Handle to the tileset to be displayed."""

        self.selected = -1
        """The tile ID that is currently selected."""

    def SelectTile(self, id):
        """
        Selects a tile from the chooser.
        """
        # Check if the index is valid
        if id < 0 or id >= len(self.spriteset):
            # Invalid index
            raise IndexError("Tile index is out of range")

        # Select the tile
        self.selected = id

    def DeselectTile(self):
        """
	    Deselects the selected tile.
	    """
        self.selected = -1

    def __len__(self):
        """
        Returns the number of tiles in this chooser.
        """
        return len(self.spriteset)


class TileChooserView(QtGui.QWidget):
    """
    View class for a tile chooser on the left side of the editor.
    """

    def __init__(self, parent=None, model=None):
        """
        Creates a new TileChooserView.

        This initializer will optionally accept a handle to a connected
        TileChooserModel object.  This can be specified later or switched
        out if the TileChooserModel is not ready at the time of creation.
        And of course, you can pass a QWidget object as a parent object,
        which can be changed later using the standard PyQt4 methods.
        """
        # typecheck the model parameter
        if model != None and not isinstance(model, TileChooserModel):
            # invalid object passed as model
            raise TypeError("model must be of type TileChooserModel")

        # call the QWidget initializer
        super(TileChooserView, self).__init__(parent)


        # set up our default resize policies
        resize = QtGui.QSizePolicy()
        resize.setHorizontalPolicy(QtGui.QSizePolicy.Fixed)
        resize.setVerticalPolicy(QtGui.QSizePolicy.Minimum)
        self.setSizePolicy(resize)

        # initialize our attributes
        self.model = model
        """Handle to the TileChooserModel object this is connected to."""

        self.ChooserWidth = 5
        """Number of tiles across in the chooser."""

        self.SelectorWidth = 3
        """Width, in pixels, of the lines that surround the selection."""

        # create the pen we use for bordering the selection
        self.selectorPen = QtGui.QPen(QtCore.Qt.white)
        self.selectorPen.setWidth(self.SelectorWidth)

    def _GetTileID(self, x, y):
        """
        Finds the ID number of a tile given its top-left coordinates.
        """
        column = x // Maps.TILE_WIDTH
        row = y // Maps.TILE_HEIGHT
        id = (row * self.ChooserWidth) + column
        return id

    def _GetTLFromID(self, id):
        """
        Determines the top-left coordinates of a tile given its ID.

        This is essentially the inverse operation of _GetTileID(x,y)
        such that _GetTLFromID(_GetTileID(x,y)) = (x,y).
        """
        # check if id is valid
        if id not in self.model.spriteset:
            raise KeyError("tile ID is out of bounds")

        # calculate
        row = id // self.ChooserWidth
        col = id % self.ChooserWidth
        tlx = Maps.TILE_WIDTH * col
        tly = Maps.TILE_HEIGHT * row
        return tlx,tly

    def paintEvent(self, event):
        """
        Called when the view widget is drawn to a surface.

        This is an overloaded method from the QWidget class.  It
        is called by the Qt 4 event manager whenever we need to
        draw the widget to something.
        """
        # Typecheck, make sure that event is actually a QPaintEvent
        if not isinstance(event, QtGui.QPaintEvent):
            raise TypeError("event must be of type QPaintEvent")

        # Set up our drawing system
        r = event.rect()
        painter = QtGui.QPainter()
        whiteBrush = QtGui.QBrush(QtCore.Qt.white)
        painter.begin(self)
        painter.setClipRect(r)
        
        # Clear the rect so we get a clean paint
        painter.setBrush(whiteBrush)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(r)

        # Figure out which tiles must be redrawn
        rect_tlx,rect_tly,w,h = r.getRect()
        tlx, tly = MapRender.GetTileTL(rect_tlx,rect_tly)
        trx, tRy = MapRender.GetTileTR(rect_tlx + w - 1, rect_tly)
        brx, bry = MapRender.GetTileBR(rect_tlx + w - 1, rect_tly + h - 1)
        tiles_wide = (trx - tlx) // Maps.TILE_WIDTH + 1
        tiles_high = (bry - tly) // Maps.TILE_HEIGHT + 1
        
        # Draw the tiles (oh yay, a nested loop)
        must_draw_selection = False
        for tile_across in range(tiles_wide):
            for tile_down in range(tiles_high):
                # figure out what's going on
                tile_x = tlx + (tile_across * Maps.TILE_WIDTH)
                tile_y = tly + (tile_down * Maps.TILE_HEIGHT)
                tile_id = self._GetTileID(tile_x, tile_y)

                # check if that tile exists
                if tile_id not in self.model.spriteset:
                    # doesn't exist
                    continue

                # draw the tile
                tile = self.model.spriteset[tile_id]
                painter.drawPixmap(tile_x,tile_y,tile.img)

                # check if we will need to draw the selection border
                if tile_id == self.model.selected:
                    must_draw_selection = True

        # do we need to draw the selection border?
        if must_draw_selection:
            # get selection information
            tile_id = self.model.selected
            tile_x, tile_y = self._GetTLFromID(tile_id)

            # draw the selection border
            painter.save()
            painter.setPen(self.selectorPen)
            painter.setBrush(QtCore.Qt.NoBrush)
            target = QtCore.QRect()
            target.setX(tile_x)
            target.setY(tile_y)
            target.setWidth(Maps.TILE_WIDTH)
            target.setHeight(Maps.TILE_HEIGHT)
            painter.drawRect(target)
            painter.restore()

        # Clean up
        painter.end()

    def sizeHint(self):
        """
        Calculates the size of the full view widget.

        This value is used by Qt 4 to manage the widget when it
        is added to its parent scrollbox.
        """
        width = Maps.TILE_WIDTH * self.ChooserWidth
        height = Maps.TILE_HEIGHT * (len(self.model) // self.ChooserWidth + 1)
        return QtCore.QSize(width,height)

    def mousePressEvent(self, event):
        """
        Called when the mouse button is released after something is clicked.

        We overload this method from Qt 4 in order to allow the user to
        select a tile by clicking on it.
        """
        # typecheck!
        if not isinstance(event, QtGui.QMouseEvent):
            raise TypeError("event must be of type QtGui.QMouseEvent")

        # deselect whatever is currently selected
        prev_id = self.model.selected
        if prev_id != -1:
            # something was selected, clear the selection
            self.model.DeselectTile()
            prev_tlx, prev_tly = self._GetTLFromID(prev_id)
            prev_target = QtCore.QRect()
            prev_target.setX(prev_tlx - self.SelectorWidth)
            prev_target.setY(prev_tly - self.SelectorWidth)
            prev_target.setWidth(Maps.TILE_WIDTH + 2 * self.SelectorWidth)
            prev_target.setHeight(Maps.TILE_HEIGHT + 2 * self.SelectorWidth)
            self.repaint(prev_target)

        # figure out what was clicked
        clicked_x = event.x()
        clicked_y = event.y()
        tlx, tly = MapRender.GetTileTL(clicked_x, clicked_y)
        id = self._GetTileID(tlx, tly)
        if id not in self.model.spriteset:
            # User clicked outside of the tiles, don't select anything
            return

        # select the tile and redraw it
        self.model.SelectTile(id)
        target = QtCore.QRect()
        target.setX(tlx - self.SelectorWidth)
        target.setY(tly - self.SelectorWidth)
        target.setWidth(Maps.TILE_WIDTH + 2 * self.SelectorWidth)
        target.setHeight(Maps.TILE_HEIGHT + 2 * self.SelectorWidth)
        self.repaint(target)
