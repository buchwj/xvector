#! /usr/bin/python

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
The main script file for the map editor.

This module includes the main application class for the map editor
as well as the code to begin execution of the map editor.  The
execution code is shielded by an if statement, so it is safe to
import this module from other modules.

The map editor is an unusual component in that it depends on the
client as a library.  This dependency is used to provide the code
to manage the available sprites, and will eventually be used in
a future version to provide a simple built-in map tester in which
the mapper can walk around the map (but without scripts or AIs executing).
"""

from PyQt4 import QtCore, QtGui
import os
import sys
import time

from xVMapEdit import EditorWindow, EditorGlobals, ServerChooser
from xVClient import Sprite, ErrorReporting


class MapEditorApp(object):
    """
    Main application class for the map editor.
    """

    # constants
    appname = "Map Editor"
    """The application name that is shown in the title bar."""

    def __init__(self):
        # initialize some variables
        self.QtApp = None
        """The main Qt application object."""
        
        self.MainWindow = None
        '''Handle to the main window object.'''
        
        self.ResourcesUsed = None
        '''Name of the server whose resources are in use.'''
        
        self.Sprites = None
        '''Handle to the current sprite manager.'''
        
        self.basetime = time.time()
        '''Unix time that the program was started.'''

    def LoadResources(self):
        """
        Loads all resources.
        """
        # What resources are we using?
        chooser = ServerChooser.ServerChooser(parent=None)
        chooser.setModal(True)
        chooser.exec_()
        
        # Load the sprites.
        try:
            self.Sprites = Sprite.SpriteManager(name=self.ResourcesUsed)
        except Sprite.SpriteDirectoryNotFound:
            # bail out
            sys.exit(0)

    def Main(self):
        """
        Called when the application is run.
        """
        # okay, go ahead and engage Qt
        self.QtApp = QtGui.QApplication(sys.argv)
        
        # set up error reporting
        ErrorReporting.ConfigureLogging()

        # load up what we need
        self.LoadResources()

        # and here we go! show the main window!
        self.MainWindow = EditorWindow.MainWindow()
        self.MainWindow.SetupWindow()
        self.MainWindow.show()

        # let Qt handle the event loop
        retval = self.QtApp.exec_()
        return retval
    
    def GetTick(self):
        '''
        Gets the number of milliseconds since the editor started running.
        
        @return: The number of milliseconds since the editor started running
        '''
        return int((time.time() - self.basetime) * 1000)


if __name__ == "__main__":
    # Run the application.
    app = MapEditorApp()
    EditorGlobals.MainApp = app
    retcode = app.Main()
    sys.exit(retcode)
