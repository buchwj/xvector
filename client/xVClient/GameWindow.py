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

from . import ClientVersion, StartupScreen

class ClientWindow(QtGui.QMainWindow):
    """
    Main window class for the client.
    """
    
    ##
    ## State constants.
    ##
    State_Startup = 0
    '''Initial state which shows the title menu and connection options.'''
    State_Game = 1
    '''In-game state used once connected to a server.'''
    
    StateDisplays = {
                     State_Startup : StartupScreen.StartupScreen,
                     State_Game : None,
                     }
    '''Display widget classes for each state.'''
    
    ##
    ## Hard-coded settings
    ## (Only things that really shouldn't be changed)
    ##
    Resolution = (1024, 768)
    '''Dimensions of the screen.'''

    def __init__(self, parent=None):
        """
        Initializes the client window.
        """
        # Declare our state-tracking attributes.
        self.State = self.State_Startup
        '''Current state of the main display.'''
        self.StateWidget = None
        '''Display widget for the current state.'''
        
        # Set up the basics
        super(ClientWindow,self).__init__(parent)
        self.setWindowTitle(ClientVersion.APP_NAME)
        self.resize(self.Resolution[0], self.Resolution[1])
        self.setMaximumSize(self.Resolution[0], self.Resolution[1])
        self.setMinimumSize(self.Resolution[0], self.Resolution[1])

    def Display(self):
        """
        Displays the window in the appropriate mode (fullscreen or windowed).
        """
        self.show()
        self._ShowState()
    
    def _ShowState(self):
        '''
        Switches the display to the appropriate widget for the current state.
        '''
        # Create the widget and display it.
        self.StateWidget = self.StateDisplays[self.State](parent=self)
        self.setCentralWidget(self.StateWidget)
        self.StateWidget.setVisible(True)
    
    def ChangeState(self, newstate):
        '''
        Changes the current state and updates the display accordingly.
        
        @type newstate: integer
        @param newstate: New state, one of the constants in this class.
        '''
        self.State = newstate
        self._ShowState()
    
    def closeEvent(self, event):
        '''
        Called when the X on the title bar is clicked.
        
        @type event: QtGui.QCloseEvent
        @param event: Close event
        '''
        # Pass it off to the current state widget
        try:
            self.StateWidget.OnClose()
            # If we got here, the widget is handling it... ignore the event so
            # that the widget can complete whatever asynchronous operations it
            # must perform to exit.
            event.ignore()
        except AttributeError:
            # state widget hasn't defined a unique close event, use default
            super(ClientWindow, self).closeEvent(event)

