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
import time
import cStringIO
from . import Packets

# A few constants...

TimeoutLimit = 60
'''
Number of seconds of network inactivity before a connection is "timed out."
'''


class BaseConnectionHandler(asyncore.dispatcher_with_send):
    '''
    The base class of all ConnectionHandler objects.
    
    This is an interface which defines the high-level interface of callbacks
    used to send and receive packets.  Actual sending and receiving of data is
    handled at a lower level by specific classes in xVClient and xVServer.  The
    two packages use different network APIs (asyncore in xVClient, gevent in
    xVServer) so we use a ConnectionHandler to abstract high-level network code
    and avoid compatibility issues between the two APIs.
    '''
    def __init__(self, sock=None):
        '''
        Creates a new BaseConnection object.
        
        @type sock: socket
        @param sock: Socket to wrap.
        '''
        # Inherit base class behavior.
        asyncore.dispatcher_with_send.__init__(self, sock)
        
        # Set up our initial timeout tracker.
        self.LastActivity = time.time()
        '''Time at which last network activity occurred.'''
        
        # Create the buffer.
        self.RecvBuffer = b""
        '''Buffer of received data; packets are built from this.'''
    
    @property
    def Address(self):
        return self.socket.getpeername()
    
    def SendPacket(self, packet):
        '''
        Queues a packet to be sent over the connection.  Non-blocking.
        
        @type packet: xVLib.Networking.Packet
        @param packet: Packet to send over the connection.
        '''
        # get the packet data and send it
        data = packet.GetBinaryForm()
        self.send(data)
    
    def CheckTimeout(self):
        '''
        Checks if the connection has timed out.
        
        If the connection has timed out, this will call the OnTimeout() method.
        '''
        # check timeout
        delta = time.time() - self.LastActivity
        if delta > TimeoutLimit:
            # connection timed out
            self.OnTimeout()
    
    def _TryPacketBuild(self):
        '''Tries to build a packet from the read buffer.'''
        # Make sure the buffer isn't empty.
        if len(self.RecvBuffer) == 0:
            # Empty.
            raise Packets.IncompletePacket
        try:
            # wrap the buffer in a stream
            BufferStream = cStringIO.StringIO(self.RecvBuffer)
        
            # try to build the packet
            NewPacket = Packets.BuildPacketFromStream(BufferStream, self)
        
            # If we get here, it worked.  Drop the data from the buffer.
            PacketEnd = BufferStream.tell()
            self.RecvBuffer = self.RecvBuffer[PacketEnd:]
            
            BufferStream.close()
            return NewPacket
        except:
            # re-raise the exception
            raise
    
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
        raise NotImplementedError
    
    def OnCorruptPacket(self):
        '''
        Called when a corrupt packet is received.
        
        Must be reimplemented by all subclasses.
        '''
        raise NotImplementedError
    
    def OnTimeout(self):
        '''
        Called when the connection times out.
        
        Must be reimplemented by all subclasses.
        '''
        raise NotImplementedError
        
    
    ##
    ## low-level callbacks
    ##
    def handle_read(self):
        '''
        Called when connection data can be read.
        
        This method reads the data off the wire and appends it to the buffer,
        then attempts to build a packet from the data.  If it succeeds, it
        calls the PacketReceived() callback method and removes the data from
        the buffer.
        
        This is a reimplemented callback method from dispatcher_with_send.
        '''
        # reset the timeout
        self.LastActivity = time.time()
        
        # receive data, append to buffer
        data = self.recv(8192)
        self.RecvBuffer += data
        
        # try building packets
        try:
            # this will loop until there are no more packets in the buffer
            while 1:
                NewPacket = self._TryPacketBuild()
                self.PacketReceived(NewPacket)
        except Packets.IncompletePacket:
            # Buffer is as cleared as possible... good.
            pass
        except Packets.CorruptPacket:
            # Corrupt packet.
            self.OnCorruptPacket()
        # Unhandled exceptions here will go to asyncore's handle_error method,
        # which you should probably overload.
    
    def handle_close(self):
        '''
        Called when the connection is closed by the remote machine.
        '''
        self.close()
