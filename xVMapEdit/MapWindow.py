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

from xVLib import Maps
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
        @param parent: Parent object of this dialog (usually the main window)
        """
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
        print "[debug] NewMapDialog.OnOK()"     # TODO: Implement
    
    def OnCancel(self):
        """
        Called when the user clicks Cancel.
        """
        print "[debug] NewMapDialog.OnCancel()"    # TODO: Implement


class MapWindow(QtGui.QDialog):
    """
    Window class that contains a map.

    These windows appear in the MDI area of the map editor; each
    holds exactly one map at all times.  The map widget itself
    is contained within a QScrollBox widget.
    """

    def __init__(self, parent=None):
        """
        Sets up the basic window.

        @type parent: QtGui.QWidget
        @param parent: Parent GUI object (should be the MDI area)
        """
        # call QDialog's initializer
        super(QtGui.QDialog, self).__init__(parent)

        # create the scroll area and add it
        self.ScrollArea = QtGui.QScrollArea(parent=self)
        """The scroll area that contains the MapWidget."""


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
    def map(self,newmap):
        # typecheck
        if not isinstance(newmap,Maps.BaseMap):
            raise TypeError("map must inherit Maps.BaseMap")
        self._map = newmap

    def paintEvent(self, event):
        """
        Called when the widget needs to be redrawn to the screen.

        This is an overloaded function from QtGui.QWidget.

        @type event: QtGui.QPaintEvent
        @param event: Event information object
        """
        # typecheck the event
        if not isinstance(event,QtGui.QPaintEvent):
            raise TypeError("event must be of type QtGui.QPaintEvent")

        # figure out what we need to redraw
        
