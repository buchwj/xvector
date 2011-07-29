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
import traceback
import sys
import time

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL

from . import ClientPaths, ClientGlobals, Metaserver, ClientNetworking
from .ui.TitleWidgetUI import Ui_TitleWidget
from .ui.PrivateServerWidgetUI import Ui_PrivateServerWidget

mainlog = logging.getLogger("Client.Main")

class TitleMenu(QtGui.QWidget):
    '''Widget that displays the title menu.'''
    
    def __init__(self, parent=None):
        '''
        Sets up the title menu widget.
        
        @type parent: QtGui.QWidget
        @param parent: Parent widget.
        '''
        # Inherit base class behavior.
        super(TitleMenu, self).__init__(parent=parent)
        
        # Set up our UI.
        self.ui = Ui_TitleWidget()
        '''Automatically-generated user interface object.'''
        self.ui.setupUi(self)
        
        # Connect buttons.
        self.connect(self.ui.btnPublic, SIGNAL("clicked()"),
                     self.OnPublicServer)
        self.connect(self.ui.btnPrivate, SIGNAL("clicked()"),
                     self.OnPrivateServer)
        self.connect(self.ui.btnSettings, SIGNAL("clicked()"),
                     self.OnSettings)
        self.connect(self.ui.btnExit, SIGNAL("clicked()"),
                     self.OnExit)
    
    def OnPublicServer(self):
        '''Called when the "Public Servers" button is clicked.'''
        # Notify the main widget.
        self.parent().OnPublicServer()
    
    def OnPrivateServer(self):
        '''Called when the "Private Servers" button is clicked.'''
        # Notify the main widget.
        self.parent().OnPrivateServer()
    
    def OnSettings(self):
        '''Called when the "Settings" button is clicked.'''
        pass    # TODO: Implement
    
    def OnExit(self):
        '''Called when the "Exit" button is clicked.'''
        self.parent().OnClose()
    
    def paintEvent(self, event):
        '''
        Called from Qt when the widget is redrawn.
        
        @type event: QtGui.QPaintEvent
        @param event: Paint event.
        '''
        # Enable stylesheets on this widget.
        opt = QtGui.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt,
                                   painter, self)


class PrivateServerWidget(QtGui.QWidget):
    '''
    Widget that allows the user to connect to a private server by address.
    '''
    
    def __init__(self, parent=None):
        '''
        Creates a new private server widget.
        '''
        # Inherit base class behavior.
        super(PrivateServerWidget, self).__init__(parent)
        
        # Set up UI.
        self.ui = Ui_PrivateServerWidget()
        '''Automatically-generated user interface object.'''
        self.ui.setupUi(self)
        
        # Create our validators.
        self.PortValidator = QtGui.QIntValidator(1, 65535, self)
        '''Port number validator.'''
        self.ui.PortEdit.setValidator(self.PortValidator)
        
        # Connect buttons to their callbacks.
        self.connect(self.ui.ConnectButton, SIGNAL("clicked()"),
                     self.OnConnect)
        self.connect(self.ui.BackButton, SIGNAL("clicked()"), self.OnBack)
    
    def OnConnect(self):
        '''Called when the Connect button is clicked.'''
        # Validate user input.
        host = self.ui.HostEdit.text()
        if host == "":
            msg = "Host must not be empty."
            mainlog.error(msg)
            return
        try:
            port = int(self.ui.PortEdit.text())
            if port < 1 or port > 65535: raise Exception
        except:
            # Port must be an integer.
            msg = "Port must be a number between 1 and 65535."
            mainlog.error(msg)
            return
        
        # Connect.
        address = (host, port)
        self.parent().ConnectToServer(address)
    
    def OnBack(self):
        '''Called when the Back button is clicked.'''
        self.parent().BackToMain()
    
    def paintEvent(self, event):
        '''
        Called from Qt when the widget is redrawn.
        
        @type event: QtGui.QPaintEvent
        @param event: Paint event.
        '''
        # Enable stylesheets on this widget.
        opt = QtGui.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt,
                                   painter, self)


class StartupScreen(QtGui.QWidget):
    '''
    Game startup screen; handles the title menu, metaserver, and auto-updater.
    '''
    
    ##
    ## Startup state constants
    ##
    StartupState_None = 0
    '''This state shows nothing.'''
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
    FadeTime = 1.0
    '''Time, in seconds, of the fade effect.'''
    
    BackgroundFile = os.path.join("ui", "backgrounds", "startup.png")
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
        
        # Declare attributes which will hold our widgets.
        self.TitleMenu = None
        '''The TitleMenu widget to display.'''
        self.PublicServersMenu = None
        '''The public servers menu to display.'''
        self.PrivateServersMenu = None
        '''The private servers menu to display.'''
        self.SettingsScreen = None
        '''The settings screen to display.'''
        
        # Create our layout.
        self.Layout = QtGui.QVBoxLayout()
        '''Main layout of the startup screen.'''
        self.setLayout(self.Layout)
        
        # Set our initial state.
        self.State = self.StartupState_Title
        '''Current state of the startup screen.'''
        self.FadeIn = True
        '''Whether or not we are fading in.'''
        self.FadeOut = False
        '''Whether or not we are fading out.'''
        self.FadeAlpha = 0.0
        '''Alpha of the widget; used for fading effects.'''
        self.FadeBrush = QtGui.QBrush(QtCore.Qt.black)
        '''Brush used to draw the fade effect.'''
        self.OnFadeComplete = None
        '''Callback for when the current fade operation is complete.'''
        self.LastFrame = 0
        '''Time of the last rendered frame.  Used for animation.'''
        
        # Load the background image.
        bkgpath = os.path.join(ClientPaths.BaseMasterPath, self.BackgroundFile)
        try:
            self.BackgroundImage = QtGui.QPixmap(bkgpath)
            '''Image shown in the background of the startup screen.'''
        except:
            msg = "Could not open %s.\n" % bkgpath
            msg += "Defaulting to blank background.\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
            
            # default to a black background
            x, y = App.MainWindow.Resolution
            self.BackgroundImage = QtGui.QPixmap(x,y)
            self.BackgroundImage.fill(QtCore.Qt.black)
        
        # Start our control timer.
        self.LastFrame = time.time()
        self.startTimer(1000 // self.FramesPerSecond)

        # Get everything going with a fade-in to the title menu.
        self.StartFadein(self._AfterInitialFadein)
    
    def StartFadeout(self, callback_when_done=None):
        '''
        Starts a fade-out effect.
        
        @type callback_when_done: Callable object.
        @param callback_when_done: Callback to call when the fade is complete.
        '''
        self.FadeOut = True
        self.FadeIn = False
        self.FadeAlpha = 1.0
        self.OnFadeComplete = callback_when_done
    
    def StartFadein(self, callback_when_done=None):
        '''
        Starts a fade-in effect.
        
        @type callback_when_done: Callable object.
        @param callback_when_done: Callback to call when the fade is complete.
        '''
        self.FadeOut = False
        self.FadeIn = True
        self.FadeAlpha = 0.0
        self.OnFadeComplete = callback_when_done
    
    def timerEvent(self, event):
        '''
        Regularly scheduled timer callback.  Controls animation.
        
        In the startup screen, the main purpose of the timer is to control
        smooth fadein and fadeout effects of the various widgets.  This
        timer is called once every 1/30 of a second.
        '''
        # Compute time delta.
        now = time.time()
        delta = now - self.LastFrame
        
        # Process fade effects.
        if self.FadeIn:
            self.FadeAlpha += 1.0 * (delta / self.FadeTime)
            if self.FadeAlpha > 1.0:
                # Fade complete.
                self.FadeAlpha = 1.0
                self.repaint()
                self.FadeIn = False
                
                # Any callbacks to call?
                if self.OnFadeComplete:
                    self.OnFadeComplete()
            else:
                self.repaint()
        elif self.FadeOut:
            self.FadeAlpha -= 1.0 * (delta / self.FadeTime)
            if self.FadeAlpha < 0.0:
                # Fade complete.
                self.FadeAlpha = 0.0
                self.repaint()
                self.FadeOut = False
                
                # Any callbacks to call?
                if self.OnFadeComplete:
                    self.OnFadeComplete()
            else:
                self.repaint()
        
        self.LastFrame = now
    
    def paintEvent(self, event):
        '''
        Called when the screen needs to be repainted.
        '''
        # Get a painter.
        painter = QtGui.QPainter()
        painter.begin(self)
        
        # Clear to black.
        App = ClientGlobals.Application
        res_x, res_y = App.MainWindow.Resolution
        target = QtCore.QRect(0, 0, res_x, res_y)
        painter.fillRect(target, QtCore.Qt.black)
        
        # Draw the background, faded as needed.
        painter.save()
        FadeBrush = QtGui.QBrush(QtGui.QColor(0,0,0,255-255*self.FadeAlpha))
        painter.drawPixmap(0, 0, self.BackgroundImage)
        painter.fillRect(target, FadeBrush)
        painter.restore()
        
        # Finish up.
        painter.end()
    
    def ChangeWidget(self, widget=None):
        '''
        Changes the displayed widget.
        
        @type widget: QtGui.QWidget
        @param widget: New widget to display, or None for no widget.
        '''
        # Is there already a widget there?
        if self.Layout.count() == 1:
            # Yes, remove it.
            old = self.Layout.itemAt(0)
            old.widget().setVisible(False)
            self.Layout.removeItem(old)
        
        # Add the new widget if needed.
        if widget:
            self.Layout.addWidget(widget)
            alignment = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            self.Layout.setAlignment(widget, alignment)
            widget.setVisible(True)
    
    def _AfterInitialFadein(self):
        '''
        Called after the initial fade-in operation is completed.
        '''
        # Create the title menu and display it.
        self.TitleMenu = TitleMenu(parent=self)
        self.ChangeWidget(self.TitleMenu)
    
    def OnPublicServer(self):
        '''
        Called when "Connect to Public Server" is clicked on the title menu.
        '''
        # Create the metaserver widget and display it.
        self.PublicServersMenu = Metaserver.MetaserverWidget(parent=self)
        self.ChangeWidget(self.PublicServersMenu)
    
    def OnPrivateServer(self):
        '''
        Called when "Connect to Private Server" is clicked on the title menu.
        '''
        # Create the private server widget and display it.
        self.PrivateServersMenu = PrivateServerWidget(parent=self)
        self.ChangeWidget(self.PrivateServersMenu)
    
    def BackToMain(self):
        '''
        Switches back to the title menu widget.
        '''
        self.ChangeWidget(self.TitleMenu)
    
    def ConnectToServer(self, address):
        '''
        Tries to connect to a server at the given address.
        
        @type address: tuple
        @param address: Network address of the server as a tuple (host, port)
        '''
        # Try to connect.
        try:
            ClientNetworking.ConnectToServer(address)
        except ClientNetworking.ConnectionFailed:
            return
        
        # Disappear the current widget.
        self.ChangeWidget(None)
    
    def OnClose(self):
        '''
        Called when the client must exit.
        '''
        self.ChangeWidget(None)
        self.StartFadeout(sys.exit)
