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
Contains the main window class for the map editor.
"""

from PySide import QtCore, QtGui
from xVMapEdit import MapEditorUI, MapEditorAboutUI, TileChooser, MapWindow
from xVClient import Sprite

class ResourceToggle(object):
    """
    Contains a set of toggle buttons which are used to control which
    type of resource is being manipulated at a given time.
    """
    
    # A few constants...
    ID_Tiles = 1
    """Button ID of the tiles button"""
    ID_Anim = 2
    """Button ID of the animations button"""
    ID_Items = 3
    """Button ID of the items button"""
    ID_NPCs = 4
    """Button ID of the NPCs button"""
    
    def __init__(self, window):
        """
        Initializes a new set of toggle controls for the resources.
        
        @type window: C{QtGui.QMainWindow}
        @param window: Main window of the map editor
        """
        # set up the basics
        self.MainWindow = window
        
        # create our buttons
        self.ButtonGroup = QtGui.QButtonGroup()
        self.ButtonGroup.setExclusive(True)
        
        self.TileButton = QtGui.QToolButton()
        tile_icon = QtGui.QIcon()
        tile_icon.addPixmap(QtGui.QPixmap(":/ResourceIcons/res/TilesIcon.png"))
        self.TileButton.setIcon(tile_icon)
        self.TileButton.setCheckable(True)
        self.TileButton.setChecked(True)
        self.TileButton.setToolTip(_("Static Tiles"))
        self.ButtonGroup.addButton(self.TileButton, self.ID_Tiles)
        
        self.AnimButton = QtGui.QToolButton()
        anim_icon = QtGui.QIcon()
        anim_icon.addPixmap(QtGui.QPixmap(":/ResourceIcons/res/AnimationsIcon.png"))
        self.AnimButton.setIcon(anim_icon)
        self.AnimButton.setCheckable(True)
        self.AnimButton.setToolTip(_("Animated Tiles"))
        self.ButtonGroup.addButton(self.AnimButton, self.ID_Anim)
        
        self.ItemButton = QtGui.QToolButton()
        item_icon = QtGui.QIcon()
        item_icon.addPixmap(QtGui.QPixmap(":/ResourceIcons/res/ItemsIcon.png"))
        self.ItemButton.setIcon(item_icon)
        self.ItemButton.setCheckable(True)
        self.ItemButton.setToolTip(_("Items"))
        self.ButtonGroup.addButton(self.ItemButton, self.ID_Items)
        
        self.NPCButton = QtGui.QToolButton()
        npc_icon = QtGui.QIcon()
        npc_icon.addPixmap(QtGui.QPixmap(":/ResourceIcons/res/NPCsIcon.png"))
        self.NPCButton.setIcon(npc_icon)
        self.NPCButton.setCheckable(True)
        self.NPCButton.setToolTip(_("NPCs"))
        self.ButtonGroup.addButton(self.NPCButton, self.ID_NPCs)
        
        # connect the button signals
        self.MainWindow.connect(self.ButtonGroup, 
                                QtCore.SIGNAL("buttonClicked(int)"),
                                self.OnViewChange)
    
    def Attach(self, toolbar):
        """
        Attaches the buttons to a toolbar.
        
        @type toolbar: C{QtGui.QToolBar}
        @param toolbar: Toolbar to attach the buttons to.
        """
        toolbar.addWidget(self.TileButton)
        toolbar.addWidget(self.AnimButton)
        toolbar.addWidget(self.ItemButton)
        toolbar.addWidget(self.NPCButton)
    
    def OnViewChange(self, id):
        """
        Called from Qt when a button is clicked.
        
        @type id: Integer
        @param id: ID of the button that was clicked
        """
        if id == self.ID_Tiles:
            view = self.MainWindow.chooserviews["tiles"]
            self.MainWindow.ui.ResourceScroll.setWidget(view)
        elif id == self.ID_Anim:
            pass    # TODO: Implement
        elif id == self.ID_Items:
            pass    # TODO: Implement
        elif id == self.ID_NPCs:
            pass    # TODO: Implement
        else:
            print "[error] unrecognized resource view", id, "selected"


class MainWindow(QtGui.QMainWindow):
    """
    Main window class for the map editor.
    """

    def __init__(self, parent=None):
        """
        Initializes the main window object.

        Although the app parameter is a keyword argument with a
        default value of None, a MapEditorApp object must be passed
        to this initializer.  If one is not, a TypeError will be raised.
        """
        # initialize the object as a standard main window
        super(MainWindow, self).__init__(parent)

        # okay, now create the UI object and map it to the window
        self.ui = MapEditorUI.Ui_MapEditorWindow()
        """The Qt 4 user interface object."""
        self.ui.setupUi(self)
        
        # next, set up the main toolbar
        self.ui.toolBar.addAction(self.ui.action_New)
        self.ui.toolBar.addAction(self.ui.action_Open)
        self.ui.toolBar.addAction(self.ui.action_Save)
        self.ui.toolBar.addSeparator()
        self.ui.toolBar.addAction(self.ui.action_Undo)
        self.ui.toolBar.addAction(self.ui.action_Redo)
        self.ui.toolBar.addSeparator()
        self.ui.toolBar.addAction(self.ui.action_Copy)
        self.ui.toolBar.addAction(self.ui.actionC_ut)
        self.ui.toolBar.addAction(self.ui.action_Paste)
        self.ui.toolBar.addSeparator()
        
        # add the resource toggle
        self.restoggle = ResourceToggle(self)
        self.restoggle.Attach(self.ui.toolBar)

        # hook the menu signals to the appropriate slots
        self.connect(self.ui.action_New, QtCore.SIGNAL("triggered()"),
                     self.OnFileNew)
        self.connect(self.ui.action_Open, QtCore.SIGNAL("triggered()"),
                     self.OnFileOpen)
        self.connect(self.ui.action_Save, QtCore.SIGNAL("triggered()"),
                     self.OnFileSave)
        self.connect(self.ui.action_Save, QtCore.SIGNAL("triggered()"),
                     self.OnFileSaveAs)
        self.connect(self.ui.actionClose, QtCore.SIGNAL("triggered()"),
                     self.OnFileClose)
        self.connect(self.ui.action_Quit, QtCore.SIGNAL("triggered()"),
                     self, QtCore.SLOT("close()"))
        self.connect(self.ui.action_Undo, QtCore.SIGNAL("triggered()"),
                     self.OnEditUndo)
        self.connect(self.ui.action_Redo, QtCore.SIGNAL("triggered()"),
                     self.OnEditRedo)
        self.connect(self.ui.action_Copy, QtCore.SIGNAL("triggered()"),
                     self.OnEditCopy)
        self.connect(self.ui.actionC_ut, QtCore.SIGNAL("triggered()"),
                     self.OnEditCut)
        self.connect(self.ui.action_Paste, QtCore.SIGNAL("triggered()"),
                     self.OnEditPaste)
        self.connect(self.ui.action_Properties, QtCore.SIGNAL("triggered()"),
                     self.OnMapProperties)
        self.connect(self.ui.action_Contents, QtCore.SIGNAL("triggered()"),
                     self.OnHelpContents)
        self.connect(self.ui.action_About, QtCore.SIGNAL("triggered()"),
                     self.OnHelpAbout)

        # create the tile choosers
        self.choosermodels = {}
        self.chooserviews = {}

        # first up, the basic tilesets
        tileset = Sprite.GetSpriteSet("tiles")
        tilemodel = TileChooser.TileChooserModel(tileset)
        self.choosermodels["tiles"] = tilemodel
        tileview = TileChooser.TileChooserView(model=tilemodel)
        self.chooserviews["tiles"] = tileview
        
        # set our default tile view
        self.ui.ResourceScroll.setWidget(tileview)

    def OnFileNew(self):
        """
        Called when the menu item File->New is clicked.
        """
        # Pull up the new map dialog
        newDlg = MapWindow.NewMapDialog(self)
        newDlg.show()

    def OnFileOpen(self):
        """
        Called when the menu item File->Open is clicked.
        """
        # TODO: Implement
        pass

    def OnFileSave(self):
        """
        Called when the menu item File->Save is clicked.
        """
        # TODO: Implement
        pass

    def OnFileSaveAs(self):
        """
        Called when the menu item File->Save As... is clicked.
        """
        # TODO: Implement
        pass

    def OnFileClose(self):
        """
        Called when the menu item File->Close is clicked.
        """
        # TODO: Implement
        pass

    def OnEditUndo(self):
        """
        Called when the menu item Edit->Undo is clicked.
        """
        # TODO: Implement
        pass

    def OnEditRedo(self):
        """
        Called when the menu item Edit->Redo is clicked.
        """
        # TODO: Implement
        pass

    def OnEditCopy(self):
        """
        Called when the menu item Edit->Copy is clicked.
        """
        # TODO: Implement
        pass

    def OnEditCut(self):
        """
        Called when the menu item Edit->Cut is clicked.
        """
        # TODO: Implement
        pass

    def OnEditPaste(self):
        """
        Called when the menu item Edit->Paste is clicked.
        """
        # TODO: Implement
        pass

    def OnMapProperties(self):
        """
        Called when the menu item Map->Properties... is clicked.
        """
        # TODO: Implement
        pass

    def OnHelpContents(self):
        """
        Called when the menu item Help->Contents is clicked.
        """
        # TODO: Implement
        pass

    def OnHelpAbout(self):
        """
        Called when the menu item Help->About is clicked.
        """
        # launch the about dialog
        dlg = AboutDialog(self)
        dlg.show()

class AboutDialog(QtGui.QDialog):
    """
    The about dialog for the map editor.
    """

    def __init__(self, parent=None):
        # deal with the original stuff
        super(QtGui.QDialog, self).__init__(parent)

        # now rig the UI
        self.ui = MapEditorAboutUI.Ui_MapEditorAboutDlg()
        self.ui.setupUi(self)
