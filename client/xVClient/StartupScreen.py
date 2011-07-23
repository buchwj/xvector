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

'''
Screen with the title menu, metaserver, and automatic updater.

The startup screen can be thought of as a central hub for the client.  Its
primary role is to allow the player to select a server to connect to, then
prepare the local files for that connection.  Its final step is to hand
off control to the Game screen, the first state of which is the login screen.
'''

import os.path
import logging

from PyQt4 import QtCore, QtGui

from . import ClientPaths, ClientGlobals

mainlog = logging.getLogger("Client.Main")

class StartupScreen(QtGui.QWidget):
    '''
    Game startup screen; handles the title menu, metaserver, and auto-updater.
    '''
    
    ##
    ## Startup state constants
    ##
    StartupState_Title = 1
    '''This state shows the title menu.'''
    StartupState_Metaserver = 2
    '''This state allows a player to choose a server from the list.'''
    StartupState_PrivateServer = 3
    '''This state allows a player to connect to a server by address.'''
    StartupState_Settings = 4
    '''This state allows a player to change the local settings.'''
    StartupState_Updater = 5
    '''This state retrieves updated files from the server.'''
    
    ##
    ## Control constants
    ##
    FramesPerSecond = 30
    '''Framecap for the startup screen.'''
    
    BackgroundFile = "ui/background/startup.png"
    '''Path (relative to the master resource root) of the background.'''
    
    def __init__(self, parent=None):
        '''
        Creates a new startup screen object.
        
        @type parent: QtGui.QWidget
        @param parent: Parent object of the screen (usually the main window)
        '''
        # Inherit base class behavior.
        super(StartupScreen,self).__init__(parent)
        App = ClientGlobals.Application
        
        # Load the background image.
        bkgpath = os.path.join(ClientPaths.BaseMasterPath, self.BackgroundFile)
        try:
            self.BackgroundImage = QtGui.QPixmap.load(bkgpath)
        except:
            msg = "Could not open %s.\n" % bkgpath
            msg += "Defaulting to blank background."
            mainlog.error(msg)
            
            # default to a black background
            x, y = App.MainWindow.Resolution
            self.BackgroundImage = QtGui.QPixmap(x,y)
            self.BackgroundImage.fill(QtCore.Qt.black)
        
        # Start our control timer.
        self.startTimer(1000 // self.FramesPerSecond)
    
    def timerEvent(self, event):
        '''
        Regularly scheduled timer callback.  Controls animation.
        
        In the startup screen, the main purpose of the timer is to control
        smooth fadein and fadeout effects of the various widgets.  This
        timer is called once every 1/30 of a second.
        '''
        pass
