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

# Do we need to do pre-run configuration?
if __name__ == "__main__":
    # Modify the path so that we have access to other engine packages.
    sys.path.append("../")
    # Set up our working directory
    import os
    import os.path
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    # check that xVLib is installed
    try:
        import xVLib
    except ImportError:
        msg = "FATAL ERROR: xVLib could not be found.\n"
        msg += "Please check that xVLib is installed in the python path.\n"
        sys.stderr.write(msg)
        sys.exit(-1)
    finally:
        del xVLib

from xVClient import GameWindow, ClientConfig, ErrorReporting, ClientPaths
from xVClient import Sprite, ClientGlobals
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
        except ClientConfig.LoadConfigError as e:
            # failed to load config file
            msg = "Error while loading the main options file.\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
            sys.exit(0)

        # create the background processor
        self.BackgroundProcessor = BackgroundProcessor(parent=self.QtApp)

        # set up the application basics
        self.MainWindow = GameWindow.ClientWindow()

        # load needed resources
        Sprite.LoadAllSprites()
        
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
