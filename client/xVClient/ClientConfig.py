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
Manages the options file for the client.
"""

import ConfigParser
import traceback
import logging

from xVClient import ClientPaths

mainlog = logging.getLogger("Client.Main")

# Constants
MAIN_SECTION = "Options"
"""The name of the main section of the options file."""


class EmptyConfigException(Exception): pass
"""Raised when ClientConfig.Save() is called without anything to save."""


class ClientConfig(object):
    """
    Manages persistant configuration values used by
    the client (ie. video settings, audo settings, etc).
    Configuration files are per-user, not global to each computer.
    """

    def __init__(self):
        """Initializes an empty configuration file."""
        self.parser = None

    def Load(self):
        """
        Loads the configuration values from the file.
        
        @warning: Any changes which have been made to this object will
        be lost if you do not first call Save().
        """
        self.parser = ConfigParser.SafeConfigParser(self.GetDefaults())
        self.parser.read(ClientPaths.UserConfig)

    def Save(self):
        """
        Saves the current configuration values to the file.
        
        @raise EmptyConfigException: Raised if there are no options to save.
        """
        # self-check
        if self.parser == None:
            # nothing to save!
            raise EmptyConfigException(_("configuration file is empty"))
        
        # save the file
        fileobj = open(self.GetFilepath(), 'w')
        self.parser.write(fileobj)
        fileobj.close()

    def GetOption(self, option):
        """
        Gets the value of a non-boolean option.
        
        @type option: string
        @param option: Name of the option to get the value of.
        
        @return: The value as a string, or None if the option is not set.
        """
        if not self.parser: return None
        return self.parser.get(MAIN_SECTION, option)

    def GetBoolOption(self, option):
        """
        Gets the value of a boolean option.
        
        @type option: string
        @param option: Name of the option to get the value of.
        
        @return: The value as a boolean, or None if the option is not set.
        """
        if self.parser == None:
            return None
        return self.parser.getboolean(MAIN_SECTION, option)

    def SetOption(self, option, value):
        """
        Sets a value.
        
        @type option: string
        @param option: Name of the option to set the value of.
        
        @type value: any
        @param value: New value.  If a string, this is used; otherwise, the
        option is converted by a call to C{str()}.
        """
        if not self.parser:
            # lazy-initialize a new (and empty) parser
            self.parser = ConfigParser.SafeConfigParser(self.GetDefaults())
        self.parser.set(MAIN_SECTION, option, str(value))

    def GetDefaults(self):
        """
        Returns a dictionary containing the default values
        for the configuration file.
        """
        defaults = dict()

        # SECTION 1: Video Options
        defaults['fullscreen'] = False
        
        # SECTION 2: Internationalization
        defaults['locale'] = "en_US"

        # All done!
        return defaults
    
    # And now, of course, we have our easy-access properties.
    # These are the preferred APIs since they save their changes.
    @property
    def fullscreen(self):
        """If true, the game will run in fullscreen mode."""
        return self.GetBoolOption("fullscreen")
    
    @fullscreen.setter
    def fullscreen(self, new_val):
        self.SetOption("fullscreen", new_val)
        self.Save()


# Okay, let's set up the cross-module support!
_MainConfig = None
"""The instance-wide configuration object, shared across all modules."""


class LoadConfigError(Exception): pass
"""Raised if a fatal error occurs during loading of the configuration file."""


def LoadConfig():
    """
    Loads the client configuration file for immediate use.
    """
    # Load it up!
    global _MainConfig
    try:
        _MainConfig = ClientConfig()
        _MainConfig.Load()
    except:
        msg = "Error while loading user settings file.\n"
        msg += traceback.format_exc()
        mainlog.error(msg)


def GetConfig():
    """
    Returns a handle to the instance-wide configuration file.
    """
    return _MainConfig
