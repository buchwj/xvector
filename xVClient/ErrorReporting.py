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
Contains code for nicely reporting errors to the user.
"""

from PyQt4 import QtGui


# Severity constants
ERROR_FATAL = 1
"""Fatal error, forces termination of application."""

ERROR_NORMAL = 2
"""Normal error, this has impact but does not crash the program."""

ERROR_WARNING = 3
"""Warning, this does not affect function but should cause concern."""

ERROR_NOTICE = 4
"""General information."""


def ShowError(message, severity=ERROR_NORMAL, parent=None):
    """
    Displays an error message to the user and waits for a response.
    """
    dlg = QtGui.QMessageBox(parent)
    dlg.setText(message)
    if severity == ERROR_FATAL:
        dlg.setIcon(QtGui.QMessageBox.Critical)
        dlg.setWindowTitle("Fatal Error")
    elif severity == ERROR_NORMAL:
        dlg.setIcon(QtGui.QMessageBox.Critical)
        dlg.setWindowTitle("Error")
    elif severity == ERROR_WARNING:
        dlg.setIcon(QtGui.QMessageBox.Warning)
        dlg.setWindowTitle("Warning")
    elif severity == ERROR_NOTICE:
        dlg.setIcon(QtGui.QMessageBox.Information)
        dlg.setWindowTitle("Notice")
    else:
        dlg.setIcon(QtGui.QMessageBox.NoIcon)
        dlg.setWindowTitle("Message")
    dlg.exec_()
