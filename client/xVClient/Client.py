#!/usr/bin/env python
#
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

"""
Main script for the client.
"""

from PyQt4 import QtGui
import traceback
import logging
import sys

mainlog = logging.getLogger("Client.Main")

from xVClient import GameWindow, ClientConfig, ErrorReporting, ClientPaths
from xVClient import ClientGlobals
from xVClient.BackgroundProcessing import BackgroundProcessor

class ClientApplication(object):
    """
    Parent application class for the client.
    """

    def __init__(self):
        # initialize members to default values
        self.QtApp = None
        '''Main Qt application object for the client.'''
        self.MainWindow = None
        '''Main window of the client.'''
        self.BackgroundProcessor = None
        '''Background task processor.'''
    
    def LoadDefaultTheme(self):
        '''
        Loads the default theme, replacing the current theme.
        
        If the stylesheet for the default theme cannot be opened, the client
        will simply fall back on using the system theme.
        '''
        # open the theme
        try:
            themefile = open(ClientPaths.DefaultStyleSheet, "r")
            stylesheet = themefile.read()
            self.QtApp.setStyleSheet(stylesheet)
        except IOError:
            msg = "Could not read default stylesheet, using system theme."
            mainlog.warning(msg)
        finally:
            themefile.close()

    def Main(self):
        """
        Executes the application and returns an exit code.
        """
        # quickly load in the Qt basics for error reporting
        self.QtApp = QtGui.QApplication(sys.argv)
        
        # set up error reporting
        ErrorReporting.ConfigureLogging()
        
        # prepare data directories
        ClientPaths.CreateUserDataDir()

        # load the main configuration
        try:
            ClientConfig.LoadConfig()
        except ClientConfig.LoadConfigError:
            # failed to load config file
            msg = "Error while loading the main options file.\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
            sys.exit(0)
        
        # load the default theme
        self.LoadDefaultTheme()

        # create the background processor
        self.BackgroundProcessor = BackgroundProcessor(parent=self.QtApp)

        # set up the application basics
        self.MainWindow = GameWindow.ClientWindow()
        
        # test the error reporting
        mainlog.error("Test error message.")

        # run the application
        self.MainWindow.Display()
        retval = self.QtApp.exec_()

        # all done
        return retval


if __name__ == "__main__":
    superapp = ClientApplication()
    ClientGlobals.Application = superapp
    retcode = superapp.Main()
    sys.exit(retcode)
