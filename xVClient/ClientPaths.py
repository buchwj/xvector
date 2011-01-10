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


# constants
userdir = ".xvector"


# Next function borrowed from ActiveState. See link below.
def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well

        http://code.activestate.com/recipes/82465/
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        if tail:
            os.mkdir(newdir)
# End borrowed code.


def CreateUserDataDir():
    """
    Creates the user-specific data directory.

    If the directory does not exist, nothing happens.
    """
    dirpath = os.path.join(os.path.expanduser("~"), userdir)
    _mkdir(dirpath)


def GetUserFile(filename):
    """
    Gets a path to a user-specific data file (RW).
    """
    global userdir
    return os.path.join(os.path.expanduser("~"), userdir, filename)


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
