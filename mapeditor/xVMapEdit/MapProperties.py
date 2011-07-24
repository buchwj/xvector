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
Allows the user to change the map properties.
'''

from PyQt4.QtCore import SIGNAL
from PyQt4 import QtGui

from .ui.MapPropertiesDialogUI import Ui_MapPropertiesDialog

class MapPropertiesDialog(QtGui.QDialog):
    '''
    Allows the user to change the map properties.
    '''
    
    def __init__(self, editor, parent=None):
        '''
        Creates a new Map Properties dialog.
        
        @type editor: MapWindow.EditorWidget
        @param editor: Editor whose map's settings are being modified.
        
        @type parent: QtGui.QWidget
        @param parent: Parent widget of this dialog.
        '''
        # Inherit base class behavior.
        super(MapPropertiesDialog, self).__init__(parent=parent)
        
        # Declare attributes.
        self.Editor = editor
        '''Editor whose map's settings are being modified.'''
        
        # Set up our UI.
        self.ui = Ui_MapPropertiesDialog()
        self.ui.setupUi(self)
        
        # Update the General settings.
        map = self.Editor.map
        self.ui.MapNameEdit.setText(map.MapName)
        self.ui.BackgroundImageEdit.setText(map.BackgroundImage)
        self.ui.NorthBorderEdit.setText(map.NorthMap)
        self.ui.EastBorderEdit.setText(map.EastMap)
        self.ui.SouthBorderEdit.setText(map.SouthMap)
        self.ui.WestBorderEdit.setText(map.WestMap)
        
        # Update the Dimensions settings.
        self.ui.WidthSpin.setValue(map.Width)
        self.ui.HeightSpin.setValue(map.Height)
        self.ui.DepthSpin.setValue(map.Depth)
        self.ui.PlayerDepthSpin.setValue(map.PlayerDepth)
        
        # Connect signals.
        self.connect(self.ui.DepthSpin, SIGNAL("valueChanged(int)"),
                     self.OnDepthChange)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.OnOK)

    def OnDepthChange(self, newdepth):
        '''Called when the Depth option is changed.'''
        self.ui.PlayerDepthSpin.setMaximum(newdepth - 1)
    
    def OnOK(self):
        '''Called when the user clicks OK.'''
        # Store the General settings.
        map = self.Editor.map
        map.MapName = self.ui.MapNameEdit.text()
        map.BackgroundImage = self.ui.BackgroundImageEdit.text()
        map.NorthMap = self.ui.NorthBorderEdit.text()
        map.EastMap = self.ui.EastBorderEdit.text()
        map.SouthMap = self.ui.SouthBorderEdit.text()
        map.WestMap = self.ui.WestBorderEdit.text()
        
        # Store the Dimensions settings.
        width = self.ui.WidthSpin.value()
        height = self.ui.HeightSpin.value()
        depth = self.ui.DepthSpin.value()
        playerdepth = self.ui.PlayerDepthSpin.value()
        if width != map.Width or height != map.Height or depth != map.Depth:
            map.Resize(width, height, depth)
        map.PlayerDepth = playerdepth
        self.Editor.LayerSel.max_depth = depth
        self.Editor.MapWidget.adjustSize()
