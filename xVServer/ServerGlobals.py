# -*- coding: utf-8 -*-

# xVector Engine Server
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
Contains the application global variable, well as some constants.
'''

import sys

##
## Globals
##

Application = None
'''Global variable for the main application object.  Usable anywhere.'''


##
## Version Information
##

MajorVersion = 0
'''Server major version number.  Constant.'''

MinorVersion = 1
'''Server minor version number (max 99).  Constant.'''

LetterVersion = 'a'
'''Server version letter tag.  Constnat.'''

UniqueVersionID = 0
'''Unique version ID.  Guaranteed to increase with every release.  Constant.'''


##
## Default paths
##
if sys.platform == "win32":
    # Windows default paths
    DefaultConfigPath = "ServerConfig.xml"
    DefaultLogsPath = "logs"
else:
    # Assuming a POSIX-style system (Linux, etc.)
    DefaultConfigPath = "/etc/xvector/ServerConfig.xml"
    DefaultLogsPath = "/var/log/xvector"
