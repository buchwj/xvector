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
Connection negotiation handlers for the server.
'''

import logging
from . import ServerGlobals
from xVLib import Packets, Version
from .ServerPacketRouter import BaseServerPacketRouter

mainlog = logging.getLogger("Server.Main")

##
## Basic packet handlers
##    
    
def ConnectionNegotiationHandler(packet):
    '''
    Handles the connection negotiation for a single connection.
    
    @type packet: xVLib.Packets.NegotiateConnectionPacket
    @param packet: Packet to handle.
    '''
    # Make sure this is a NegotiateConnection packet
    if packet.PacketType != Packets.NegotiateConnection:
        msg = "Packet with type %i passed to ConnectionNegotiationHandler."
        msg %= packet.PacketType
        mainlog.error(msg)
        raise TypeError(msg)
    
    # Perform a version check
    if packet.Signature != Packets.ProtocolSignature:
        # Protocol signature mismatch, error 3
        args = (packet.Connection.Address,
                Packets.ConnectionRejectedPacket.Error_Signature)
        msg = "%s - Connection rejected (error %i, signature mismatch)."
        msg %= args
        mainlog.info(msg)
        
        reply = Packets.ConnectionRejectedPacket(packet.Connection)
        reply.RejectionCode = reply.Error_Signature
        packet.Connection.SendPacket(reply)
        packet.Connection.close()
        return
    elif packet.Revision != Packets.ProtocolRevision:
        # Protocol revision mismatch, error 2
        args = (packet.Connection.Address,
                Packets.ConnectionRejectedPacket.Error_Revision)
        msg = "%s - Connection rejected (error %i, revision mismatch)."
        msg %= args
        mainlog.info(msg)
        
        reply = Packets.ConnectionRejectedPacket(packet.Connection)
        reply.RejectionCode = reply.Error_Revision
        packet.Connection.SendPacket(reply)
        packet.Connection.close()
        return
    elif (packet.MajorVersion != Version.MajorVersion or
          packet.MinorVersion != Version.MinorVersion):
        # Version mismatch, error 1
        args = (packet.Connection.Address,
                Packets.ConnectionRejectedPacket.Error_Outdated)
        msg = "%s - Connection rejected (error %i, version mismatch)."
        msg %= args
        mainlog.info(msg)
        
        reply = Packets.ConnectionRejectedPacket(packet.Connection)
        reply.RejectionCode = reply.Error_Outdated
        packet.Connection.SendPacket(reply)
        packet.Connection.close()
        return
    
    # Accept the connection
    App = ServerGlobals.Application
    reply = Packets.ConnectionAcceptedPacket(packet.Connection)
    reply.ServerName = App.Config['General/ServerName']
    reply.ServerNewsURL = App.Config['General/ServerNewsURL']
    # TODO: Add "no-register" flag support
    reply.SendPacket()
    packet.Connection.SetState(packet.Connection.State_WaitForLogin)


##
## Packet routers
##

class ConnectionNegotiationRouter(BaseServerPacketRouter):
    '''
    Single-connection packet router for the connection negotiation state.
    
    A separate object of this class should be created for each connection, as
    these objects track internal state.  (Actually, they DON'T in this case
    since the server only has a single task during the negotiation state, but
    it's good practice anyway.)
    '''
    
    def __init__(self):
        # Inherit from base class.
        super(ConnectionNegotiationRouter, self).__init__()
        
        # Set up negotiation handlers.
        negotiate = ConnectionNegotiationHandler
        self.Handlers[Packets.NegotiateConnection] = negotiate
        
        # Strike the keep-alive handler (not allowed before negotiation).
        del self.Handlers[Packets.KeepAlive]
