#! /usr/bin/python

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

from PySide import QtGui
import os
import sys

# i18n constants
I18N_DOMAIN = "xVMapEdit"

if __name__ == "__main__":
    # Try to home in on the client.
    if os.path.exists('sprites'):
        # Client located in the current working directory
        print "Client located in current directory."
    elif os.path.exists(os.path.join('..','xvClient','sprites')):
        # Client located at ../xVClient/sprites
        print "Client located in ../xVClient."
        os.chdir(os.path.join('..','xvClient'))
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
    # Set up internationalization support
    import gettext
    gettext.install(I18N_DOMAIN, "locales/")

from xVMapEdit import EditorWindow
from xVClient import Sprite, ErrorReporting

class MapEditorApp(object):
    """
    Main application class for the map editor.
    """

    # constants
    appname = _("Map Editor")
    """The application name that is shown in the title bar."""

    def __init__(self):
        # initialize some variables
        self.qtapp = None
        """The main Qt application object."""
        self.mainwnd = None
        """Handle to the main window object."""

    def LoadResources(self):
        """
        Loads all resources.
        """
        # Load the sprites.
        try:
            Sprite.LoadAllSprites()
        except Sprite.SpriteLoadFailure as e:
            ErrorReporting.ShowError(e.args[0], ErrorReporting.ERROR_FATAL)
            sys.exit(0)

    def Main(self):
        """
        Called when the application is run.
        """
        # okay, go ahead and engage Qt
        self.qtapp = QtGui.QApplication(sys.argv)

        # load up what we need
        self.LoadResources()

        # and here we go! show the main window!
        self.mainwnd = EditorWindow.MainWindow()
        self.mainwnd.show()

        # let Qt handle the event loop
        retval = self.qtapp.exec_()
        return retval

if __name__ == "__main__":
    # Run the application.
    print "Starting map editor..."
    app = MapEditorApp()
    retcode = app.Main()
    sys.exit(retcode)
