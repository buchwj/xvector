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

from xVLib import Networking
from . import ServerGlobals, IPBans, ConnectionNegotiation, Login

# stuff we use later
mainlog = logging.getLogger("Server.Main")


class ConnectionClosed(Exception): pass
'''Raised when a connection is closed.'''


class ServerConnection(Networking.BaseConnectionHandler):
    '''
    Server-side connection handler for a single connection.
    '''
    
    ##
    ## State constants.
    ##
    
    State_Negotiate = 0
    '''Connection negotiation state.'''
    State_WaitForLogin = 1
    '''State in which the server waits for the client to login or register.'''
    State_Login = 2
    '''State in which the server is processing a challenge-response login.'''
    State_CharacterSelect = 3
    '''State in which the user is selecting a character.'''
    State_CharacterCreate = 4
    '''State in which the user is creating a new character.'''
    State_Game = 5
    '''State in which the user is playing the game.'''
    
    
    ##
    ## State packet routers.
    ##
    StateRouters = {
        State_Negotiate: ConnectionNegotiation.ConnectionNegotiationRouter,
        State_WaitForLogin: Login.WaitForLoginRouter,
        State_Login: Login.LoginRouter,
        State_CharacterSelect: None,                # TODO: Implement
        State_CharacterCreate: None,                # TODO: Implement
        State_Game: None,                           # TODO: Implement
    }
    '''
    Maps connection states to their packet router classes.
    '''
    
    def __init__(self, sock=None):
        '''
        Creates a new server-side connection handler.
        
        @type sock: socket
        @param sock: Connected socket to wrap
        '''
        # Inherit base class behavior
        Networking.BaseConnectionHandler.__init__(self, sock)
        
        # Set the initial state.
        self.State = self.State_Negotiate
        '''Current state.'''
        self.Router = self.StateRouters[self.State]()
        '''Current packet router.'''
        print "[debug] self.Router = %s" % self.Router
        
        # Declare account management attributes.
        self._Account = None
        '''Account associated with this connection.'''
        
        # Login state tracking attributes.
        self.LoginChallenge = None
        '''Login challenge for the current login attempt.'''
        self.LastLogin = 0
        '''Time of the last login attempt.'''
        
        # Register the connection.
        msg = "New connection from %s." % self.Address[0]
        mainlog.info(msg)
        App = ServerGlobals.Application
        try:
            App.Connections.AddConnection(self)
        except ConnectionLimitExceeded:
            self.close()
        except BannedIPAddress:
            self.close()
    
    def SetState(self, newstate):
        self.State = newstate
        
        # Adjust the packet router.
        self.Router = self.StateRouters[newstate]()
    
    ##
    ## connection information properties
    ##
    
    def GetAccountName(self):
        '''Old-style class getter for the connected account's name.'''
        if self.Account:
            return self.Account.Username
        else:
            return None
    
    def GetCharacterName(self):
        '''Old-style class getter for the connected character's name.'''
        return None     # TODO: Implement
    
    def GetAccount(self):
        '''Old-style class getter for the associated account.'''
        return self._Account
    
    def SetAccount(self, newaccount):
        '''Old-style class setter for the associated account.'''
        self._Account = newaccount
    
    ##
    ## reimplemented methods from Networking.BaseConnectionHandler
    ##
    
    def PacketReceived(self, packet):
        '''
        Reimplemented from xVLib.Networking.BaseConnectionHandler.
        
        Here we pass the packet to the appropriate handler.  Again, nothing
        special.  This is essentially just a routing method.
        '''
        # Hand it off to the router.
        self.Router.HandlePacket(packet)
    
    def OnCorruptPacket(self):
        # Log an error message.
        msg = "%s - Corrupt packet received." % self.Address[0]
        msg += "\n\n%s" % traceback.format_exc()
        mainlog.error(msg)
        
        # Close the connection.
        self.close()
    
    def OnTimeout(self):
        # Log the event.
        msg = "%s - Connection timed out." % self.Address[0]
        mainlog.info(msg)
        
        # Close the connection.
        self.close()
    
    ##
    ## low-level asyncore callbacks
    ##
    
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
    ## crypto stuff
    ##
    
    def WrapTLS(self):
        '''
        Encrypts the connection in a TLS layer.
        '''
        
    
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
        
        # Deregister the connection.
        App = ServerGlobals.Application
        try:
            App.Connections.RemoveConnection(self)
        except UnregisteredConnection:
            pass
        
        # Inherit base class behavior.
        asyncore.dispatcher_with_send.close(self)


class ConnectionLimitExceeded(Exception): pass
'''Raised if the connection limit is exceeded.'''


class UnregisteredConnection(Exception): pass
'''Raised if a referenced connection is not registered with the manager.''' 


class NameAlreadyInUse(Exception): pass
'''Raised if an account or character name is already in use.'''


class BannedIPAddress(Exception): pass
'''Raised if the connection's IP address is banned.'''


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
        '''
        Adds a connection.
        
        @type conn: ServerConnection
        @param conn: Connection to add.
        '''
        # check that the connection isn't already added
        if conn in self.ConnectionSet:
            # already added, continue
            return
        
        # Make sure the connection's IP isn't banned.
        addr = conn.Address
        if IPBans.IsBanned(addr[0]):
            msg = "%s - IP is banned, rejecting connection." % addr[0]
            mainlog.info(msg)
            raise BannedIPAddress
        
        # now register the connection
        App = ServerGlobals.Application
        maxtotal = App.Config['Network/Connections/Max']
        if len(self.ConnectionSet) > maxtotal:
            # Total connection limit exceeded
            msg = "Too many total connections, rejecting from %s." % addr[0]
            mainlog.warning(msg)
            raise ConnectionLimitExceeded
        self.ConnectionSet.add(conn)
        
        # check the address
        maxip = App.Config['Network/Connections/PerIP']
        if addr[0] in self.AddressConnectCount:
            if self.AddressConnectCount[addr[0]] > maxip:
                # Per-IP connection limit exceeded.
                msg = "Too many connections from %s, rejecting." % addr[0]
                mainlog.info(msg)
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
        acctname = conn.GetAccountName()
        if acctname:
            if acctname in self.ByAccountName:
                if self.ByAccountName[acctname] != conn:
                    # account already connected by other connection
                    raise NameAlreadyInUse
            else:
                # register
                self.ByAccountName[acctname] = conn
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
        charname = conn.GetCharacterName()
        if charname:
            # we don't have to check for it to already be logged in since the
            # character is tied to a single account
            self.ByCharacterName[charname] = conn
        else:
            if oldChar:
                try:
                    del self.ByCharacterName[oldChar]
                except:
                    pass
    
    def RemoveConnection(self, conn):
        '''
        Queues a connection for removal.
        
        @type conn: ServerConnection
        @param conn: Connection to unregister
        
        @raise UnregisteredConnection: Raised if conn is not registered.
        '''
        # make sure the connection is registered
        if conn not in self.ConnectionSet:
            # not registered; don't report, this might be legitimate
            # (premature close() due to IP ban, etc.)
            raise UnregisteredConnection
        addr = conn.Address[0]
        
        # remove the connection from the lookup tables
        charname = conn.GetCharacterName()
        if charname:
            try:
                if self.ByCharacterName[charname] == conn:
                    del self.ByCharacterName[charname]
                else:
                    args = (addr, charname)
                    msg = "%s - Tried to deregister character %s not "
                    msg += "associated with the connection."
                    msg %= args
                    mainlog.error(msg)
            except:
                pass
        
        acctname = conn.GetAccountName()
        if acctname:
            try:
                if self.ByAccountName[acctname] == conn:
                    del self.ByAccountName[acctname]
                else:
                    args = (addr, acctname)
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
    
    def ScanForTimeouts(self):
        '''
        Finds timed-out connections and closes them.
        '''
        # Scan the connections.
        copyset = self.ConnectionSet.copy()
        for conn in copyset:
            conn.CheckTimeout()


class NetworkStartupError(Exception): pass
'''Raised if an error occurs while initializing the network server.'''


class NetworkServer(asyncore.dispatcher):
    '''
    Listens for new incoming connections and assigns them to handlers.
    
    Don't directly create instances of this class; instead, use one of its
    subclasses, either IPv4Server or IPv6Server.
    '''
    
    def __init__(self):
        '''Creates the network server and starts listening for connections.'''
        # Inherit base class behavior
        asyncore.dispatcher.__init__(self)
    
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
        sock = pair[0]
        conn = ServerConnection(sock)
    
    def handle_error(self):
        '''Called when an unhandled exception is raised.'''
        # show an error
        msg = "Unhandled exception in NetworkServer:\n" 
        msg += traceback.format_exc()
        mainlog.error(msg)


class IPv4Server(NetworkServer):
    '''
    Network server class for IPv4 connections.
    '''
    
    def __init__(self):
        # inherit base class behavior
        NetworkServer.__init__(self)
        
        # create the listening socket
        App = ServerGlobals.Application
        iface = App.Config['Network/Address/IPv4/Interface']
        port = App.Config['Network/Address/IPv4/Port']
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


class IPv6Server(NetworkServer):
    '''
    Network server class for IPv6 connections.
    '''
    
    def __init__(self):
        # inherit base class behavior
        NetworkServer.__init__(self)
        
        # create the listening socket
        App = ServerGlobals.Application
        iface = App.Config['Network/Address/IPv6/Interface']
        port = App.Config['Network/Address/IPv6/Port']
        addr = (iface, port)
        try:
            # Create the IPv6 socket
            self.create_socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.set_reuse_addr()
            
            # Limit to IPv6 only (this is an easy way to separate IPv4/IPv6 on
            # multiple platforms)
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
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


def PollNetwork():
    '''
    Polls the network and handles any network events that are pending.
    
    This should be called once per cycle of the main loop.
    '''
    # Figure out what we're doing
    App = ServerGlobals.Application
    usepoll = App.Config['Network/Engine/UsePoll']
    
    # Poll the network
    asyncore.loop(timeout=0, count=1, use_poll=usepoll)
    
    # Check for timed-out connections
    App.Connections.ScanForTimeouts()
