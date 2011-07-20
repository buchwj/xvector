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
Server-specific network code.
'''

import logging
import traceback
import asyncore
import socket
import cStringIO

from xVLib import Networking, Packets
from xVServer import ServerGlobals

# stuff we use later
mainlog = logging.getLogger("Server.Main")

class ConnectionClosed(Exception): pass
'''Raised when a connection is closed.'''


class ServerConnection(asyncore.dispatcher_with_send):
    '''
    Server-side connection handler for a single connection.
    
    Although not explicitly inheriting from it, this class implements the
    xVLib.BaseConnectionHandler interface.
    '''
    def __init__(self, sock=None, map=None):
        '''
        Creates a new server-side connection handler.
        
        @type sock: socket
        @param sock: Connected socket to wrap
        
        @type map: dict
        @param map: Tracking structure for asyncore.
        '''
        # inherit base class behavior
        asyncore.dispatcher_with_send.__init__(self, sock, map)
        
        # declare our network attributes
        self.sock = sock
        '''Socket connected to the remote machine.'''
        
        self.Address = sock.getpeername()
        '''Network address of the remote machine.'''
        
        # Register the connection.
        msg = "New connection from %s." % self.Address[0]
        mainlog.info(msg)
        App = ServerGlobals.Application
        try:
            App.Connections.AddConnection(self)
        except ConnectionLimitExceeded:
            self.close()
        
        # create the buffer
        self.RecvBuffer = b""
        '''Buffer of received data; packets are built from this.'''
    
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
            NewPacket = Packets.BuildPacketFromStream(BufferStream)
        
            # If we get here, it worked.  Drop the data from the buffer.
            PacketEnd = BufferStream.tell()
            self.RecvBuffer = self.RecvBuffer[PacketEnd:]
            
            return NewPacket
        except:
            # re-raise the exception
            raise
        finally:
            BufferStream.close()
    
    ##
    ## connection information properties
    ##
    
    @property
    def AccountName(self):
        '''Read-only property for accessing the connected account's name.'''
        return None     # TODO: Implement
    
    @property
    def CharacterName(self):
        '''Read-only property for accessing the connected character's name.'''
        return None     # TODO: Implement
    
    ##
    ## reimplemented methods from Networking.BaseConnectionHandler
    ##
    
    def SendPacket(self, packet):
        '''
        Reimplmented from xVLib.Networking.BaseConnectionHandler.
        
        All we do here is convert the packet to binary and add it to the
        outgoing data queue.  Nothing fancy.
        '''
        # get the packet data and send it
        data = packet.GetBinaryForm()
        self.send(data)
    
    def PacketReceived(self, packet):
        '''
        Reimplemented from xVLib.Networking.BaseConnectionHandler.
        
        Here we pass the packet to the appropriate handler.  Again, nothing
        special.  This is essentially just a routing method.
        '''
        pass    # TODO: Implement
    
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
            # Corrupt packet? Hmm... better log this.
            mainlog.error("%s - Corrupt packet received." % self.Address[0])
            # And, of course, kill the connection! Bad connection! BAD!
            self.close()
        except:
            # Unhandled exception?
            msg = self.Address[0] + " - Unhandled exception while reading "
            msg += "data.\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
            # Better close the connection just to be safe.
            self.close()
    
    def handle_close(self):
        '''
        Called when the connection is closed by the remote machine.
        '''
        self.close()
    
    def handle_error(self):
        '''
        Called when an unhandled exception occurs in the handler.
        '''
        # log the error
        msg = self.Address[0] + " - Unhandled exception in connection handler."
        msg += "\n%s" % traceback.format_exc()
        mainlog.error(msg)
        
        # kill the connection if it's still alive
        try:
            self.close()
        except:
            # we don't care
            pass
    
    ##
    ## reimplemented methods from asyncore.dispatcher
    ##
    
    def close(self):
        '''
        Closes the socket and cleans up.
        
        This extends the close() method of asyncore.dispatcher.
        '''
        # Log the close event.
        msg = "%s - Connection closed." % self.Address[0]
        mainlog.info(msg)
        
        # Inherit base class behavior.
        asyncore.dispatcher_with_send.close(self)


class ConnectionLimitExceeded(Exception): pass
'''Raised if the connection limit is exceeded.'''


class UnregisteredConnection(Exception): pass
'''Raised if a referenced connection is not registered with the manager.''' 


class NameAlreadyInUse(Exception): pass
'''Raised if an account or character name is already in use.'''


class ConnectionManager(object):
    '''
    Manages the set of server connections.
    
    This class exposes a set of data structures useful for rapid lookup of
    connections.  The individual connections are responsible for registering
    themselves appropriately.
    
    Note that a connection does not have to be registered with all indices at
    once.  It MUST be registered with ConnectionSet and ByAddress, but the
    others are only mandatory once they make sense for the connection.
    '''
    def __init__(self):
        '''Creates an empty connection manager.'''
        # Create the master connection set.
        self.ConnectionSet = set()
        '''Set of all managed connections.'''
        
        # Create the lookup indices.
        self.ByAddress = {}
        '''Maps network address tuples to their connections.'''
        self.ByAccountName = {}
        '''Maps account names to their connections.'''
        self.ByCharacterName = {}
        '''Maps character names to their connections.'''
        
        # Create the tracking lists.
        self.AddressConnectCount = {}
        '''Maps address strings to the number of connections from them.'''
    
    def AddConnection(self, conn):
        '''Adds a connection.'''
        # check that the connection isn't already added
        if conn in self.ConnectionSet:
            # already added, continue
            return
        
        # now register the connection
        App = ServerGlobals.Application
        maxtotal = App.Config['Network.Connections.Max']
        addr = conn.Address
        if len(self.ConnectionSet) > maxtotal:
            # Total connection limit exceeded
            msg = "Too many total connections, rejecting from %s." % addr[0]
            mainlog.warning(msg)
            raise ConnectionLimitExceeded
        self.ConnectionSet.add(conn)
        
        # check the address
        maxip = App.Config['Network.Connections.PerIP']
        if addr[0] in self.AddressConnectCount:
            if self.AddressConnectCount[addr[0]] > maxip:
                # Per-IP connection limit exceeded.
                msg = "Too many connections from %s, rejecting." % addr[0]
                mainlog.warning(msg)
                raise ConnectionLimitExceeded
            self.AddressConnectCount[addr[0]] += 1
        else:
            self.AddressConnectCount[addr[0]] = 1
        self.ByAddress[addr] = conn
    
    def UpdateConnection(self, conn, oldAccount=None, oldChar=None):
        '''
        Updates a connection that has already been added.
        
        @type conn: ServerConnection
        @param conn: Connection object to update in the manager.
        
        @type oldAccount: string
        @param oldAccount: If set, the old account name to cancel.
        
        @type oldChar: string
        @param oldChar: If set, the old character name to cancel.
        
        @raise NameAlreadyInUse: Raised if the account or character name is
        already registered with a different connection.
        '''
        # ensure that the connection is registered
        if conn not in self.ConnectionSet:
            # not registered
            addr = conn.Address[0]
            msg = "Tried to update an unregistered connection from %s." % addr
            mainlog.error(msg)
            raise UnregisteredConnection
        
        # is there a change of account?
        if conn.AccountName:
            if conn.AccountName in self.ByAccountName:
                if self.ByAccountName[conn.AccountName] != conn:
                    # account already connected by other connection
                    raise NameAlreadyInUse
            else:
                # register
                self.ByAccountName[conn.AccountName] = conn
        else:
            if oldAccount:
                # does this connection actually own that account?
                try:
                    if self.ByAccountName[oldAccount] == conn:
                        # deregister
                        del self.ByAccountName[oldAccount]
                except:
                    # we don't care about any key errors
                    pass
        
        # is there a change of character?
        if conn.CharacterName:
            # we don't have to check for it to already be logged in since the
            # character is tied to a single account
            self.ByCharacterName[conn.CharacterName] = conn
        else:
            if oldChar:
                try:
                    del self.ByCharacterName[oldChar]
                except:
                    pass
    
    def RemoveConnection(self, conn):
        '''
        Removes a connection.
        
        @type conn: ServerConnection
        @param conn: Connection to unregister
        
        @raise UnregisteredConnection: Raised if conn is not registered.
        '''
        # make sure the connection is registered
        if conn not in self.ConnectionSet:
            # not registered
            addr = conn.Address[0]
            msg = "Tried to remove an unregistered connection from %s." % addr
            mainlog.error(msg)
            raise UnregisteredConnection
        addr = conn.Address[0]
        
        # remove the connection from the lookup tables
        if conn.CharacterName:
            try:
                if self.ByCharacterName[conn.CharacterName] == conn:
                    del self.ByCharacterName[conn.CharacterName]
                else:
                    args = (addr, conn.CharacterName)
                    msg = "%s - Tried to deregister character %s not "
                    msg += "associated with the connection."
                    msg %= args
                    mainlog.error(msg)
            except:
                pass
        
        if conn.AccountName:
            try:
                if self.ByAccountName[conn.AccountName] == conn:
                    del self.ByAccountName[conn.AccountName]
                else:
                    args = (addr, conn.AccountName)
                    msg = "%s - Tried to deregister account %s not associated "
                    msg += "with the connection."
                    msg %= args
                    mainlog.error(msg)
            except:
                pass
        
        # remove the connection entirely
        self.ConnectionSet.remove(conn)
        try:
            self.AddressConnectCount[addr] -= 1
        except:
            msg = "%s - Failed to decrement per-IP connection count." % addr
            mainlog.error(msg)


class NetworkStartupError(Exception): pass
'''Raised if an error occurs while initializing the network server.'''


class NetworkServer(asyncore.dispatcher):
    '''
    Listens for new incoming connections and assigns them to handlers.
    '''
    
    def __init__(self):
        '''Creates the network server and starts listening for connections.'''
        # inherit base class behavior
        asyncore.dispatcher.__init__(self)
        
        # create the listening socket
        App = ServerGlobals.Application
        iface = App.Config['Network.Address.Interface']
        port = App.Config['Network.Address.Port']
        addr = (iface, port)
        try:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
        except socket.error as err:
            msg = "Could not create listening socket: %s" % err.args[1]
            mainlog.critical(msg)
            raise NetworkStartupError
        
        # bind to the network address and start listening
        try:
            self.bind(addr)
        except socket.error as err:
            msg = "Could not bind listening socket: %s" % err.args[1]
            mainlog.critical(msg)
            raise NetworkStartupError
        try:
            self.listen(5)
        except socket.error as err:
            msg = "Could not listen on listening socket: %s" % err.args[1]
            mainlog.critical(msg)
            raise NetworkStartupError
    
    def handle_accept(self):
        '''Called when a client is trying to connect.'''
        # accept the connection
        try:
            pair = self.accept()
        except socket.error as err:
            # something went wrong
            msg = "Failed to accept incoming connection: %s" % err.args[1]
            mainlog.error(msg)
            return
        if not pair:
            # apparently they're not trying to connect anymore...
            return
        
        # wrap the connection
        sock, addr = pair
        conn = ServerConnection(sock)


def PollNetwork():
    '''
    Polls the network and handles any network events that are pending.
    
    This should be called once per cycle of the main loop.
    '''
    # figure out what we're doing
    App = ServerGlobals.Application
    usepoll = App.Config['Network.Engine.UsePoll']
    
    # poll the network
    asyncore.loop(timeout=0, count=1, use_poll=usepoll)
