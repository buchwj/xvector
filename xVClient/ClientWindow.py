# xVector Engine Client
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

from PySide import QtGui

from xVClient import GameRenderer
from xVClient import ClientConfig
from xVClient import ClientVersion

class ClientWindow(QtGui.QMainWindow):
    """
    Main window class for the client.
    """

    def __init__(self, parent=None):
        """
        Initializes the client window.
        """
        # Set up the basics
        super(ClientWindow,self).__init__(parent)
        self.setWindowTitle(ClientVersion.APP_NAME)
        self.resize(800,600)
        self.setMaximumSize(800,600)
        self.setMinimumSize(800,600)
        
        # Create our main rendering system
        self.renderer = GameRenderer.GameRenderer(self)
        """The widget which renders and displays the game to the user."""
        
        self.setCentralWidget(self.renderer)

    def Display(self):
        """
        Displays the window in the appropriate mode (fullscreen or windowed).
        """
        # do we want fullscreen?
        config = ClientConfig.GetConfig()
        if config.GetBoolOption("fullscreen"):
            # fullscreen mode
            print "Running in fullscreen mode."
            self.showFullScreen()
        else:
            # windowed mode
            print "Running in windowed mode."
            self.show()
