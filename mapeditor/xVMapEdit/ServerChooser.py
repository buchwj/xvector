# xVector Engine Map Editor
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
Allows the user to select which server's resources to work with.
'''

import os.path
from PyQt4 import QtCore, QtGui
from xVClient import ClientPaths
from . import EditorGlobals
from .ui import ServerChooserUI

class ServerChooser(QtGui.QDialog):
    '''
    Allows the user to choose which server's resources to work with.
    '''
    
    ##
    ## Constants
    ##
    DefaultResourcesName = "[[ Default Resources ]]"
    
    def __init__(self, parent=None):
        '''
        Creates a new ServerChooser object.
        
        @type parent: QtGui.QWidget
        @param parent: Parent widget of the dialog.
        '''
        # Inherit base class behavior.
        super(ServerChooser, self).__init__(parent)
        
        # Load the UI for the chooser menu.
        self.ui = ServerChooserUI.Ui_ServerChooserDialog()
        self.ui.setupUi(self)
        
        # Scan for resources and create our list model.
        self.ResourceList = self.FindResourceDirs()
        strlist = QtCore.QStringList()
        for server in self.ResourceList: strlist.append(server)
        self.ListModel = QtGui.QStringListModel(strlist)
        self.ui.ResourcesList.setModel(self.ListModel)
        
        # Connect the buttons.
        self.connect(self.ui.buttonOK, QtCore.SIGNAL("accepted()"),
                     self.OnOK)
    
    def FindResourceDirs(self):
        '''
        Scans the system for resource directories to use.
        
        @return: A list of server names whose resources can be used.
        '''
        # We can always use the default resources.
        ResourceList = [self.DefaultResourcesName]
        
        # Does the servers folder even exist?
        targetdir = os.path.join(ClientPaths.BaseUserPath,
                                 ClientPaths.ServersPrefix)
        if not os.path.isdir(targetdir):
            # No servers found.
            return ResourceList
        
        # Scan the servers folder.
        for candidate in os.listdir(targetdir):
            # Is this a directory?
            if os.path.isdir(candidate):
                # Add it!
                ResourceList.append(candidate)
        
        # All done!
        return ResourceList
    
    def OnOK(self):
        '''Signal from Qt that the user has clicked OK.'''
        # Which resources were selected?
        selected = self.ui.ResourcesList.selectedIndexes()[0].data()
        if selected == self.DefaultResourcesName:
            # "None" is understood to mean the default resource set
            selected = None
        
        # Inform the app of the choice.
        App = EditorGlobals.MainApp
        App.ResourcesUsed = selected
