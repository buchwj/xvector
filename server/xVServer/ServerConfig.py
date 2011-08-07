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
Contains constants for the server configuration.

The server configuration file is loaded using the code in the ConfigurationFile
module in xVLib.  This module only contains constants specific to the server
configuration.
'''

from . import ServerGlobals
from xVLib.ConfigurationFile import NullTransformer, IntTransformer
from xVLib.ConfigurationFile import BoolTransformer

DefaultValues = {
                 # General section
                 'General/ServerName': u'Change This',
                 'General/ServerNewsURL': u'',
                 'General/DisableRegistration': u'',
                 
                 # Database section
                 'Database/Type': u'sqlite',
                 'Database/Host': u'',
                 'Database/Port': 0,
                 'Database/Name': u'xvector.sqlite',
                 'Database/Username': u'',
                 'Database/Password': u'',
                 
                 # Resources section
                 'Resources/AutoUpdater/Enabled': False,
                 'Resources/AutoUpdater/URL': u'',
                 'Resources/ExternalMaps/Enabled': False,
                 'Resources/ExternalMaps/URL': u'',
                 
                 # Network section
                 'Network/Address/IPv4/Enabled': True,
                 'Network/Address/IPv4/Interface': u'0.0.0.0',
                 'Network/Address/IPv4/Port': 24020,
                 'Network/Address/IPv6/Enabled': True,
                 'Network/Address/IPv6/Interface': u'::',
                 'Network/Address/IPv6/Port': 24020,
                 'Network/Connections/Max': 50,
                 'Network/Connections/PerIP': 2,
                 'Network/Engine/UsePoll': False,
                 
                 # Logging section
                 'Logging/Directory': ServerGlobals.DefaultLogsPath,
                 'Logging/Rotator/MaxSize': 4194304,
                 'Logging/Rotator/LogCount': 10,
                 }
'''
Standard default values for the server configuration.
'''

KnownTransformers = {
                      # General section
                      'General/ServerName': NullTransformer,
                      'General/ServerNewsURL': NullTransformer,
                      'General/DisableRegistration': BoolTransformer,
                      
                      # Resources section
                      'Resources/AutoUpdater/Enabled': BoolTransformer,
                      'Resources/AutoUpdater/URL': NullTransformer,
                      'Resources/ExternalMaps/Enabled': BoolTransformer,
                      'Resources/ExternalMaps/URL': NullTransformer,
                      
                      # Network section
                      'Network/Address/IPv4/Enabled': BoolTransformer,
                      'Network/Address/IPv4/Interface': NullTransformer,
                      'Network/Address/IPv4/Port': IntTransformer,
                      'Network/Address/IPv6/Enabled': BoolTransformer,
                      'Network/Address/IPv6/Interface': NullTransformer,
                      'Network/Address/IPv6/Port': IntTransformer,
                      'Network/Connections/Max': IntTransformer,
                      'Network/Connections/PerIP': IntTransformer,
                      'Network/Engine/UsePoll': BoolTransformer,
                      
                      # Logging section
                      'Logging/Directory': NullTransformer,
                      'Logging/Rotator/MaxSize': IntTransformer,
                      'Logging/Rotator/LogCount': IntTransformer,
                      }
'''
Standard value transforms for the server configuration.
'''
