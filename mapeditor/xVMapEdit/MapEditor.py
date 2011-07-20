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

if __name__ == "__main__":
    # Try to home in on the client.
    if os.path.exists('sprites'):
        # Client located in the current working directory
        print "Client located in current directory."
    elif os.path.exists(os.path.join('..','xVClient','sprites')):
        # Client located at ../xVClient/sprites
        print "Client located in ../xVClient."
        os.chdir(os.path.join('..','xVClient'))
    elif os.path.exists(os.path.join('..','client','sprites')):
        # Client located at ../client/sprites
        print "Client located in ../client."
        os.chdir(os.path.join('..','client'))
    else:
        # Fatal error: client not found.
        # (Hey, at some point, let's add a config option for other locations)
        sys.stderr.write("FATAL ERROR: client not found.")
        sys.exit(-1)
    # Modify the path so that we have access to other engine packages.
    sys.path.append("../")  # TODO: Make this dynamic so it can find where the
                            # client is installed (eg. using registry on
                            # Windows, etc.)


from xVMapEdit import EditorWindow, EditorGlobals
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
        """Handle to the main window object."""
        
        self.animtimer = None
        '''Timer for controlling animation framerates.'''
        
        self.basetime = time.time()
        '''Unix time that the program was started.'''

    def LoadResources(self):
        """
        Loads all resources.
        """
        # Load the sprites.
        try:
            Sprite.LoadAllSprites()
        except Sprite.SpriteLoadFailure as e:
            ErrorReporting.ShowError(e.args[0], ErrorReporting.FatalError)
            sys.exit(0)

    def Main(self):
        """
        Called when the application is run.
        """
        # okay, go ahead and engage Qt
        self.QtApp = QtGui.QApplication(sys.argv)

        # load up what we need
        self.LoadResources()
        
        # set up the animation-control timer
        self.animtimer = QtCore.QTimer()
        self.animtimer.setInterval(25)
        self.animtimer.setSingleShot(False)
        self.QtApp.connect(self.animtimer, QtCore.SIGNAL('timeout()'), self.onAnimPulse)

        # and here we go! show the main window!
        self.MainWindow = EditorWindow.MainWindow()
        self.MainWindow.SetupWindow()
        self.MainWindow.show()
        self.animtimer.start(25)

        # let Qt handle the event loop
        retval = self.QtApp.exec_()
        return retval
    
    def GetTick(self):
        '''
        Gets the number of milliseconds since the editor started running.
        
        @return: The number of milliseconds since the editor started running
        '''
        return int((time.time() - self.basetime) * 1000)
    
    def onAnimPulse(self):
        '''
        Invoked by the animation timer every 25 milliseconds.  Pumps the animation frames.
        '''
        curtick = self.GetTick()
        for type, spriteset in Sprite.spritesets.iteritems():
            spriteset.PumpAnimation(curtick)


if __name__ == "__main__":
    # Run the application.
    print "Starting map editor..."
    app = MapEditorApp()
    EditorGlobals.MainApp = app
    retcode = app.Main()
    sys.exit(retcode)
