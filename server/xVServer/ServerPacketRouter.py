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
Packet router for the server.
'''

import logging
from xVLib import Packets

mainlog = logging.getLogger("Server.Main")

def PacketRejector(packet):
    '''
    Rejects any packets passed to this handler.
    
    @type packet: xVLib.Packets.Packet
    @param packet: Packet to reject.
    '''
    # log the event
    args = (packet.Connection.Address, packet.PacketType)
    msg = "%s - Unhandled packet type %i received." % args
    mainlog.warning(msg)
    
    # close the connection
    packet.Connection.close()


def KeepAliveHandler(self, packet):
    '''
    Packet handler for the KeepAlive packet type.
    
    @type packet: xVLib.Packets.KeepAlivePacket
    @param packet: Packet to handle.
    '''
    # make sure this is a keep-alive packet
    if packet.PacketType != Packets.KeepAlive:
        msg = "Packet with type %i passed to KeepAliveHandler."
        msg %= packet.PacketType
        mainlog.error(msg)
        raise TypeError(msg)
    
    # reply with a keep-alive packet of our own
    reply = Packets.KeepAlivePacket(packet.Connection)
    packet.Connection.SendPacket(reply)


class BaseServerPacketRouter(Packets.PacketRouter):
    '''
    Base server packet router.  This automatically rejects all packets.
    
    Subclass this to create state-specific packet routers.
    '''
    
    def __init__(self):
        # Inherit from base class.
        super(BaseServerPacketRouter, self).__init__()
        
        # Set default packet handler.
        self.DefaultHandler = PacketRejector
        
        # Create our keep-alive handler.
        self.Handlers[Packets.KeepAlive] = KeepAliveHandler
