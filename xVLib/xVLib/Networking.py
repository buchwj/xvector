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
import socket, ssl
import hashlib
import cStringIO
from collections import deque
from . import Packets

# A few constants...

TimeoutLimit = 60
'''
Number of seconds of network inactivity before a connection is "timed out."
'''

##
## Development public key fingerprints
## (for displaying warnings to players)
##

DEFAULT_KEY_FINGERPRINT = "\xc3\x88<\xa1\xb9\x14Dd\xe7zJ\x82Itl'>\xec8\x8f"
'''
Public key fingerprint for the default developer certificate that ships with
the server.  This certificate is fine for development purposes but should not
be used with production servers as the "private" key is not actually private.
The fingerprint is included in the code for matching against remote peer keys
in order to warn players about potentially insecure servers.

This fingerprint is calculated by taking the SHA-1 digest of the return value
of SSLSocket.getpeercert(binary_form=True) on the client.
'''

class EncryptionException(Exception): pass
'''Raised if a network encryption method is called at an inappropriate time.'''

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
        
        # Set up encryption trackers.
        self._NegotiateTLS = False
        '''If True, negotiates a TLS encryption layer with the other side.'''
        self._DenegotiateTLS = False
        '''If True, denegotiates a TLS encryption layer with the other side.'''
        self.PostNegotiationPackets = deque()
        '''Queue of packets to send after a successful TLS negotiation.'''
        self.PostDenegotiationPackets = deque()
        '''Queue of packets to send after a successful TLS denegotiation.'''
        self.IsEncrypted = False
        '''If True, the connection is encrypted with TLS.'''
    
    @property
    def Address(self):
        return self.socket.getpeername()
    
    def SendPacket(self, packet):
        '''
        Queues a packet to be sent over the connection.  Non-blocking.
        
        @type packet: xVLib.Networking.Packet
        @param packet: Packet to send over the connection.
        '''
        # Any negotiations/denegotiations going on to queue packets for?
        if self._NegotiateTLS:
            self.PostNegotiationPackets.append(packet)
            return
        elif self._DenegotiateTLS:
            self.PostDenegotiationPackets.append(packet)
            return
        
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
    
    def WrapTLS(self):
        '''
        Wraps the connection in a TLS encryption layer.
        
        This method is non-blocking and will return immediately; however, this
        does not mean that the connection is encrypted as soon as the method
        returns.  For all intents and purposes, however, you can treat it as
        such because no other traffic (including any sensitive data) will be
        sent during the negotiation phase.
        
        You can check for a successful negotiation by checking the IsEncrypted
        member variable.
        '''
        if self._NegotiateTLS or self._DenegotiateTLS or self.IsEncrypted:
            # invalid connection state for calling this method
            raise EncryptionException("cannot call WrapTLS() at this time")
        self._NegotiateTLS = True
        self._DenegotiateTLS = False
        self.IsEncrypted = False
        self.OnNegotiateTLS()
    
    def UnwrapTLS(self):
        '''
        Unwraps the connection from a TLS encryption layer.
        
        This method is non-blocking and will return immediately; however, this
        does not mean that the connection is decrypted as soon as the method
        returns.  For all intents and purposes, however, you can treat it as
        such because no other traffic will be sent or received until the
        denegotiation is complete.
        
        You can check for the completion of the denegotiation by checking the
        IsEncrypted member variable. 
        '''
        if self._NegotiateTLS or self._DenegotiateTLS or not self.IsEncrypted:
            # invalid connection state for calling this method
            raise EncryptionException("cannot call UnwrapTLS() at this time")
        self._NegotiateTLS = False
        self._DenegotiateTLS = True
        self.IsEncrypted = True
    
    
    def GetKeyFingerprint(self):
        '''
        If the connection is currently encrypted with TLS, calculates a
        fingerprint of the remote public key.
        
        @raise EncryptionException: Raised if this is called when the
        connection is not encrypted.
        
        @return: Returns a fingerprint of the remote public key.
        '''
        if not self.IsEncrypted:
            msg = "Cannot get fingerprint when connection not encrypted."
            raise EncryptionException(msg)
        
        key = self.socket.getpeercert(binary_form=True)
        return hashlib.sha1(key).digest()
    
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
    
    def OnNegotiateTLS(self):
        '''
        Called when TLS encryption needs to be negotiated.
        
        Must be reimplemented by all subclasses.
        
        This method should NOT attempt to perform the TLS handshake; instead,
        simply wrap the socket appropriately and replace this object's socket
        member variable with the wrapped socket.  The handshake is
        automatically taken care of by the default I/O event handlers.
        '''
        raise NotImplementedError
    
    def OnValidateRemoteKey(self):
        '''
        Called when the remote key of a TLS connection can be verified.
        
        This only needs to be reimplemented by subclasses if there are cases
        where the key can be rejected; the default behavior is to accept all
        remote keys.
        
        @return: Returns True if the key is accepted, False otherwise.
        '''
        return True
    
    ##
    ## more encryption stuff
    ##
    def _PushTLSHandshake(self):
        '''
        Tries to process any TLS handshakes that are pending.
        '''
        if self._NegotiateTLS:
            try:
                self.socket.do_handshake()
            except ssl.SSLError as err:
                # Failed; is this a fatal error?
                if (err.arg[0] != ssl.SSL_ERROR_WANT_READ
                    and err.arg[0] != ssl.SSL_ERROR_WANT_WRITE):
                    # Fatal error.
                    raise
                else:
                    # Can't do anything for now.
                    return
            # Negotiation successful... clear the backlog.
            self.IsEncrypted = True
            self._NegotiateTLS = False
            self._DenegotiateTLS = False
            
            # Validate the key.
            key_accepted = self.OnValidateRemoteKey()
            if not key_accepted:
                # Remote key is rejected for some reason
                self.shutdown(socket.SHUT_RDWR)
                self.close()
            
            # Send all the packets that were waiting to be sent.
            try:
                while 1:
                    packet = self.PostNegotiationPackets.popleft()
                    self.SendPacket(packet)
            except IndexError:
                pass
        
        elif self._DenegotiateTLS:
            try:
                self.socket = self.socket.unwrap()
            except ssl.SSLError as err:
                # Failed; is this a fatal error?
                if (err.arg[0] != ssl.SSL_ERROR_WANT_READ
                    and err.arg[0] != ssl.SSL_ERROR_WANT_WRITE):
                    # Fatal error.
                    raise
                else:
                    # Can't do anything for now.
                    return
            # Denegotiation successful... clear the backlog.
            self.IsEncrypted = True
            self._NegotiateTLS = False
            self._DenegotiateTLS = False
            try:
                while 1:
                    packet = self.PostDenegotiationPackets.popleft()
                    self.SendPacket(packet)
            except IndexError:
                pass
    
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
        
        # first of all: are we negotiating/denegotiating any TLS stuff?
        if self._NegotiateTLS or self._DenegotiateTLS:
            # First we need to flush the send buffer... anything there?
            if len(self.out_buffer) == 0:
                # No; let's try to negotiate whatever.
                self._PushTLSHandshake()
        
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
    
    def handle_write(self):
        '''
        Called when we can write data to the connection.
        
        The data queueing is handled by the parent asyncore class; we simply
        extend this method to handle our encryption stuff.
        '''
        # Are we negotiating anything?
        if self._NegotiateTLS or self._DenegotiateTLS:
            # First we need to flush the send buffer... anything there?
            if len(self.out_buffer) == 0:
                # No; let's try to negotiate whatever.
                self._PushTLSHandshake()
        
        # Fall back on the default behavior (thereby also flushing buffers).
        asyncore.dispatcher_with_send.handle_write(self)
    
    def handle_close(self):
        '''
        Called when the connection is closed by the remote machine.
        '''
        self.shutdown(socket.SHUT_RDWR)
        self.close()
