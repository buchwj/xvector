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
Contains the main window class for the map editor.
"""

from PyQt4 import QtCore, QtGui
from .ui import MapEditorUI, MapEditorAboutUI
from . import TileChooser, MapWindow, EditTools, EditorGlobals
from xVClient import Sprite, ErrorReporting
from xVLib import Maps

class ResourceToggle(object):
    """
    Contains a set of toggle buttons which are used to control which
    type of resource is being manipulated at a given time.
    """
    
    # A few constants...
    ID_Tiles = 1
    """Button ID of the tiles button"""
    ID_Items = 2
    """Button ID of the items button"""
    ID_NPCs = 3
    """Button ID of the NPCs button"""
    
    def __init__(self):
        """
        Initializes a new set of toggle controls for the resources.
        """
        # set up the basics
        mainApp = EditorGlobals.MainApp
        self.MainWindow = mainApp.MainWindow
        
        # create our buttons
        self.ButtonGroup = QtGui.QButtonGroup()
        self.ButtonGroup.setExclusive(True)
        
        self.TileButton = QtGui.QToolButton()
        tile_icon = QtGui.QIcon()
        tile_icon.addPixmap(QtGui.QPixmap(":/ResourceIcons/res/TilesIcon.png"))
        self.TileButton.setIcon(tile_icon)
        self.TileButton.setCheckable(True)
        self.TileButton.setChecked(True)
        self.TileButton.setToolTip("Tiles")
        self.ButtonGroup.addButton(self.TileButton, self.ID_Tiles)
        
        self.ItemButton = QtGui.QToolButton()
        item_icon = QtGui.QIcon()
        item_icon.addPixmap(QtGui.QPixmap(":/ResourceIcons/res/ItemsIcon.png"))
        self.ItemButton.setIcon(item_icon)
        self.ItemButton.setCheckable(True)
        self.ItemButton.setToolTip("Items")
        self.ButtonGroup.addButton(self.ItemButton, self.ID_Items)
        
        self.NPCButton = QtGui.QToolButton()
        npc_icon = QtGui.QIcon()
        npc_icon.addPixmap(QtGui.QPixmap(":/ResourceIcons/res/NPCsIcon.png"))
        self.NPCButton.setIcon(npc_icon)
        self.NPCButton.setCheckable(True)
        self.NPCButton.setToolTip("NPCs")
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
        elif id == self.ID_Items:
            pass    # TODO: Implement
        elif id == self.ID_NPCs:
            pass    # TODO: Implement
        else:
            print "[error] unrecognized resource view", id, "selected"
    
    @property
    def SelectedResource(self):
        '''
        Property method for getting the ID of the selected resource.
        '''
        return self.ButtonGroup.checkedId()
    
    @SelectedResource.setter
    def SelectedResource(self, resource):
        button = self.ButtonGroup.button(resource)
        button.setChecked(True)


class ToolToggle(object):
    '''
    Contains a set of toggle buttons which are used to choose which tool to
    use on the map.
    '''
    
    def __init__(self):
        '''
        Initializes a new tool toggle widget.
        '''
        # Set up the main button group.
        self.buttonGroup = QtGui.QButtonGroup()
        self.buttonGroup.setExclusive(True)
        
        # Selector tool.
        self.SelectorButton = QtGui.QToolButton()
        self.SelectorButton.setCheckable(True)
        self.SelectorButton.setToolTip("Selector")
        self.buttonGroup.addButton(self.SelectorButton, 
                                   EditTools.Toolbox.ID_Selector)
        
        # Pen tool.
        self.PenButton = QtGui.QToolButton()
        self.PenButton.setCheckable(True)
        self.PenButton.setToolTip("Pen")
        self.buttonGroup.addButton(self.PenButton,
                                   EditTools.Toolbox.ID_Pen)
        
        # Rectangle Draw tool.
        self.RectDrawButton = QtGui.QToolButton()
        self.RectDrawButton.setCheckable(True)
        self.RectDrawButton.setToolTip("Rectangle Draw")
        self.buttonGroup.addButton(self.RectDrawButton,
                                   EditTools.Toolbox.ID_RectangleDraw)
        
        # Flood Bucket tool.
        self.FloodButton = QtGui.QToolButton()
        self.FloodButton.setCheckable(True)
        self.FloodButton.setToolTip("Flood Bucket")
        self.buttonGroup.addButton(self.FloodButton,
                                   EditTools.Toolbox.ID_FloodBucket)
        
        # Select the selector tool by default.
        self.SelectorButton.setChecked(True)
    
    def Attach(self, toolbar):
        '''
        Attaches the buttons to a toolbar.
        
        @type toolbar: C{QtGui.QToolBar}
        @param toolbar: Toolbar to attach buttons to.
        '''
        toolbar.addWidget(self.SelectorButton)
        toolbar.addWidget(self.PenButton)
        toolbar.addWidget(self.RectDrawButton)
        toolbar.addWidget(self.FloodButton)
        
    @property
    def currentTool(self):
        '''
        Property method for getting and setting the currently selected tool.
        '''
        return self.buttonGroup.checkedId()

    @currentTool.setter
    def currentTool(self, tool):
        button = self.buttonGroup.button(tool)
        if not button:
            raise IndexError("Requested tool does not exist.")
        button.setChecked(True)


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
        
        # declare our attributes
        self.ui = None
        '''The Qt 4 user interface object.'''
        self.restoggle = None
        '''The resource toggle buttons.'''
        self.Toolbox = None
        '''The main Toolbox object for the editor.'''
        self.toolToggle = None
        '''The toggle buttons for each of the different tools.'''
        self.choosermodels = {}
        '''Sprite chooser models.'''
        self.chooserviews = {}
        '''Sprite chooser views.'''
    
    def SetupWindow(self):
        '''
        Sets up the window UI.
        
        We keep this separate from __init__ since certain parts (the Toolbox)
        need the EditorWindow object to fully exist.
        '''
        # create the UI object and map it to the window
        self.ui = MapEditorUI.Ui_MapEditorWindow()
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
        self.restoggle = ResourceToggle()
        self.restoggle.Attach(self.ui.toolBar)
        
        # create our toolbox
        self.Toolbox = EditTools.Toolbox()
        
        # add the tool toggle
        self.ui.toolBar.addSeparator()
        self.toolToggle = ToolToggle()
        self.toolToggle.Attach(self.ui.toolBar)

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
        # Get the filepath to open
        caption = "Open File"
        filter = "Map Files (*.xvm);;All Files (*.*)"
        filepath = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                     caption=caption,
                                                     filter=filter)
        if not filepath:
            # User clicked cancel, do nothing
            return
        
        # Open the file
        openedMap = Maps.Map()
        try:
            openedMap.LoadMapFromFile(filepath)
            editor = MapWindow.EditorWidget(map=openedMap)
            subwindow = self.ui.mdiArea.addSubWindow(editor)
            subwindow.setWindowTitle(openedMap.header.mapname)
            subwindow.show()
        except:
            # something went wrong, show the error
            message = "An error occurred while opening the map."
            ErrorReporting.ShowException(parent=self, start_msg=message)

    def OnFileSave(self):
        """
        Called when the menu item File->Save is clicked.
        """
        # Which sub-window is active?
        subwindow = self.ui.mdiArea.activeSubWindow()
        if not subwindow:
            # no active subwindow; do nothing
            return
        
        # Call save
        subwindow.widget().onSave()

    def OnFileSaveAs(self):
        """
        Called when the menu item File->Save As... is clicked.
        """
        # Which sub-window is active?
        subwindow = self.ui.mdiArea.activeSubWindow()
        if not subwindow:
            # no active subwindow; do nothing
            return
        
        # Call save as
        subwindow.widget().onSaveAs()

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
        # Which sub-window is active?
        subwindow = self.ui.mdiArea.activeSubWindow()
        if not subwindow:
            # undo clicked, but no active subwindow; do nothing
            return
        
        # Call undo
        subwindow.widget().onUndo()

    def OnEditRedo(self):
        """
        Called when the menu item Edit->Redo is clicked.
        """
        # Which sub-window is active?
        subwindow = self.ui.mdiArea.activeSubWindow()
        if not subwindow:
            # undo clicked, but no active subwindow; do nothing
            return
        
        # Call redo
        subwindow.widget().onRedo()

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
    
    def OnMenuWindow(self):
        '''
        Called right before the Window menu is displayed.
        
        We use this to display the list of MDI subwindows to the user.
        '''
        # Destroy whatever we already have in the Window menu.
        pass    # TODO: Implement

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
        
        # connect the "About Qt..." button
        self.connect(self.ui.btnAboutQt, QtCore.SIGNAL("clicked()"),
                     self.onAboutQt)
    
    def onAboutQt(self):
        """
        Called when the "About Qt..." button is clicked.
        """
        QtGui.QMessageBox.aboutQt(self, "About Qt")
