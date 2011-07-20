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
Contains code for nicely reporting errors to the user.
"""

import logging
import traceback
from PyQt4 import QtGui
from xVClient import ClientGlobals

mainlog = logging.getLogger("Client.Main")

# Severity constants
FatalError = 1
"""Fatal error, forces termination of application."""

NormalError = 2
"""Normal error, this has impact but does not crash the program."""

WarningError = 3
"""Warning, this does not affect function but should cause concern."""

NoticeError = 4
"""General information."""


def ShowError(message, severity=NormalError, parent=None):
    """
    Displays an error message to the user and waits for a response.
    """
    dlg = QtGui.QMessageBox(parent)
    dlg.setText(message)
    if severity == FatalError:
        dlg.setIcon(QtGui.QMessageBox.Critical)
        dlg.setWindowTitle("Fatal Error")
    elif severity == NormalError:
        dlg.setIcon(QtGui.QMessageBox.Critical)
        dlg.setWindowTitle("Error")
    elif severity == WarningError:
        dlg.setIcon(QtGui.QMessageBox.Warning)
        dlg.setWindowTitle("Warning")
    elif severity == NoticeError:
        dlg.setIcon(QtGui.QMessageBox.Information)
        dlg.setWindowTitle("Notice")
    else:
        dlg.setIcon(QtGui.QMessageBox.NoIcon)
        dlg.setWindowTitle("Message")
    dlg.exec_()


def ShowException(severity=NormalError, start_msg='An error has occurred!', parent=None):
    '''
    Displays the currently-handled exception in an error box.
    '''
    msg = start_msg + "\n\n" + traceback.format_exc()
    ShowError(msg, severity, parent)


class ErrorMessageHandler(logging.Handler):
    '''
    Logging handler that displays messages in Qt message boxes.
    '''
    def __init__(self):
        '''
        Creates a new handler.
        '''
        super(ErrorMessageHandler,self).__init__()
    
    def _ShowError(self, message):
        '''
        Shows an error message and returns immediately.
        
        @type message: string
        @param message: Message to display.
        '''
        app = ClientGlobals.Application
        wnd = QtGui.QMessageBox(parent=app.MainWindow)
        wnd.setIcon(QtGui.QMessageBox.Critical)
        wnd.setWindowTitle("Error")
        wnd.setStandardButtons(QtGui.QMessageBox.Ok)
        wnd.setText(message)
        wnd.show()
    
    def emit(self, record):
        self._ShowError(record.getMessage())

def ConfigureLogging():
    '''
    Configures the logging mechanism to report errors as dialog boxes.
    '''
    # Set up the handler.
    handler = ErrorMessageHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.ERROR)
    mainlog.addHandler(handler)
