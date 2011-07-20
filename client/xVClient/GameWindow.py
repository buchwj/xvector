# xVector Engine Client
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

from PyQt4 import QtGui

from . import GameRenderer, ClientConfig, ClientVersion

# auto-generated UI classes
from .ui import TitleWidgetUI, LoginWidgetUI, ConnectWidgetUI
from .ui import MetaserverWidgetUI

class ClientWindow(QtGui.QMainWindow):
    """
    Main window class for the client.
    """
    
    ##
    ## State constants.
    ##
    State_Intermediate = 0
    State_Preconnect = 1
    State_Connecting = 2
    State_Login = 3
    State_Game = 4

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
        fullscreen = False
        try:
            if config.GetBoolOption("fullscreen"):
                # fullscreen mode
                print "Running in fullscreen mode."
                fullscreen = True
            else:
                # windowed mode
                print "Running in windowed mode."
                fullscreen = False
        except:
            # windowed mode
            print "Running in windowed mode."
            fullscreen = False
        finally:
            if fullscreen:
                self.showFullScreen()
            else:
                self.show()