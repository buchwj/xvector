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

import logging
import traceback
from xVLib import Maps
from xVClient import MapRender
from PyQt4 import QtCore, QtGui
from . import EditorGlobals, EditTools
from .ui import NewMapDialogUI

mainlog = logging.getLogger("")

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
        This dialog MUST have a parent (and it MUST act like MainWindow)!
        
        @type MainWindow: xVMapEdit.EditorWindow.MainWindow
        @param MainWindow: The actual main window object.
        
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
        self.uiobj.txtMapName.setFocus()
        
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
        # Validate user input
        name = self.uiobj.txtMapName.text()
        width = self.uiobj.spnWidth.value()
        height = self.uiobj.spnHeight.value()
        depth = self.uiobj.spnDepth.value()
        playerdepth = self.uiobj.playerDepthSpin.value()
        if len(name) < 1:
            # Name cannot be blank
            msg = "The map name cannot be blank."
            mainlog.error(msg)
            return
        if width <= 0 or height <= 0 or depth <= 0:
            # Invalid width/Height
            error = "All dimensions must be positive."
            QtGui.QMessageBox.warning(self, "Error", error)
            return
        
        # Create our new map
        try:
            NewMap = Maps.Map(width, height, depth, playerdepth)
            NewMap.header.MapName = name
        except Exception:
            # fail
            return
        
        # Create the map window
        widget = EditorWidget(parent=self.parent().ui.mdiArea, map=NewMap)
        wnd = self.parent().ui.mdiArea.addSubWindow(widget)
        wnd.setWindowTitle(name)
        wnd.show()
    
    def OnCancel(self):
        """
        Called when the user clicks Cancel.
        """
        # Don't do anything
        pass


class LayerSelector(QtGui.QWidget):
    '''
    Widget that allows the user to select a layer to work with.
    
    This appears at the top of every EditorWidget.
    '''
    
    def __init__(self, parent=None, value=0):
        '''
        Creates a new layer selector widget.
        
        @type value: integer
        @param value: Initial layer to set the slider to
        '''
        # initialize the widget
        super(LayerSelector,self).__init__(parent)
        
        # create the layout
        self.Layout = QtGui.QHBoxLayout()
        self.Layout.setSpacing(0)
        self.Layout.setMargin(0)
        self.setLayout(self.Layout)
        
        # add a dummy stretcher
        self.Layout.addStretch(1)
        
        # create our size policy
        self.SizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                            QtGui.QSizePolicy.Fixed)
        
        # create our widgets
        self.lblCaption = QtGui.QLabel("Layer: ", parent=self)
        self.lblCaption.setSizePolicy(self.SizePolicy)
        self.Layout.addWidget(self.lblCaption)
        self.Layout.setAlignment(self.lblCaption, QtCore.Qt.AlignRight)
        
        self.spnLayer = QtGui.QSpinBox(parent=self)
        self.spnLayer.setMinimum(0)
        self.spnLayer.setMaximum(0)
        self.spnLayer.setValue(value)
        self.spnLayer.setSizePolicy(self.SizePolicy)
        self.Layout.addWidget(self.spnLayer)
        self.Layout.setAlignment(self.spnLayer, QtCore.Qt.AlignRight)
        
        # connect our signals and slots
        self.connect(self.spnLayer, QtCore.SIGNAL("valueChanged(int)"),
                     self.OnLayerChange)
    
    @property
    def layer(self):
        '''
        Property definition for getting and setting the current layer.
        '''
        return self.spnLayer.value()
    
    @layer.setter
    def layer(self, newlayer):
        self.spnLayer.setValue(newlayer)
    
    @property
    def max_depth(self):
        '''
        Property definition for getting and setting the maximum Depth.
        '''
        return self.spnLayer.getMaximum() + 1
    
    @max_depth.setter
    def max_depth(self, max):
        self.spnLayer.setMaximum(max - 1)
    
    def OnLayerChange(self, layer):
        '''
        Called when the user changes the layer using the spin control.
        
        @type layer: integer
        @param layer: User input.
        '''
        # notify the renderer
        self.parent().MapWidget.current_layer = layer


class ActionNotPermittedException(Exception): pass
'''Raised if an action cannot be performed on a given editor.'''


class InvalidSelectionException(Exception): pass
'''Raised if a selection in the map editor is determined to be invalid.'''


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
        
        @type map: xVLib.Maps.Map
        @param map: Map to edit with this, if one already exists.
        
        @type MainWindow: xVMapEdit.EditorWindow.MainWindow
        @param MainWindow: Handle to the MainWindow object.
        """
        # call the parent initializer
        super(EditorWidget, self).__init__(parent)
        
        # declare attributes
        MainApp = EditorGlobals.MainApp
        self.MainWindow = MainApp.MainWindow
        '''Handle to the main window of the editor.'''
        self.UndoStack = []
        '''A stack containing previous (undoable) operations.'''
        self.RedoStack = []
        '''A stack containing the next (redoable) operations.'''
        self.FilePath = None
        '''Path to which this file is saved; None if not yet saved.'''
        self.FileChanged = False
        '''True if changes have been made to the file.'''

        # create the layout
        self.Layout = QtGui.QVBoxLayout()
        self.Layout.setSpacing(0)
        self.Layout.setMargin(0)
        self.setLayout(self.Layout)
        
        # we want all of this stuff to be resizable
        policy_core = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Expanding)
        policy_edge = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Maximum)
        
        # create the layer selector and add it
        self.LayerSel = LayerSelector(parent=self, value=0)
        '''The layer selector widget.'''
        self.LayerSel.max_depth = map.Depth
        self.LayerSel.setSizePolicy(policy_edge)
        self.Layout.addWidget(self.LayerSel)

        # create the scroll area and add it
        self.ScrollArea = QtGui.QScrollArea(parent=self)
        """The scroll area that contains the MapWidget."""
        self.ScrollArea.setSizePolicy(policy_core)
        self.Layout.addWidget(self.ScrollArea)
        
        # create the status bar and add it
        self.StatusBar = QtGui.QStatusBar(parent=self)
        """The status bar of the window."""
        self.StatusBar.setSizePolicy(policy_edge)
        self.Layout.addWidget(self.StatusBar)
        
        self.CoordinateLabel = QtGui.QLabel(parent=self.StatusBar)
        """Shows the coordinates of the moused-over tile."""
        
        self.CoordinateLabel.setText("(0,0)")
        self.StatusBar.addPermanentWidget(self.CoordinateLabel)
        
        # create our map widget and add it
        self.MapWidget = MapEditWidget(self.ScrollArea, map, 
                                       self.CoordinateLabel)
        '''Main editing widget.'''
        self.ScrollArea.setWidget(self.MapWidget)
        
        # fix the tab order
        self.setTabOrder(self.ScrollArea, self.LayerSel)
        
        # set the focus policy
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
    
    def PushUndoOperation(self, change):
        '''
        Pushes an operation onto the undo stack.
        
        Note that this will not inherently clear the redo stack.  This is
        because in the case that an action is redone, it will be pushed onto
        the undo stack, but any future redo actions must still remain on the
        redo stack.
        
        @type change: xVMapEdit.EditTools.ReversibleChange
        @param change: Operation to push onto the undo stack.
        '''
        # push
        self.UndoStack.append(change)
        
        # update
        self.UpdateMenuActions()
    
    def PopUndoOperation(self):
        '''
        Pops an operation off of the undo stack.
        
        Note that this will not inherently push the operation onto the redo
        stack.  You must do this yourself if you want the operation to be
        redoable.
        
        @return: The top operation from the undo stack.
        '''
        # pop
        popped = self.UndoStack.pop()
        
        # update
        self.UpdateMenuActions()
        
        # finish
        return popped
    
    def ClearUndoStack(self):
        '''
        Clears the undo stack.
        '''
        self.UndoStack = []
        self.UpdateMenuActions()
    
    def PushRedoOperation(self, change):
        '''
        Pushes an operation onto the redo stack.
        
        @type change: xVMapEdit.EditTools.ReversibleChange
        @param change: Operation to push onto the redo stack.
        '''
        self.RedoStack.append(change)
        self.UpdateMenuActions()
    
    def PopRedoOperation(self):
        '''
        Pops an operation off of the redo stack.
        
        Note that this will not inherently push the operation onto the undo
        stack.  You must do this yourself if you want the operation to be
        undoable.
        
        @return: The top operation from the redo stack.
        '''
        popped = self.RedoStack.pop()
        self.UpdateMenuActions()
        return popped
    
    def ClearRedoStack(self):
        '''
        Clears the redo stack.
        '''
        self.RedoStack = []
        self.UpdateMenuActions()
    
    def focusInEvent(self, event):
        '''
        Called when this window gains focus.
        
        This is a reimplemented method from Qt 4.  We use it to ensure that
        the menu buttons are properly updated for this window's map when it
        gains focus.
        
        @type event: C{QtGui.QFocusEvent}
        @param event: Focus event from Qt 4.
        '''
        # Update the menu actions.
        self.UpdateMenuActions()
        
        # Let the window do its usual thing.
        super(EditorWidget,self).focusInEvent(event)
    
    def onUndo(self):
        '''
        Called when Undo is clicked when this window is active.
        
        @raise ActionNotPermittedException: Raised if there is nothing to undo.
        '''
        # Is undo even possible?
        if len(self.UndoStack) == 0:
            # Can't undo
            raise ActionNotPermittedException("Nothing to undo.")
        
        # Undo
        change = self.UndoStack.pop()
        change.UndoChange()
        self.PushRedoOperation(change)
        self.MapWidget.update()
    
    def onRedo(self):
        '''
        Called when Redo is clicked when this window is active.
        
        @raise ActionNotPermittedException: Raised if there is nothing to redo.
        '''
        # Is redo even possible?
        if len(self.RedoStack) == 0:
            # Can't redo
            raise ActionNotPermittedException("Nothing to redo.")
        
        # Redo
        change = self.RedoStack.pop()
        change.RedoChange()
        self.PushUndoOperation(change)
        self.MapWidget.update()
    
    def onSave(self):
        '''
        Called when Save is clicked when this window is active.
        '''
        # Has the file been saved yet?
        if not self.FilePath:
            # No, we'll need to "Save As..."
            print "[debug] calling onSaveAs()"
            self.onSaveAs()
            return
        
        # Save the file
        try:
            self.map.SaveMapToFile(self.FilePath)
            self.ClearUndoStack()
            self.ClearRedoStack()
        except:
            # failed, ignore
            pass
    
    def onSaveAs(self):
        '''
        Called when Save As is clicked when this window is active.
        '''
        # Pick a file path.
        print "[debug] in onSaveAs()"
        print traceback.format_list(traceback.extract_stack())
        caption = "Save As..."
        filter = "Map files (*.xvm);;All files (*.*)"
        self.FilePath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                          caption=caption,
                                                          filter=filter)
        if not self.FilePath:
            # No file path selected.
            return
        
        # Okay, we have a file path, now actually save the file
        self.onSave()
    
    def OnSelectAll(self):
        '''
        Called when Select All is clicked when this window is active.
        '''
        # Select everything and make a record of it.
        record = EditTools.SelectorChange(self)
        record.previous_selection = self.selection
        self.selection = ((0,0), (self.map.Width - 1, self.map.Height - 1))
        record.new_selection = self.selection
        self.PushUndoOperation(record)
    
    def OnDeselect(self):
        '''
        Called when Deselect is clicked when this window is active.
        '''
        # Deselect everything and make a record of it.
        record = EditTools.SelectorChange(self)
        record.previous_selection = self.selection
        self.selection = None
        record.new_selection = self.selection
        self.PushUndoOperation(record)
    
    @property
    def selection(self):
        '''
        Property abstraction that allows reference to the selection at the
        editor window level.
        '''
        return self.MapWidget.selection
    
    @selection.setter
    def selection(self, select):
        self.MapWidget.selection = select
        self.UpdateMenuActions()
    
    @property
    def Layer(self):
        '''
        Property method for getting and setting the current layer.
        '''
        return self.LayerSel.layer
    
    @Layer.setter
    def Layer(self, newlayer):
        self.LayerSel.layer = newlayer
    
    @property
    def map(self):
        '''
        Property method for getting the map from this editor.
        '''
        return self.MapWidget.map
    
    @map.setter
    def map(self, newmap):
        self.MapWidget.map = newmap
    
    def UpdateMenuActions(self):
        '''
        Enables and disables the appropriate menu actions for this widget.
        '''
        MainApp = EditorGlobals.MainApp
        
        # Options that are always enabled
        MainApp.MainWindow.ui.action_Select_All.setEnabled(True)
        
        # Undo/Redo
        canUndo = len(self.UndoStack) > 0
        canRedo = len(self.RedoStack) > 0
        MainApp.MainWindow.ui.action_Undo.setEnabled(canUndo)
        MainApp.MainWindow.ui.action_Redo.setEnabled(canRedo)
        
        # Options that need a selection to be made
        hasSelection = bool(self.selection)
        MainApp.MainWindow.ui.action_Copy.setEnabled(hasSelection)
        MainApp.MainWindow.ui.actionC_ut.setEnabled(hasSelection)
        MainApp.MainWindow.ui.action_Paste.setEnabled(hasSelection)
        MainApp.MainWindow.ui.action_Deselect.setEnabled(hasSelection)


class MapEditWidget(QtGui.QWidget):
    """
    Widget that displays a map and allows it to be edited.

    These are almost exclusively used as the contents of the MapWindow
    objects.  In terms of model-view-controller, they can be thought
    of as the corresponding view to a Maps.FullMap model.
    """

    def __init__(self, parent=None, map=None, statusbar=None):
        """
        Initializes the widget.
        
        @type parent: QtGui.QWidget
        @param parent: Parent widget of this object.
        
        @type map: Maps.Map
        @param map: Map to be edited in this widget
        
        @type statusbar: QtGui.QLabel
        @param statusbar: Status bar element to be updated with the position.
        """
        # initialize the widget itself
        super(QtGui.QWidget, self).__init__(parent)

        # set up some attributes
        mainApp = EditorGlobals.MainApp
        self.MainWindow = mainApp.MainWindow
        '''Handle to the main editor window.'''
        self.EditorWindow = self.parent().parent()
        '''Handle to the editor sub-window for this map.'''
        self._map = None
        """Internal handle to the map; access this via object.map instead."""
        self.sbar = statusbar
        '''Status bar element to be updated with cursor position.'''
        self.renderer = MapRender.MapRenderer(mainApp.Sprites)
        '''Renderer object for our map.'''
        self._current_layer = 0
        '''Current layer (used to determine alpha blending in rendering)'''
        self.prev_tile = (-1,-1)
        '''Last tile that mouse hovered over. Used to check tile changes.'''
        self.usingTool = False
        '''Is the user in the process of using a tool?'''
        self.hasSelection = False
        '''Is anything selected?'''
        self.selectionStartCoords = (0,0)
        '''Tile coordinates of the upper-left corner of the selection.'''
        self.selectionEndCoords = (0,0)
        '''Tile coordinates of the bottom-right corner of the selection.'''

        self.map = map
        
        # Enable mouse tracking.
        self.setMouseTracking(True)

    @property
    def current_layer(self):
        '''Property method for getting and setting the current layer.'''
        return self._current_layer
    
    @current_layer.setter
    def current_layer(self, newlayer):
        self._current_layer = newlayer
        self.update()

    @property
    def map(self):
        return self._map
    
    @map.setter
    def map(self, newmap):
        # typecheck
        if not isinstance(newmap,Maps.BaseMap):
            raise TypeError("map must inherit Maps.BaseMap")
        
        # set the new map and inform the renderer
        self._map = newmap
        self.renderer.map = self._map

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
        width = rect.width()
        height = rect.height()
        targetCoords = (rx1, ry1)
        sourceCoords = targetCoords         # 1:1 mapping here
        
        # blank the region
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtCore.Qt.NoPen)
        whiteBrush = QtGui.QBrush(QtCore.Qt.white)
        painter.setBrush(whiteBrush)
        targetRect = QtCore.QRect(rx1, ry1, width, height)
        painter.fillRect(targetRect, whiteBrush)
        painter.end()
        
        # walk through the layers and render
        for z in range(self.map.Depth):
            # layers above the current are rendered with some amount of
            # transparency depending on their distance above the current
            # layer; we determine this amount here.
            distAbove = z - self.current_layer
            if distAbove <= 0: alpha = 255
            else: alpha = 90
            
            # go ahead and render the layer
            self.renderer.RenderLayer(self, targetCoords, sourceCoords, (0,0),
                                      width, height, z, alpha)
        
        # do we need to draw the selection border?
        if self.hasSelection:
            # yes, draw it
            self._DrawSelectionBorder()
    
    def _DrawSelectionBorder(self):
        '''
        Draws the selection border around the selected area.
        
        @raise InvalidSelectionException: Raised if the selection is invalid.
        '''
        # verify that the selection is valid
        startX, startY = self.selectionStartCoords
        endX, endY = self.selectionEndCoords
        if startX < 0 or startY < 0 or endX < 0 or endY < 0 or \
            startX >= self.map.Width or startY >= self.map.Height or \
            endX >= self.map.Width or endY >= self.map.Height:
            # invalid tile coordinates
            raise InvalidSelectionException("Coordinates out of bounds.")
        
        # now check that the selection is top-left and bottom-right corners
        if startX > endX or startY > endY:
            # invalid selection specification
            raise InvalidSelectionException("Corner ordering is invalid.")
        
        # figure out what we're drawing
        pix_startX = startX * Maps.TileWidth
        pix_startY = startY * Maps.TileHeight
        pix_endX = endX * Maps.TileWidth
        pix_endY = endY * Maps.TileHeight
        pix_endX, pix_endY = MapRender.GetTileBR(pix_endX, pix_endY)
        width = pix_endX - pix_startX
        height = pix_endY - pix_startY
        
        # grab a painter and set it up
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtCore.Qt.NoBrush)
        pen = QtGui.QPen(QtCore.Qt.red)
        pen.setWidth(2)
        painter.setPen(pen)
        
        # draw our selection
        targetRect = QtCore.QRect(pix_startX, pix_startY, width, height)
        painter.drawRect(targetRect)
        
        # finish up
        painter.end()
    
    def _RedrawTileSection(self, startCoords, endCoords, border=0):
        '''
        Redraws the requested tiles of the map.
        
        @type startCoords: integer tuple
        @param startCoords: Coordinates of the starting tile.
        
        @type endCoords: integer tuple
        @param endCoords: Coordinates of the ending tile.
        
        @type border: integer
        @param border: Width of the border along the edge to redraw.
        
        @raise IndexError: Raised if the coordinates are out of bounds.
        '''
        # Validate parameters
        tStartX, tStartY = startCoords
        tEndX, tEndY = endCoords
        if tStartX < 0 or tStartY < 0 or tEndX < 0 or tEndY < 0:
            # out of bounds
            raise IndexError("Selection coordinates must be positive.")
        if tStartX >= self.map.Width or tEndX >= self.map.Width:
            # out of bounds
            raise IndexError("Selection coordinates out of bounds.")
        if tStartY >= self.map.Height or tEndY >= self.map.Height:
            # out of bounds
            raise IndexError("Selection coordinates out of bounds.")
        
        # Figure out what we're drawing
        tULX = min(tStartX, tEndX)
        tULY = min(tStartY, tEndY)
        tBRX = max(tStartX, tEndX)
        tBRY = max(tStartY, tEndY)
        pStartX = tULX * Maps.TileWidth - border
        pStartY = tULY * Maps.TileHeight - border
        pEndX = tBRX * Maps.TileWidth
        pEndY = tBRY * Maps.TileHeight
        pEndX, pEndY = MapRender.GetTileBR(pEndX, pEndY)
        width = pEndX - pStartX + border
        height = pEndY - pStartY + border
        
        # Redraw
        self.update(pStartX, pStartY, width, height)
        
    def sizeHint(self):
        """
        Calculates the size of the full widget.
        
        This finds the size of the <i>entire</i> widget, not just the
        portion visible in the scroll window.
        
        @returns: A C{QtCore.QSize} object containing the size of the widget.
        """
        width = self.map.Width * Maps.TileWidth
        height = self.map.Height * Maps.TileHeight
        return QtCore.QSize(width, height)
    
    def mouseMoveEvent(self, event):
        '''
        Called when the mouse is moved.
        
        This is a reimplemented function from Qt 4's QWidget class.
        We use it to update the status bar's position tracker.
        
        @type event: C{QtGui.QMouseEvent}
        @param event: Mouse movement event from Qt
        '''
        # Where is the mouse currently located?
        point = event.pos()
        x = point.x()
        y = point.y()
        curtile = self.renderer.GetTileMajorXY(x, y)
        curtile = self._ReboundCoordinates(curtile)
        tileX, tileY = curtile
        
        # Has the mouse moved onto a new tile?
        tileChanged = False
        if curtile != self.prev_tile:
            # We're on a new tile
            tileChanged = True
            
            # Update the status bar.
            try:
                text = "(" + str(tileX) + "," + str(tileY) + ")"
                self.sbar.setText(text)
            except:
                # Looks like the status bar doesn't exist. Don't bother.
                pass
        
        # Is the left mouse button being held down?
        if event.buttons() & QtCore.Qt.LeftButton:
            # Left button held down. Do we need to use the tool?
            if tileChanged:
                # But hold on.  Are we even using a tool?
                if self.usingTool:
                    # Alright, go ahead and use the tool.
                    try:
                        currentTool = self.MainWindow.Toolbox.CurrentTool
                        currentTool.ContinueOperation(curtile)
                        self.update()
                    except:
                        # Show a warning.
                        msg = "Unhandled exception in mouseMoveEvent().\n"
                        msg += traceback.format_exc()
                        mainlog.warning(msg)
        
        # Processing complete, update the previous tile tracker
        if tileChanged:
            self.prev_tile = curtile
        
        # Let the widget do its usual thing with the mouse.
        super(MapEditWidget,self).mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        '''
        Called when a mouse button is first pressed.
        
        This is a reimplemented function from Qt 4's QWidget class.
        We use it to start using tools when the user clicks stuff.
        
        @type event: C{QtGui.QMouseEvent}
        @param event: Mouse press event from Qt
        '''
        # Was the mouse press the left button?
        if event.button() == QtCore.Qt.LeftButton:
            # Where is the mouse currently located?
            point = event.pos()
            x = point.x()
            y = point.y()
            curtile = self.renderer.GetTileMajorXY(x, y)
            
            # Start using the tool.
            try:
                currentTool = self.MainWindow.Toolbox.CurrentTool
                currentTool.BeginOperation(self.EditorWindow, curtile)
                self.update()
                self.usingTool = True
            except:
                # Show a warning.
                msg = "Unhandled exception in mousePressEvent().\n"
                msg += traceback.format_exc()
                mainlog.warning(msg)
        
        # Let the widget do its usual thing with the mouse.
        super(MapEditWidget,self).mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        '''
        Called when a mouse button is released.
        
        This is a reimplemented function from Qt 4's QWidget class.
        We use it to finish using tools when the user releases the mouse.
        
        @type event: C{QtGui.QMouseEvent}
        @param event: Mouse press event from Qt
        '''
        # Was the released button the left button?
        if event.button() == QtCore.Qt.LeftButton:
            try:
                # Finish using the tool.
                currentTool = self.MainWindow.Toolbox.CurrentTool
                change = currentTool.EndOperation()
                self.update()
                self.usingTool = False
                
                # Push the operation onto the undo stack, clear the redo stack.
                self.EditorWindow.PushUndoOperation(change)
                self.EditorWindow.ClearRedoStack()
                
            except:
                # Show a warning.
                msg = "Unhandled exception in mouseReleaseEvent().\n"
                msg += traceback.format_exc()
                mainlog.warning(msg)
        
        # Let the widget do its usual thing with the mouse.
        super(MapEditWidget,self).mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        '''
        Called when the mouse enters the widget.
        
        This is a reimplemented function from Qt 4's QWidget class.
        We use it to set the correct cursor for the tool being used.
        
        @type event: C{QtCore.QEvent}
        @param event: Enter event from Qt
        '''
        # Grab the correct cursor
        cursor = self.MainWindow.Toolbox.CurrentCursor
        self.setCursor(cursor)
    
    def _ReboundCoordinates(self, coords):
        '''
        Rebounds coordinates to ensure that they are inside of the map.
        
        @return: Tuple containing the rebounded coordinates.
        '''
        x = coords[0]
        y = coords[1]
        if x < 0: x = 0
        if x >= self.map.Width: x = self.map.Width - 1
        if y < 0: y = 0
        if y >= self.map.Height: y = self.map.Height - 1
        return (x,y)
    
    @property
    def selection(self):
        '''
        Allows setting and getting the selection as a tuple pair of the form
        ((x1,y1),(x2,y2)).  Returns None if there is no selection, and will
        deselect the current selection if set to None.
        ''' 
        if not self.hasSelection:
            return None
        return (self.selectionStartCoords, self.selectionEndCoords)
    
    @selection.setter
    def selection(self, newsel):
        # What did we have before?
        hadSelection = self.hasSelection
        if hadSelection:
            oldSC = self.selectionStartCoords
            oldEC = self.selectionEndCoords
        
        # Do we have a new selection?
        if not newsel:
            self.hasSelection = False
        
        # Update selection.
        if newsel:
            self.selectionStartCoords = self._ReboundCoordinates(newsel[0])
            self.selectionEndCoords = self._ReboundCoordinates(newsel[1])
            self.hasSelection = True
        
        # Do we need to clear the old selection on screen?
        if hadSelection:
            self._RedrawTileSection(oldSC, oldEC, 2)
        
        # Draw the new selection on screen.
        if newsel:
            self._RedrawTileSection(newsel[0], newsel[1], 2)
