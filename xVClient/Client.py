#!/usr/bin/python
#
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

"""
Main script for the client.
"""

from PyQt4 import QtGui
import sys

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

from xVClient import ClientWindow
from xVClient import ClientConfig
from xVClient import ErrorReporting
from xVClient import ClientPaths
from xVClient import Sprite

class ClientApplication(object):
    """
    Parent application class for the client.
    """

    def __init__(self):
        # initialize members to default values
        self.qtapp = None
        self.mainwnd = None
        self.timer = None

    def Main(self):
        """
        Executes the application and returns an exit code.
        """
        # quickly load in the Qt basics for error reporting
        self.qtapp = QtGui.QApplication(sys.argv)
        
        # prepare data directories
        ClientPaths.CreateUserDataDir()

        # load the main configuration
        try:
            ClientConfig.LoadConfig()
        except ClientConfig.LoadConfigError as e:
            # failed to load config file
            msg = "Failed to load the options file.\n\n"
            msg += "Details:\n" + str(e.args[0])
            ErrorReporting.ShowError(msg, ErrorReporting.FatalError)
            sys.exit(0)

        # set up the application basics
        self.mainwnd = ClientWindow.ClientWindow()

        # load needed resources
        Sprite.LoadAllSprites()

        # run the application
        self.mainwnd.Display()
        retval = self.qtapp.exec_()

        # all done
        return retval
    
    def GetQtApp(self):
        """
        Returns a handle to the Qt application object.
        """
        return self.qtapp

    def GetMainWindow(self):
        """
        Returns a handle to the main window.
        """
        return self.mainwnd

    def GetTimer(self):
        """
        Returns a handle to the main timer.
        """
        return self.timer

# If the script is executed directly, create an instance
# of the application and launch it.  We have to include
# this if statement because this module is imported
# elsewhere in the code to use the functions defined above.
if __name__ == "__main__":
    superapp = ClientApplication()
    retcode = superapp.Main()
    sys.exit(retcode)
