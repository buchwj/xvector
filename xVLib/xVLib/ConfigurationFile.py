# -*- coding: utf-8 -*-

# xVector Engine Core Library
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
Reads the main configuration file and makes settings available.
'''

# It is important that this file does not import other xVector modules.
# If it does, it may cause a circular dependency, and that would be bad.
# The only exception is xVServer.ServerGlobals, as that file is guaranteed
# not to import any other xVector modules.

from xml.etree import cElementTree
import logging

mainlog = logging.getLogger("")


DefaultFlag = "!!default!!"
'''Value that, if encountered, is replaced with the default value.'''


def NullTransformer(value): return value
'''Default transformer that makes no change to the value.'''

IntTransformer = int
'''Transforms value to an integer.'''

def BoolTransformer(value): 
    if value.lower() == "true" or value == "1": return True
    return False
'''Transforms value to a boolean.''' 


class ConfigurationFile(object):
    
    def __init__(self, filepath, defaults={}, transformers={}):
        '''
        Loads the configuration file from the given filepath.
        
        @type filepath: string
        @param filepath: Filepath of configuration file to load.
        
        @type defaults: dict
        @param defaults: Default values for options.
        
        @type transformers: dict
        @param transformers: Transformer methods to be used for converting
        values to the appropriate types.
        '''
        # Declare attributes.
        self.Tree = None
        '''Element tree of the configuration file.'''
        self.DefaultValues = defaults
        '''Default values for options.'''
        self.Transformers = transformers
        '''Transformer methods for converting values to appropriate formats.'''
        
        # Load the configuration file.
        with open(filepath, "r") as fileobj:
            self.Tree = cElementTree.parse(fileobj)
    
    def __getitem__(self, key):
        '''
        Called when this object is accessed as a dict.
        
        This looks up the option name provided as the key and returns the
        value.  If the option is not found and a default value is available,
        the default value will be returned; otherwise, a KeyError exception
        will be raised.
        
        @type key: string
        @param key: Option name
        
        @raise KeyError: Raised if the option is not set and no default value
        is available for the option.
        
        @raise ValueError: Raised if the default flag is set for the given
        option and there is no default value for the option.
        '''
        # Is a default available?
        try:
            default = self.DefaultValues[key]
        except KeyError:
            default = None
        
        # Look up the option in the file
        value = self.Tree.findtext(key, default)
        if value == None:
            # Not found, no default
            msg = "Option %s not found in configuration file." % key
            mainlog.error(msg)
            raise KeyError(key)
        value = value.strip()
        if value == DefaultFlag:
            # Replace with default.
            if default == None:
                # No default, this is an error.
                msg = "No default value for option %s." % key
                mainlog.error(msg)
                raise ValueError(msg)
            return default
        
        # Value needs any transformations?
        try:
            transformer = self.Transformers[key]
            # Transform and roll out... err, uh, I mean return.
            return transformer(value)
        except KeyError:
            # no transformer, return raw value
            return value
