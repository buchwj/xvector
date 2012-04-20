# xVector Engine Client
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
Base networking code for the client.
'''

import socket
import traceback
import logging
import sys
import time
import asyncore
from xVLib import Networking, Packets
from PyQt4 import QtGui
from . import ClientGlobals

mainlog = logging.getLogger("Client.Main")

class ClientConnectionHandler(Networking.BaseConnectionHandler):
    '''
    Asynchronous network handler for the client.
    '''
    
    def __init__(self, sock=None):
        '''
        Creates a new connection handler.
        
        @type sock: socket
        @param sock: Socket to wrap.
        '''
        # Inherit base class behavior.
        Networking.BaseConnectionHandler.__init__(self, sock)
        
        # Declare attributes.
        self.KeepAliveSent = False
        '''Flag used to track if a KeepAlive packet has already been sent.'''
    
    ##
    ## High-level callbacks
    ##
    
    def PacketReceived(self, packet):
        '''
        Called when a packet is received.
        
        @type packet: xVLib.Packets.Packet
        @param packet: Packet that was received.
        '''
        pass    # TODO: Implement
    
    def OnCorruptPacket(self):
        '''
        Called when a corrupt packet is received.
        '''
        # Show error message.
        msg = "Corrupt data received from server."
        mainlog.error(msg)
        
        # Disconnect.
        self.close()
    
    def OnTimeout(self):
        '''
        Called when the connection times out.
        '''
        # Close the connection.
        self.close()
        
        # Show an error message.
        msg = "Connection to server timed out."
        mainlog.error(msg)
    
    def CheckTimeout(self):
        '''
        Checks if the connection is timed out.
        
        This is overloaded from a method in BaseConnectionHandler; this version
        adds a check to see if we need to send a KeepAlive packet. 
        '''
        # Inherit base class behavior.
        Networking.BaseConnectionHandler.CheckTimeout(self)
        
        # Check if we need to send a KeepAlive packet.
        delta = time.time() - self.LastActivity
        if not self.KeepAliveSent and delta > Networking.TimeoutLimit // 2:
            # Send a KeepAlive packet.
            self.KeepAliveSent = True
            keepalive = Packets.KeepAlivePacket(self)
            keepalive.SendPacket()
    
    ##
    ## Low-level asyncore callbacks
    ##
    
    def handle_connect(self):
        '''
        Called when the connection is first established.
        '''
        # Start the connection negotiation.
        ConnPacket = Packets.NegotiateConnectionPacket(self)
        self.SendPacket(ConnPacket)
    
    def handle_error(self):
        '''
        Called when an unhandled exception is caught.
        '''
        # What are we dealing with?
        type, value = sys.exc_info()[:2]
        if type == socket.error:
            # Socket error
            msg = "A network error has occurred.\n"
            msg += str(value)
            mainlog.error(msg)
        else:
            # Unhandled exception
            msg = "Unhandled exception in the connection handler:\n\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
        
        # Close the connection.
        self.close()
    
    def handle_read(self):
        # Switch off the KeepAliveSent flag.
        self.KeepAliveSent = False
        
        # Inherit base class behavior.
        Networking.BaseConnectionHandler.handle_read(self)
    
    def close(self):
        '''
        Closes the connection and returns to the title screen.
        '''
        # Inherit base class behavior.
        Networking.BaseConnectionHandler.close(self)
        
        # Go back to the title screen.
        App = ClientGlobals.Application
        App.Connection = None
        App.MainWindow.ChangeState(App.MainWindow.State_Startup)
    
    def OnValidateRemoteKey(self):
        # check if the server is using the development key
        fingerprint = self.GetKeyFingerprint()
        if fingerprint == Networking.DEFAULT_KEY_FINGERPRINT:
            # match; warn the user and ask for permission to continue
            title = "Security Warning"
            message = """You are attempting to login to a server which is using
            the default development private key for encryption.  By connecting
            to this server, your login information may be compromised by a
            third party.  Do you wish to continue connecting to the server?"""
            buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            response = QtGui.QMessageBox.warning(None, title, message, buttons,
                                                 QtGui.QMessageBox.No)
            return (response == QtGui.QMessageBox.Yes)
        
        # no match; we're good
        return True


class ConnectionFailed(Exception): pass
'''Raised if the connection was not successfully established.'''


def ConnectToServer(address):
    '''
    Initiates a connection to the server at the given address and wraps it.
    
    @type address: tuple
    @param address: Network address of server as a tuple C{(host, port)}
    '''
    # Try to connect.
    try:
        conn = ClientConnectionHandler()
        conn.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(address)
    except socket.error as err:
        msg = "Failed to connect to the server.\n"
        msg += "Error code %i: %s." % err[:2]
        mainlog.error(msg)
        raise ConnectionFailed
    
    # Set the main connection.
    App = ClientGlobals.Application
    App.Connection = conn


def PollNetwork():
    '''
    Polls for network activity.
    '''
    # Scan network.
    asyncore.loop(timeout=0, count=1)
    
    # Check for timeouts.
    App = ClientGlobals.Application
    conn = App.Connection
    if conn:
        conn.CheckTimeout()
