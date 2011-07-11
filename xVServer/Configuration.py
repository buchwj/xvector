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
Reads the main configuration file and makes settings available.
'''

# It is important that this file does not import other xVector modules.
# If it does, it may cause a circular dependency, and that would be bad.
# The only exception is xVServer.ServerGlobals, as that file is guaranteed
# not to import any other xVector modules.

from xVServer import ServerGlobals

from xml.parsers import expat
import logging
import traceback
import copy

mainlog = logging.getLogger("Server.Main")

_DefaultValues = {
                 # Network section
                 'Network.Address.Interface': u'0.0.0.0',
                 'Network.Address.Port': 24020,
                 'Network.Connections.Max': 50,
                 'Network.Connections.PerIP': 2,
                 'Network.Engine.UsePoll': False,
                 
                 # Logging section
                 'Logging.Directory.Path': ServerGlobals.DefaultLogsPath,
                 'Logging.Rotator.MaxSize': 4194304,
                 'Logging.Rotator.LogCount': 10,
                 }

def _NullTransformer(value): return value
_IntTransformer = int
def _BoolTransformer(value): 
    if value.tolower() == "true": return True
    return False

_KnownTransformers = {
                      # Network section
                      'Network.Address.Interface': _NullTransformer,
                      'Network.Address.Port': _IntTransformer,
                      'Network.Connections.Max': _IntTransformer,
                      'Network.Connections.PerIP': _IntTransformer,
                      'Network.Engine.UsePoll': _BoolTransformer,
                      
                      # Logging section
                      'Logging.Directory.Path': _NullTransformer,
                      'Logging.Rotator.MaxSize': _IntTransformer,
                      'Logging.Rotator.LogCount': _IntTransformer,
                      }

class _MainConfigurationParser(object):
    '''
    Object used internally for tracking the parser state.
    '''
    def __init__(self):
        '''Initializes the tracker.'''
        self.parser = expat.ParserCreate()
        '''Handle to the expat parser.'''
        self.ParentElements = []
        '''Stack of parent elements.'''
        self.ParsedConfig = copy.copy(_DefaultValues)
        '''Parsed configuration values.'''
        
        # Attach the callbacks.
        self.parser.StartElementHandler = self.StartElementHandler
        self.parser.EndElementHandler = self.EndElementHandler
    
    def LoadFromFile(self, filepath):
        '''
        Loads and parses the configuration from the given file.
        
        @type filepath: string
        @param filepath: File to load configuration from
        '''
        # parse the file
        with file(filepath, 'r') as fileobj:
            self.parser.ParseFile(fileobj)
            
        # run platform validation 
        self.PlatformValidation()
    
    def _GetPropName(self, attribute):
        '''
        Formats an attribute reference name for the configuration dict.
        
        @type attribute: string
        @param attribute: Name of the attribute whose name must be found.
        '''
        propname = ""
        for part in self.ParentElements:
            propname += "%s." % part
        propname += attribute
        return propname
    
    def StartElementHandler(self, name, attributes):
        '''
        Called from expat at the start of every element.
        '''
        # first of all, do we care about this?
        if name == "ServerConfiguration":
            # nope
            return
        
        # record the element
        self.ParentElements.append(name)
        for name, value in attributes.iteritems():
            PropName = self._GetPropName(name)
            # is the default being used?
            if value == "!!default!!":
                if PropName in _DefaultValues:
                    self.ParsedConfig[PropName] = _DefaultValues[PropName]
                    continue
            # can we validate/convert the type?
            if PropName in _KnownTransformers:
                try:
                    tvalue = _KnownTransformers[PropName](value)
                except:
                    # invalid value
                    raise ValueError("invalid value for option %s" % name)
            else:
                tvalue = value
            self.ParsedConfig[PropName] = tvalue
    
    def EndElementHandler(self, name):
        '''
        Called from expat at the end of every element.
        '''
        # first of all, do we care about this?
        if name == "ServerConfiguration":
            # nope
            return
        self.ParentElements.remove(name)
    
    def PlatformValidation(self):
        '''
        Runs platform validation on values.
        '''
        # Network.Engine.UsePoll not supported on all platforms
        if self.ParsedConfig['Network.Engine.UsePoll']:
            try:
                from select import poll
            except ImportError:
                # Not supported
                msg = "Your platform does not support poll; not using poll."
                mainlog.warning(msg)
                self.ParsedConfig['Network.Engine.UsePoll'] = False

def LoadConfigFile(filepath):
    '''
    Loads the main configuration file from the given filepath.
    
    @type filepath: string
    @param filepath: Filepath to load the main configuration file from
    '''
    try:
        # grab a parser and run it
        parser = _MainConfigurationParser()
        parser.LoadFromFile(filepath)
        
        # okay, if we got this far without an exception, we're all good
        return parser.ParsedConfig
    except ValueError as err:
        # failed the validation/transformation
        args = (filepath, err[1])
        msg = "While loading configuration file %s: %s" % args
        mainlog.log(logging.ERROR, msg)
        return None
    except IOError as err:
        # something went wrong low-level
        args = (filepath, err[1])
        msg = "While loading configuration file %s: %s" % args
        mainlog.log(logging.ERROR, msg)
        return None
    except expat.ExpatError as err:
        # something went wrong while parsing
        args = (filepath, err.args[0])
        msg = "While loading configuration file %s: %s" % args
        mainlog.log(logging.ERROR, msg)
        return None
    except:
        # unhandled exception
        args = (filepath, traceback.format_exc())
        msg = "Unhandled exception while loading configuration file %s:\n%s"
        msg = msg % args
        mainlog.log(logging.ERROR, msg)
        return None
