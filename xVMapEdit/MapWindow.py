# xVector Engine Map Editor
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
Contains code for displaying and editing a map within the editor.
"""

import sys

from xVLib import Maps
from xVClient import MapRender, ErrorReporting
from PyQt4 import QtCore, QtGui
from xVMapEdit import NewMapDialogUI

class NewMapDialog(QtGui.QDialog):
    """
    Dialog that is shown every time File->New is clicked.
    
    Prompts the user for basic information about the map used in
    the initial creation of the map.
    """
    
    def __init__(self, parent=None):
        """
        Initializes a new instance of the new map dialog.
        
        @type parent: C{QtGui.QWidget}
        @param parent: Parent object of this dialog (usually the main window).
        This dialog MUST have a parent (and it MUST act like EditorWindow)!
        
        @raise ValueError
        Raised if an invalid parent is specified.
        """
        # Check the parent _very_ carefully
        if parent == None:
            raise ValueError("A parent window must be specified!")
        try:
            # Call a harmless method on the parent's MDI area to test if it exists
            parent.ui.mdiArea.documentMode()
        except AttributeError:
            raise ValueError("Parent window must provide ui.mdiArea")
        
        # initialize ourselves as a QDialog
        super(QtGui.QDialog, self).__init__(parent)
        
        # attach our user interface
        self.uiobj = NewMapDialogUI.Ui_NewMapDialog()
        self.uiobj.setupUi(self)
        
        # add our signals
        self.connect(self.uiobj.buttonBox, QtCore.SIGNAL("accepted()"),
                     self.OnOK)
        self.connect(self.uiobj.buttonBox, QtCore.SIGNAL("rejected()"),
                     self.OnCancel)
        self.connect(self, QtCore.SIGNAL("finished()"), self.OnCancel)
    
    def OnOK(self):
        """
        Called when the user clicks OK.
        """
        print "[debug] NewMapDialog.OnOK()"
        # Validate user input
        name = self.uiobj.txtMapName.text()
        width = self.uiobj.spnWidth.value()
        height = self.uiobj.spnHeight.value()
        if len(name) < 1:
            # Name cannot be blank
            error = "The map name cannot be blank."
            ErrorReporting.ShowError(error, ErrorReporting.WarningError)
            return
        if width <= 0 or height <= 0:
            # Invalid width/height
            error = "Width and height must both be positive."
            QtGui.QMessageBox.warning(self, "Error", error)
            return
        
        # Create our new map
        try:
            NewMap = Maps.Map(width=width, height=height)
        except Exception:
            ErrorReporting.ShowException(ErrorReporting.NormalError,
                                         "Error while creating new map.",
                                         self)
            return
        
        # Create the map window
        widget = EditorWidget(parent=self.parent().ui.mdiArea, map=NewMap)
        wnd = self.parent().ui.mdiArea.addSubWindow(widget)
        wnd.setWindowTitle(name)
    
    def OnCancel(self):
        """
        Called when the user clicks Cancel.
        """
        print "[debug] NewMapDialog.OnCancel()"    # TODO: Implement


class LayerSelector(QtGui.QWidget):
    '''
    Widget that allows the user to select a layer to work with.
    
    This appears at the top of every EditorWidget.
    '''
    
    def __init__(self, value=1):
        '''
        Creates a new layer selector widget.
        
        @type value: integer
        @param value: Initial layer to set the slider to
        '''
        # create the layout
        self.Layout = QtGui.QHBoxLayout()
        self.setLayout(self.Layout)
        
        # create the controls
        self.lblCaption = QtGui.QLabel("Layer: ", parent=self)
        self.Layout.addWidget(self.lblCaption)
        
        self.spnLayer = QtGui.QSlider(parent=self)
        self.spnLayer.setValue(value)
        self.Layout.addWidget(self.spnLayer)


class EditorWidget(QtGui.QWidget):
    """
    Window class that contains a map.

    These windows appear in the MDI area of the map editor; each
    holds exactly one map at all times.  The map widget itself
    is contained within a QScrollBox widget.
    """

    def __init__(self, parent=None, map=None):
        """
        Sets up the basic window.

        @type parent: QtGui.QWidget
        @param parent: Parent GUI object (should be the MDI area)
        """
        # call the parent initializer
        super(EditorWidget, self).__init__(parent)

        # create the layout
        self.Layout = QtGui.QVBoxLayout()
        self.setLayout(self.Layout)
        
        # crea

        # create the scroll area and add it
        self.ScrollArea = QtGui.QScrollArea(parent=self)
        """The scroll area that contains the MapWidget."""
        
        self.Layout.addWidget(self.ScrollArea)
        
        # create the status bar and add it
        self.StatusBar = QtGui.QStatusBar(parent=self)
        """The status bar of the window."""
        
        self.Layout.addWidget(self.StatusBar)
        
        self.CoordinateLabel = QtGui.QLabel(parent=self.StatusBar)
        """Shows the coordinates of the moused-over tile."""
        
        self.CoordinateLabel.setText("(0,0)")
        self.StatusBar.addPermanentWidget(self.CoordinateLabel)
        
        # create our map widget and add it
        self.MapWidget = MapWidget(parent=self.ScrollArea, map=map)
        self.ScrollArea.setWidget(self.MapWidget)
    
    def closeEvent(self, event):
        '''
        Called when the window closes.
        
        @type event: C{QtCore.QCloseEvent}
        @param event: Close event passed by Qt
        '''
        


class MapWidget(QtGui.QWidget):
    """
    Widget that displays a map and allows it to be edited.

    These are almost exclusively used as the contents of the MapWindow
    objects.  In terms of model-view-controller, they can be thought
    of as the corresponding view to a Maps.FullMap model.
    """

    def __init__(self, parent=None, map=None):
        """
        Initializes the widget.
        """
        # initialize the widget itself
        super(QtGui.QWidget, self).__init__(parent)

        # set up some attributes
        self._map = None
        """Internal handle to the map; access this via object.map instead."""

        self.map = map

    @property
    def map(self):
        return self._map
    
    @map.setter
    def map(self, newmap):
        # typecheck
        if not isinstance(newmap,Maps.BaseMap):
            raise TypeError("map must inherit Maps.BaseMap")
        self._map = newmap

    def paintEvent(self, event):
        """
        Called when the widget needs to be redrawn to the screen.

        @type event: C{QtGui.QPaintEvent}
        @param event: Event information object
        """
        # typecheck the event
        if not isinstance(event,QtGui.QPaintEvent):
            raise TypeError("event must be of type QtGui.QPaintEvent")

        # figure out what we need to redraw
        rect = event.rect()
        rx1, ry1, rx2, ry2 = rect.getCoords()
        tlx, tly = MapRender.GetTileTL(rx1, ry1)
        brx, bry = MapRender.GetTileBR(rx2, ry2)
        tiles_wide = (brx - tlx) // Maps.TileWidth
        base_w = tlx // Maps.TileWidth
        tiles_high = (bry - tly) // Maps.TileHeight
        base_h = tly // Maps.TileHeight
        
        # get an active painter 
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setClipRect(rect)
        
        # white-out our target
        whiteBrush = QtGui.QBrush(QtCore.Qt.white)
        painter.fillRect(rect, whiteBrush)
        
        # DRAW. THE. TILES. (left to right, top to bottom)
        for rel_tileY in range(tiles_high):
            tileY = base_h + rel_tileY
            for rel_tileX in range(tiles_wide):
                # check if tile is in bounds
                tileX = base_w + rel_tileX
                if tileX > self.map.header.width:
                    # out of bounds, don't draw anything
                    continue
                elif tileY > self.map.header.height:
                    # out of bounds, don't draw anything
                    continue
                
                # figure out what we're drawing
                try:
                    tile = self.map.tiles[tileX][tileY]
                except IndexError:
                    # the tile grid does NOT agree with the map header!
                    # insert a blank tile here!
                    try:
                        self.map.tiles[tileX][tileY] = Maps.Tile()
                    except:
                        # something is seriously wrong
                        raise Maps.MapError("tile was nonexistant and could not be created")
                
                # okay, now we have to draw all of the layers
    
    def sizeHint(self):
        """
        Calculates the size of the full widget.
        
        This finds the size of the <i>entire</i> widget, not just the
        portion visible in the scroll window.
        
        @returns: A C{QtCore.QSize} object containing the size of the widget.
        """
        width = self.map.header.width * Maps.TileWidth
        height = self.map.header.height * Maps.TileHeight
        return QtCore.QSize(width, height)
