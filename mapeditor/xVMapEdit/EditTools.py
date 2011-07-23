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

'''
Tool classes (select, draw, flood, etc.), and the undo/redo support classes.

These tools are only for drawing tiles; objects such as NPCs and items are
added with other mechanisms.
'''

from xVMapEdit import EditorGlobals
from PyQt4 import QtCore, QtGui

import copy
import logging
import collections

mainlog = logging.getLogger("")

class ReversibleChange(object):
    '''
    The base class of all modifications which support undo/redo.
    
    This should be subclassed for each type of modification which supports
    the undo and redo features.
    '''
    def __init__(self, editor):
        '''
        Initializes an empty reversible change.
        
        @type map: MapWindow.EditorWidget
        @param map: Editor to which this change applies.
        '''
        self.editor = editor
        '''The editor to which this change applies.'''
    
    def UndoChange(self):
        '''
        Reverses the change to the map.
        
        This must be reimplemented by all subclasses.
        '''
        # not implemented in the base class
        pass
    
    def RedoChange(self):
        '''
        Repeats the change to the map.
        
        This must be reimplemented by all subclasses.
        '''
        # not implemented in the base class
        pass


class NoOperationException(Exception): pass
'''
Raised if a tool is asked to continue an operation when none is in progress.
'''


class Tool(object):
    '''
    The base class of all editor tools.
    
    Each tool should declare a subclass of this.  Tools should also declare
    subclasses of the ReversibleChange class in order to provide undo/redo
    support; the Tool subclasses are expected to provide objects of the
    corresponding ReversibleChange subclass upon completion of an operation. 
    
    Tools are not attached to any specific map; they must be prepared to accept
    any arbitrary map and operate on it.  Tools can expect to only ever process
    a single map at a given time, however; the user must finish using the tool
    on one map before moving to another.
    '''
    def __init__(self):
        '''
        Initializes the tool.
        '''
        # not implemented in the base class
        pass
    
    def BeginOperation(self, editor, startTileCoords):
        '''
        Begins an operation of this tool on the given map at the given point.
        
        This must be reimplemented by all subclasses.
        
        @type editor: xVMapEdit.MapWindow.EditorWidget
        @param editor: Editor on which to operate.
        
        @type startTileCoords: integer tuple
        @param startTileCoords: Tile coordinates of the first point.
        '''
        # not implemented in the base class
        pass
    
    def ContinueOperation(self, nextTileCoords):
        '''
        Continues an operation in progress at the next point.
        
        This must be reimplemented by all subclasses.
        
        @raise NoOperationException: Raised if no operation is in progress.
        
        @type nextTileCoords: integer tuple
        @param nextTileCoords: Tile coordinates of the next point.
        '''
        # not implemented in the base class
        pass
    
    def EndOperation(self):
        '''
        Ends an operation which is already in progress, and returns a
        ReversibleChange object corresponding to the full operation.
        
        This must be reimplemented by all subclasses.
        
        @raise NoOperationException: Raised if no operation is in progress.
        
        @returns: A ReversibleChange object corresponding to the full operation.
        '''
        # not implemented in the base class
        pass


# These constants define the type of map property that was changed by an
# operation.

ChangeType_Tiles = 0
'''Indicates that tiles were modified by a tool.'''


class UnsupportedChangeType(Exception): pass
'''Raised if a change type is not supported by a given operation.'''

# Okay, now that we've defined the base classes, let's define our
# actual tools.


###############################################################################
## TOOL 1: Selector
###############################################################################
## Description:
##   Allows selection of a rectangular section of a map.
##   The starting point and ending point define two opposite corners
##   of the rectangle.
## Undo/Redo Support:
##   Undo: Deselects the region.
##   Redo: Reselects the region.
###############################################################################

class SelectorChange(ReversibleChange):
    '''
    ReversibleChange subclass for the Selector tool.
    '''
    def __init__(self, editor):
        '''
        Starts a new operation record for the Selector tool.
        
        @type editor: MapWindow.EditorWidget
        @param editor: Editor to which this operation was applied.
        '''
        # Inherit any base class behavior
        super(SelectorChange,self).__init__(editor)
        
        # Declare our attributes.
        self.previous_selection = None
        '''
        Previous selection, as a tuple of tuples, e.g. ((0,0),(1,1)).
        Set to None if there was no previous selection.
        '''
        self.new_selection = None
        '''
        New selection, as a tuple of tuples, e.g. ((0,0),(1,1)).
        Set to None if there is no new selection.
        '''
    
    def UndoChange(self):
        '''Reverts the selection.'''
        # Inherit any base class behavior
        super(SelectorChange,self).UndoChange()
        
        # Undo selection.
        self.editor.MapWidget.selection = self.previous_selection
    
    def RedoChange(self):
        '''Repeats the selection.'''
        # Inherit any base class behavior
        super(SelectorChange,self).RedoChange()
        
        # Redo selection.
        self.editor.MapWidget.selection = self.new_selection


class SelectorTool(Tool):
    '''
    Tool subclass for the Selector tool.
    '''
    def __init__(self):
        '''Initializes the selector tool.'''
        # Inherit any base class behavior
        super(SelectorTool,self).__init__()
        
        # declare our attributes
        self.current_editor = None
        '''Editor of the operation currently in progress.'''
        self.initial_pos = None
        '''Initial position of the current operation.'''
        self.latest_pos = None
        '''Latest position of the current operation.'''
        self.change = None
        '''SelectorChange object for the current operation.'''
    
    def BeginOperation(self, editor, startTileCoords):
        '''
        Begins an operation of this tool on the given map at the given point.
        
        @type editor: MapWindow.EditorWidget
        @param editor: Editor on which to operate.
        
        @type startTileCoords: integer tuple
        @param startTileCoords: Tile coordinates of the first point.
        '''
        # Inherit any base class behavior
        super(SelectorTool,self).BeginOperation(editor, startTileCoords)
        
        # Update arguments
        self.current_editor = editor
        self.initial_pos = startTileCoords
        self.latest_pos = startTileCoords
        self.change = SelectorChange(editor)
        self.change.previous_selection = editor.selection
        
        # Show the initial selection in the editor
        selection = (startTileCoords, startTileCoords)
        editor.selection = selection
    
    def ContinueOperation(self, nextTileCoords):
        '''
        Updates the selection to a new point.
        
        @raise NoOperationException: Raised if no operation is in progress.
        
        @type nextTileCoords: integer tuple
        @param nextTileCoords: Tile coordinates of the next point.
        '''
        # Inherit any base class behavior
        super(SelectorTool,self).ContinueOperation(nextTileCoords)
        
        # Check if an operation is in progress
        if not self.current_editor:
            # No operation in progress
            raise NoOperationException("Selector tool not started.")
        
        # Update the selection.
        self.latest_pos = nextTileCoords
        self._UpdateSelection(nextTileCoords)
    
    def EndOperation(self):
        '''
        Ends the selection.
        
        @raise NoOperationException: Raised if no operation is in progress.
        
        @return: A SelectorChange object for the ended operation.
        '''
        # Inherit any base class behavior
        super(SelectorTool,self).EndOperation()
        
        # Check if an operation is in progress
        if not self.current_editor:
            # No operation in progress
            raise NoOperationException("Selector tool not started.")
        
        # End the operation.
        record = self.change
        self.current_editor = None
        self.initial_pos = None
        self.latest_pos = None
        self.change = None
        
        # Hand back the record.
        return record
    
    def _UpdateSelection(self, nextTileCoords):
        '''
        Updates the selection, ensuring that the proper corners of the
        selection are supplied to the editor.
        
        @warning: This method does not check if an operation is in progress.
        
        @type nextTileCoords: integer tuple
        @param nextTileCoords: Tile coordinates of the next point.
        '''
        # Find the corners
        x1, y1 = self.initial_pos
        x2, y2 = nextTileCoords
        ulCorner = (min(x1, x2), min(y1, y2))
        brCorner = (max(x1, x2), max(y1, y2))
        
        # Update the selection.
        newsel = (ulCorner, brCorner)
        self.change.new_selection = newsel
        self.current_editor.selection = newsel


###############################################################################
## TOOL 2: Pen
###############################################################################
## Description:
##   Replaces tiles with the selected map object wherever the tool operates.
## Undo/Redo Support:
##   Undo: Reverts the replaced tiles to their old state.
##   Redo: Updates all operated tiles to the selected tile.
###############################################################################

class PenChange(ReversibleChange):
    '''
    ReversibleChange subclass for the Pen tool.
    '''
    
    def __init__(self, editor):
        '''
        Creates a new record of a Pen operation.
        
        @type editor: MapWindow.EditorWidget
        @param editor: Editor to which this change applies.
        '''
        # Inherit any base class behavior.
        super(PenChange,self).__init__(editor)
        
        # Declare our attributes.
        self.ChangeType = ChangeType_Tiles
        '''Type of map resource that was modified by this operation.'''
        self.Layer = 0
        '''Layer at which this change was made.'''
        self.PreviousState = {}
        '''
        Previous state of the map prior to the change.
        
        This is stored as two dicts, addressable as [x][y].
        '''
        self.NewState = {}
        '''
        New state of the map after the change.
        
        This is stored as two dicts, addressable as [x][y].
        '''
    
    def UndoChange(self):
        '''
        Undoes the Pen operation.
        
        @raise UnsupportedChangeType: Raised if the resource type is not
        recognized.
        '''
        # Walk through the new state.
        for x in range(self.editor.map.Width):
            # Any changes made to this column?
            if x in self.PreviousState:
                for y in range(self.editor.map.Height):
                    # Any changes made to this coordinate?
                    if y in self.PreviousState[x]:
                        # Restore the state.
                        old = self.PreviousState[x][y]
                        # What type of resource are we restoring?
                        if self.ChangeType == ChangeType_Tiles:
                            # Restore tile.
                            target = self.editor.map.tiles
                            target[self.Layer][x][y].tileid = old
                        else:
                            # Unknown type.
                            raise UnsupportedChangeType()
    
    def RedoChange(self):
        '''
        Redoes the Pen operation.
        
        @raise UnsupportedChangeType: Raised if the resource type is not
        recognized.
        '''
        # Walk through the new state.
        for x in range(self.editor.map.Width):
            # Any changes made to this column?
            if x in self.NewState:
                for y in range(self.editor.map.Height):
                    # Any changes made to this coordinate?
                    if y in self.NewState[x]:
                        # Restore the state.
                        new = self.NewState[x][y]
                        # What type of resource are we restoring?
                        if self.ChangeType == ChangeType_Tiles:
                            # Restore tile.
                            target = self.editor.map.tiles
                            target[self.Layer][x][y].tileid = new
                        else:
                            # Unknown type.
                            raise UnsupportedChangeType()


class PenTool(Tool):
    '''
    Tool subclass for the Pen tool.
    '''
    def __init__(self):
        '''Initializes the Pen tool.'''
        # Inherit any base class behavior.
        super(PenTool,self).__init__()
        
        # Declare attributes.
        self.currentEditor = None
        '''Editor that the Pen tool is currently operating on.'''
        self.currentOperation = None
        '''PenChange record of the current operation.'''
        self.currentID = 0
        '''For updating tiles, the tile ID that is being drawn.'''
    
    def BeginOperation(self, editor, startTileCoords):
        '''
        Begins a new Pen operation.
        
        @raise UnsupportedChangeType: Raised if the resource type is not
        recognized.
        
        @type editor: xVMapEdit.MapWindow.EditorWidget
        @param editor: Editor on which to operate.
        
        @type startTileCoords: integer tuple
        @param startTileCoords: Coordinates of the first tile of the operation.
        '''
        # Inherit any base class behavior.
        super(PenTool,self).BeginOperation(editor, startTileCoords)
        
        # Begin filling out the operation record.
        self.currentEditor = editor
        self.currentOperation = PenChange(editor)
        self.currentOperation.Layer = editor.Layer
        
        # What are we modifying?
        MainApp = EditorGlobals.MainApp
        restoggle = MainApp.MainWindow.restoggle
        resource = restoggle.SelectedResource
        if resource == restoggle.ID_Tiles:
            # Editing tiles... replace it
            self.currentOperation.ChangeType = ChangeType_Tiles
            self.currentID = MainApp.MainWindow.choosermodels['tiles'].selected
            self._UpdateTile(startTileCoords)
        else:
            # Unrecognized change type
            raise UnsupportedChangeType("Unknown resource type.")
    
    def ContinueOperation(self, nextTileCoords):
        '''
        Continues an existing operation.
        
        @raise NoOperationException: Raised if no operation is in progress.
        @raise UnsupportedChangeType: Raised if the resource type is not
        recognized.
        
        @type nextTileCoords: integer tuple
        @param nextTileCoords: Coordinates of the next tile of the operation.
        '''
        # Inherit any base class behavior.
        super(PenTool,self).ContinueOperation(nextTileCoords)
        
        # Is there any operation in progress?
        if not self.currentEditor:
            # No, there is not.
            raise NoOperationException("The Pen tool has not been started.")
        
        # What are we modifying?
        if self.currentOperation.ChangeType == ChangeType_Tiles:
            # Editing tiles... replace it
            self._UpdateTile(nextTileCoords)
        else:
            # Unrecognized change type
            raise UnsupportedChangeType("Unknown resource type.")
    
    def EndOperation(self):
        '''
        Ends an existing operation.
        
        @raise NoOperationException: Raised if no operation is in progress.
        
        @return: A PenChange object representing the completed operation.
        '''
        # Is there an operation in progress?
        if not self.currentEditor:
            # No, there is not.
            raise NoOperationException("The Pen tool has not been started.")
        
        # end the operation
        record = self.currentOperation
        self.currentEditor = None
        self.currentID = 0
        self.currentOperation = None
        return record
    
    def _UpdateTile(self, coordinates):
        '''
        Updates the tile with the given coordinates to the given ID, and logs
        the change.
        
        This method is only for modifying tiles.  Other resources must use
        other methods.
        '''
        # validate parameters
        x,y = coordinates
        if x < 0 or y < 0:
            raise IndexError("Coordinates out of bounds.")
        if x >= self.currentEditor.map.Width:
            raise IndexError("Coordinates out of bounds.")
        if y >= self.currentEditor.map.Height:
            raise IndexError("Coordinates out of bounds.")
        if self.currentID < 0:
            raise IndexError("Tile ID must be positive (was %i)." % self.currentID)
        
        # update tile
        map = self.currentEditor.map
        z = self.currentEditor.Layer
        old_id = map.tiles[z][x][y].tileid
        map.tiles[z][x][y].tileid = self.currentID
        
        # log change
        if x not in self.currentOperation.PreviousState:
            self.currentOperation.PreviousState[x] = {}
            self.currentOperation.NewState[x] = {}
        if y not in self.currentOperation.PreviousState[x]:
            self.currentOperation.PreviousState[x][y] = old_id
            self.currentOperation.NewState[x][y] = self.currentID


###############################################################################
## TOOL 3: Rectangle Draw
###############################################################################
## Description:
##   Draws a rectangle of the selected map object.
##   The starting point and ending point define two opposite corners
##   of the rectangle.
## Undo/Redo Support:
##   Undo: Reverts the rectangle to its old state.
##   Redo: Repeats the operation.
###############################################################################

class RectangleDrawChange(ReversibleChange):
    '''
    ReversibleChange subclass for the Rectangle Draw tool.
    
    The current implementation of this has the potential to become memory
    intensive for very large maps; it makes a copy of the entire layer
    upon creation to use as a reference for undo operations.
    '''
    
    def __init__(self, editor):
        # Inherit base class behavior.
        super(RectangleDrawChange, self).__init__(editor)
        
        # Declare attributes.
        self.Layer = 0
        '''Layer to which this operation was applied.'''
        
        self.PreviousState = None
        '''State of the layer prior to the operation.'''
        
        self.TileUsed = 0
        '''ID of the tile used for the operation.'''
        
        self.StartCoords = None
        '''Starting coordinates of the rectangle.'''
        
        self.EndCoords = None
        '''Ending coordinates of the rectangle.'''
    
    def UndoChange(self):
        # Copy the backup of the layer to the editor's map.
        self.editor.map.tiles[self.Layer] = copy.deepcopy(self.PreviousState)
    
    def RedoChange(self):
        # Figure out what we have to update.
        xmin = min(self.StartCoords[0], self.EndCoords[0])
        xmax = max(self.StartCoords[0], self.EndCoords[0])
        ymin = min(self.StartCoords[1], self.EndCoords[1])
        ymax = max(self.StartCoords[1], self.EndCoords[1])
        
        # Update.
        targetlayer = self.editor.map.tiles[self.Layer]
        for x in range(xmin, xmax+1):
            for y in range(ymin, ymax+1):
                targetlayer[x][y].tileid = self.TileUsed


class RectangleDrawTool(Tool):
    '''
    Tool subclass for the Rectangle Draw tool.
    '''
    
    def __init__(self):
        # Inherit base class behavior.
        super(RectangleDrawTool, self).__init__()
        
        # Declare attributes.
        self.CurrentEditor = None
        '''Editor to which changes are currently being made.'''
        self.CurrentOperation = None
        '''Record of the current operation.'''
        self.CurrentTile = 0
        '''Current tile ID to draw.'''
        self.StartCoords = None
        '''Starting coordinates of the operation.'''
        self.LatestCoords = None
        '''Latest coordinates of the operation.'''
        self.PreviousCoords = None
        '''Previous coordinates of the operation.'''
    
    def BeginOperation(self, editor, startTileCoords):
        # Inherit base class behavior.
        super(RectangleDrawTool, self).BeginOperation(editor, startTileCoords)
        
        # Validate input.
        if not editor.map.CoordinatesInBounds(startTileCoords):
            msg = "Coordinates %s out of bounds." % str(startTileCoords)
            mainlog.error(msg)
            raise IndexError(msg)
        
        # Create a new record.
        self.CurrentEditor = editor
        
        self.CurrentOperation = RectangleDrawChange(editor)
        self.CurrentOperation.PreviousState = copy.deepcopy(editor.map.tiles)
        self.CurrentOperation.Layer = editor.Layer
        prevstate = copy.deepcopy(editor.map.tiles[editor.Layer])
        self.CurrentOperation.PreviousState = prevstate
        self.CurrentOperation.StartCoords = startTileCoords
        
        MainApp = EditorGlobals.MainApp
        self.CurrentTile = MainApp.MainWindow.choosermodels['tiles'].selected
        self.CurrentOperation.TileUsed = self.CurrentTile
        
        # Start the operation.
        self.StartCoords = startTileCoords
        self.LatestCoords = startTileCoords
        self.PreviousCoords = None
        self._UpdateMap()
    
    def ContinueOperation(self, nextTileCoords):
        # Make sure there's already an operation in progress.
        if not self.CurrentEditor:
            msg = "RectangleDrawTool.ContinueOperation() called prematurely."
            mainlog.error(msg)
            raise NoOperationException(msg)
        
        # Validate input.
        if not self.CurrentEditor.map.CoordinatesInBounds(nextTileCoords):
            msg = "Coordinates %s out of bounds." % str(nextTileCoords)
            mainlog.error(msg)
            raise IndexError(msg)
        
        # Continue the operation.
        self.PreviousCoords = self.LatestCoords
        self.LatestCoords = nextTileCoords
        self._UpdateMap()
    
    def EndOperation(self):
        # Make sure there's already an operation in progress.
        if not self.CurrentEditor:
            msg = "RectangleDrawTool.EndOperation() called prematurely."
            mainlog.error(msg)
            raise NoOperationException(msg)
        
        # Finalize the record.
        self.CurrentOperation.EndCoords = self.LatestCoords
        record = self.CurrentOperation
        
        # Reset the tool state.
        self.CurrentEditor = None
        self.CurrentOperation = None
        self.CurrentTile = 0
        self.StartCoords = None
        self.PreviousCoords = None
        self.LatestCoords = None
        
        # Hand over the record.
        return record
    
    def _UpdateMap(self):
        '''Updates the map as needed.'''
        # Any previous rectangle needing update?
        z = self.CurrentEditor.Layer
        if self.PreviousCoords:
            # Temporarily reset to original state.
            xmin = min(self.StartCoords[0], self.PreviousCoords[0])
            xmax = max(self.StartCoords[0], self.PreviousCoords[0])
            ymin = min(self.StartCoords[1], self.PreviousCoords[1])
            ymax = max(self.StartCoords[1], self.PreviousCoords[1])
            for x in range(xmin, xmax+1):
                for y in range(ymin, ymax+1):
                    original = self.CurrentOperation.PreviousState[x][y].tileid
                    self.CurrentEditor.map.tiles[z][x][y].tileid = original
        
        # Fill the current record with the selected tile.
        xmin = min(self.StartCoords[0], self.LatestCoords[0])
        xmax = max(self.StartCoords[0], self.LatestCoords[0])
        ymin = min(self.StartCoords[1], self.LatestCoords[1])
        ymax = max(self.StartCoords[1], self.LatestCoords[1])
        for x in range(xmin, xmax+1):
            for y in range(ymin, ymax+1):
                self.CurrentEditor.map.tiles[z][x][y].tileid = self.CurrentTile


###############################################################################
## TOOL 4: Flood Bucket
###############################################################################
## Description:
##   Fills the contiguous region containing the end tile with the selected
##   map object.
## Undo/Redo Support:
##   Undo: Reverts to old state.
##   Redo: Repeats the operation.
###############################################################################

class FloodChange(ReversibleChange):
    '''
    ReversibleChange subclass for the Flood Bucket tool.
    '''
    def __init__(self, editor):
        # Inherit base class behavior.
        super(FloodChange, self).__init__(editor)
        
        # Declare attributes.
        self.Layer = 0
        '''Layer to which this operation was applied.'''
        self.PreviousState = None
        '''State of the layer prior to the operation.'''
        self.NewState = None
        '''State of the layer following the operation.'''
        
    def UndoChange(self):
        # Inherit base class behavior.
        super(FloodChange, self).UndoChange()
        
        # Reverse the change.
        self.editor.map.tiles[self.Layer] = copy.deepcopy(self.PreviousState)
    
    def RedoChange(self):
        # Inherit base class behavior.
        super(FloodChange, self).RedoChange()
        
        # Repeat the change.
        self.editor.map.tiles[self.Layer] = copy.deepcopy(self.NewState)


class FloodTool(Tool):
    '''
    Tool subclass for the Flood Bucket tool.
    
    This is a bit of an odd tool in that we don't actually do anything until
    EndOperation() is called; all we really do is track where the mouse is
    going.  Once the user releases the mouse button, we flood from the point
    that the mouse was released.
    '''
    
    def __init__(self):
        # Inherit base class behavior.
        super(FloodTool, self).__init__()
        
        # Declare attributes.
        self.CurrentEditor = None
        '''Editor to which the current operation is being applied.'''
        self.LatestPoint = None
        '''Last point at which the mouse was located.'''
    
    def BeginOperation(self, editor, startTileCoords):
        # Inherit base class behavior.
        super(FloodTool, self).BeginOperation(editor, startTileCoords)
        
        # Make sure there isn't already an operation in progress.
        if self.CurrentEditor:
            msg = "FloodTool.BeginOperation() called during an operation."
            mainlog.error(msg)
            return
        
        # Validate input.
        if not editor.map.CoordinatesInBounds(startTileCoords):
            msg = "Coordinates (%i, %i) out of bounds." % startTileCoords
            mainlog.error(msg)
            raise IndexError(msg)
        
        # Begin the operation.
        self.CurrentEditor = editor
        self.LatestPoint = startTileCoords
    
    def ContinueOperation(self, nextTileCoords):
        # Inherit base class behavior.
        super(FloodTool, self).ContinueOperation(nextTileCoords)
        
        # Make sure we already have an operation in progress.
        if not self.CurrentEditor:
            msg = "FloodTool.ContinueOperation() called prematurely."
            mainlog.error(msg)
            raise NoOperationException
        
        # Validate input.
        if not self.CurrentEditor.map.CoordinatesInBounds(nextTileCoords):
            msg = "Coordinates (%i, %i) out of bounds." % nextTileCoords
            mainlog.error(msg)
            raise IndexError(msg)
        
        # Continue the operation.
        self.LatestPoint = nextTileCoords
    
    def EndOperation(self):
        # Inherit base class behavior.
        super(FloodTool, self).EndOperation()
        
        # Make sure we already have an operation in progress.
        if not self.CurrentEditor:
            msg = "FloodTool.EndOperation() called prematurely."
            mainlog.error(msg)
            raise NoOperationException
        
        # Gather data on flood.
        MainApp = EditorGlobals.MainApp
        newtype = MainApp.MainWindow.choosermodels['tiles'].selected
        
        z = self.CurrentEditor.Layer
        x, y = self.LatestPoint
        oldtype = self.CurrentEditor.map.tiles[z][x][y].tileid
        
        # Start a record of the operation.
        record = FloodChange(self.CurrentEditor)
        record.PreviousState = copy.deepcopy(self.CurrentEditor.map.tiles[z])
        
        # Commence flood.
        target = self.CurrentEditor.map.tiles[z]
        visited = set()
        to_visit = collections.deque()
        to_visit.append(self.LatestPoint)
        while len(to_visit) > 0:
            # What are we looking at?
            coords = to_visit.pop()
            visited.add(coords)
            curx, cury = coords
            
            # Continue the flood.
            target[curx][cury].tileid = newtype
            neighbors = self._GetNeighbors(coords)
            for next in neighbors:
                # Interested?
                if next in visited: continue
                if not self.CurrentEditor.map.CoordinatesInBounds(next):
                    continue
                if target[next[0]][next[1]].tileid != oldtype: continue
                # Yes, we're interested.
                to_visit.append(next)
        
        # Finish the record.
        record.NewState = copy.deepcopy(self.CurrentEditor.map.tiles[z])
        
        # End the current operation.
        self.CurrentEditor = None
        self.LatestPoint = None
        
        # Hand over the record.
        return record

    def _GetNeighbors(self, coords):
        '''Gets the adjacent (non-diagonal) tiles to the given coordinates.'''
        neighbors = []
        x, y = coords
        neighbors.append((x-1,y))
        neighbors.append((x+1,y))
        neighbors.append((x,y-1))
        neighbors.append((x,y+1))
        return neighbors


###############################################################################
########################## End Tools / Begin Toolbox ##########################
###############################################################################

class NoToolException(Exception): pass
'''Raised when a nonexistant tool is referenced.'''


class Toolbox(dict):
    '''
    Manages all of the available tools.
    
    You should not create objects of this yourself; the only instance should
    exist as a member of the MainWindow class.  Access it through that.
    '''
    
    # Tool IDs
    ID_Selector = 1
    '''Button ID of the Selector tool.'''
    ID_Pen = 2
    '''Button ID of the Pen tool.'''
    ID_RectangleDraw = 3
    '''Button ID of the Rectangle Draw tool.'''
    ID_FloodBucket = 4
    '''Button ID of the Flood Bucket tool.'''
    
    def __init__(self):
        '''
        Initializes all of the tools.
        '''
        # Declare attributes
        mainApp = EditorGlobals.MainApp
        self.MainWindow = mainApp.MainWindow
        '''Handle to the main window of the editor.'''
        
        # Yeah... initialize the tools.
        self[self.ID_Selector] = SelectorTool()
        self[self.ID_Pen] = PenTool()
        self[self.ID_RectangleDraw] = RectangleDrawTool()
        self[self.ID_FloodBucket] = FloodTool()
    
    @property
    def CurrentTool(self):
        '''
        Property that allows quick access to the selected tool.
        
        @raise NoToolException: Raised if a nonexistant tool is selected.
        '''
        # What tool is selected?
        selected = self.MainWindow.toolToggle.currentTool
        if selected not in self:
            msg = "Unknown tool selected with ID %i." % selected
            mainlog.error(msg)
            raise NoToolException("Unknown tool selected.")
        return self[selected]
    
    @property
    def CurrentCursor(self):
        '''
        Property that allows quick access to the cursor for the selected tool.
        
        If a cursor specific to the tool is not found, the arrow cursor will
        be used by default.
        '''
        # What tool is selected?
        selected = self.MainWindow.toolToggle.currentTool
        if selected == self.ID_Selector:
            # Selector tool uses a standard arrow cursor
            return QtGui.QCursor(QtCore.Qt.ArrowCursor)
        elif selected == self.ID_Pen:
            # Pen tool uses the pen cursor
            pass    # TODO: Implement
        elif selected == self.ID_RectangleDraw:
            # Rectangle draw tool uses the rectangle draw cursor
            pass    # TODO: Implement
        elif selected == self.ID_FloodBucket:
            # Flood bucket tool uses the flood bucket cursor
            pass    # TODO: Implement
        
        # If we get here, no cursor is known.  Default to the arrow cursor.
        return QtGui.QCursor(QtCore.Qt.ArrowCursor)
