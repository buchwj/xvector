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
Contains functions that find the engine's needed filepaths.
"""

import os
import re
from xVLib import Directories

# constants
BaseUserPath = os.path.join(os.path.expanduser("~"), ".xvector")
'''Path of folder containing user files.'''

BaseMasterPath = os.path.join(os.path.split(__file__)[0], "res")
'''Path to the master (non-user) files.'''


##
## Various default resource files
##

DefaultStyleSheet = os.path.join(BaseMasterPath, "ui", "DefaultTheme.qss")
'''Path to the default stylesheet for the application.'''

UserConfig = os.path.join(BaseUserPath, "Settings.cfg")
'''Path to the user's settings file.'''

##
## Resource directory prefixes
## (These can be added to a server resource directory, or onto the master
## resource directory to get the default resources).
##

ServersPrefix = "Servers"
'''Directory prefix of the folder containing all server resources.'''

SpritesPrefix = "Sprites"
'''Directory prefix of the sprites folders.'''


##
## Methods for locating server-specific files
##

def ServerResourceDir(name):
    '''
    Gets the path to the base resource directory for the given server.
    
    @type name: string
    @param name: Server name
    '''
    return os.path.join(BaseUserPath, ServersPrefix, name)


def CreateUserDataDir():
    """
    Creates the user-specific data directory.

    If the directory does not exist, nothing happens.
    """
    dirpath = os.path.join(os.path.expanduser("~"), BaseUserPath)
    Directories.mkdir(dirpath)


##
## ALL OF THE FOLLOWING METHODS ARE DEPRECATED!
## DO NOT USE THESE!!!
##

def GetUserFile(filename):
    """
    Gets a path to a user-specific data file (RW).
    """
    global BaseUserPath
    return os.path.join(os.path.expanduser("~"), BaseUserPath, filename)


def GetSpriteDir(basedir=""):
    """
    Gets a path to the sprites directory.
    """
    return os.path.join(os.getcwd(), basedir, "sprites")


def GetSpriteFile(filename, basedir=""):
    """
    Gets a path to a file in the sprites directory (R).
    """
    return os.path.join(GetSpriteDir(basedir=basedir), filename)


def GetDefaultMapDir(basedir=""):
    """
    Gets a path to the default maps directory (R).
    """
    return os.path.join(os.getcwd(), basedir, "default-maps")


def GetMapDir():
    """
    Gets a path to the user-specific maps directory (RW).
    """
    return GetUserFile("maps")


def GetMapFile(filename):
    """
    Gets a path to a file in the user-specific maps directory (RW).
    """
    return os.path.join(GetMapDir(), filename)


def GetRegexForExtension(extension):
    """
    Compiles a regular expression that matches any files
    with the given extension (ie. ".png", ".map", etc)
    """
    expression = ".*" + extension + r"$"
    compiled = re.compile(expression)
    return compiled


# Okay, so the base functions are done.  Let's add some more functions
# for finding specific resources.

def GetOptionsFile():
    """
    Gets the path to the client options file.
    
    @return: The path to the client options file.
    """
    return GetUserFile("options.cfg")
