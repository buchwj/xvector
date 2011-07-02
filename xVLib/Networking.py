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
Contains the base networking code extended in the client and server.
'''

import asyncore
import zlib

class BaseConnection(asyncore.dispatcher_with_send):
    '''
    The base class of all Connection objects.
    
    This is a simple wrapper around Python's asyncore module.
    We don't actually handle any network operations aside from send() in
    the base class; the asyncore callback methods must still be implemented
    in the subclasses.  What the base class does provide is an interface for
    writing to network sockets with optional compression and other features
    not already built into the asyncore module.
    '''
    
