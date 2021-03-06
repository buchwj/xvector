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
Contains global variables used throughout the different modules.

Also contains some convenience methods for loading resources.
'''

import os.path

MainApp = None
'''Global: Main application object of the editor.'''

##
## Constants
##

ResourceDirName = "res_editor"
'''Name of the folder in which map editor resources are stored.'''


def UIResource(name):
    '''
    Gets the path to the requested UI resource (icons, etc.).
    
    @type name: string
    @param name: Name of the file to get from the resources.
    '''
    return os.path.join(os.path.split(__file__)[0], ResourceDirName, name)
