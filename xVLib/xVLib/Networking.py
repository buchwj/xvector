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

import time

class BaseConnectionHandler(object):
    '''
    The base class of all ConnectionHandler objects.
    
    This is an interface which defines the high-level interface of callbacks
    used to send and receive packets.  Actual sending and receiving of data is
    handled at a lower level by specific classes in xVClient and xVServer.  The
    two packages use different network APIs (asyncore in xVClient, gevent in
    xVServer) so we use a ConnectionHandler to abstract high-level network code
    and avoid compatibility issues between the two APIs.
    '''
    def __init__(self):
        '''
        Creates a new BaseConnection object.
        '''
        
        # Set up our initial timeout tracker.
        self.last_activity = time.time()
        '''Time at which last network activity occurred.'''
    
    ##
    ## interface methods... subclasses should implement these
    ##
    
    def PacketReceived(self, packet):
        '''
        Callback method called when a full packet is received and decoded.
        
        Must be reimplemented by all subclasses.
        
        @type packet: xVLib.Networking.Packet
        @param packet: Packet received from the network.
        '''
        # no behavior in the base class; subclasses must implement this
        pass
    
    def SendPacket(self, packet):
        '''
        Queues a packet to be sent over the connection.  Non-blocking.
        
        Must be reimplemented by all subclasses.
        
        @type packet: xVLib.Networking.Packet
        @param packet: Packet to send over the connection.
        '''
        pass    # TODO: Implement
