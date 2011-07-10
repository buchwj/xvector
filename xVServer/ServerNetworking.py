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

from xVLib import Networking, Packets
from xVServer import ServerGlobals
from gevent.select import select
from gevent.pool import Pool
from gevent.server import StreamServer
from gevent import socket

# stuff we use later
App = ServerGlobals.Application
mainlog = logging.getLogger("Server.Main")

class ConnectionClosed(Exception): pass
'''Raised when a connection is closed.'''


class ServerConnectionHandler(Networking.BaseConnectionHandler):
    '''
    Server-side connection handler which interfaces with gevent.
    '''
    def __init__(self, sock=None, addr=None):
        '''
        Creates a new server-side connection handler.
        
        @type sock: gevent.socket.socket
        @param sock: Connected socket to wrap
        
        @type addr: network address tuple
        @param addr: Network address of remote machine
        '''
        # inherit base class behavior
        super(ServerConnectionHandler, self).__init__()
        
        # declare our attributes
        self.sock = sock
        '''Socket connected to the remote machine.'''
        
        self.addr = addr
        '''Network address of the remote machine.'''
        
        # create the buffers
        self.RecvBufer = b""
        '''Buffer of received data; packets are built from this.'''
        
        self.SendBuffer = b""
        '''Buffer of sent data.'''
    
    ##
    ## reimplemented methods from Networking.BaseConnectionHandler
    ##
    def SendPacket(self, packet):
        pass    # TODO: Implement
    
    def PacketReceived(self, packet):
        pass    # TODO: Implement
    
    ##
    ## low-level callbacks
    ##
    def OnReadable(self):
        '''
        Called when connection data can be read.
        
        This method reads the data off the wire and appends it to the buffer,
        then attempts to build a packet from the data.  If it succeeds, it
        calls the PacketReceived() callback method and removes the data from
        the buffer.
        '''
        pass    # TODO: Implement
    
    def OnWritable(self):
        '''
        Called when data can be written to the socket.
        
        This method writes as much data from the write buffer as it can, then
        removes the data from the write buffer.
        '''
        pass    # TODO: Implement
    
    def OnClose(self):
        '''
        Called when the connection is closed.
        
        When this is called, you should assume that the socket has already
        been closed.  This method is only for cleanup after the connection
        has ended.
        '''
        pass    # TODO: Implement


def ServerConnectionThread(sock, addr):
    '''
    Greenlet function for gevent which handles a server network connection.
    
    All this does is map the green socket to the appropriate callback methods
    in the ServerConnectionHandler class; it also is responsible for creating
    the handler object.
    '''
    # Log the connection and build a handler
    mainlog.log(logging.INFO, "New connection from %s" % addr[0])
    handler = ServerConnectionHandler(sock, addr)
    # TODO: Register handler with the connection manager
    
    # Continuously poll the socket.
    try:
        socklist = [sock]
        while 1:
            ready = select(socklist, socklist, socklist, timeout=30.0)
            
            # What's going on?
            readable, writable = ready[0:2]
            rcount = len(readable)
            wcount = len(writable)
            if rcount == 0 and wcount == 0:
                # Connection timed out.
                sock.close()
                raise ConnectionClosed
            if rcount > 0:
                # Data can be read from the socket.
                handler.OnReadable()
            if wcount > 0:
                # Socket is writable.
                handler.OnWritable() 
    except ConnectionClosed:
        # clean up the connection here
        handler.OnClose()
    except:
        # unhandled exception
        msg = "Unhandled exception in connection from %s\n\n" % addr[0]
        msg += traceback.format_exc()
        mainlog.log(logging.ERROR, msg)
    finally:
        mainlog.log(logging.INFO, "Connection closed from %s" % addr[0])


class NetworkStartupError(Exception): pass
'''Raised if an error occurs while initializing the network server.'''


class NetworkServer(object):
    '''
    Manages network resources for the server.
    '''
    
    def __init__(self, address):
        '''Creates an empty server.'''
        # gevent-related attributes
        try:
            self.ThreadPool = Pool(int(App.Config['Network.Connections.Max']))
            '''Greenlet pool containing connection handlers.'''
        except ValueError:
            mainlog.critical("Maximum connection count must be positive.")
            raise NetworkStartupError
        
        # prep the server socket
        try:
            self.ServerSocket = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
            self.ServerSocket.bind(address)
        except socket.error as err:
            # something went wrong
            msg = "Failed to create the listening socket: %s" % err.args[1]
            mainlog.critical(msg)
            raise NetworkStartupError
            
    
