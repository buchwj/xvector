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
Classes which represent binary network packets as Python objects.
'''

import cStringIO
import zlib
from xVLib import BinaryStructs

class IncompletePacket(Exception): pass
'''Raised when a packet cannot be decoded because it is incomplete.'''


class CorruptPacket(Exception): pass
'''Raised when a packet cannot be decoded because it is corrupt.'''


#
# Packet Types
# (see docs/protocol/protocol_core for details)
#
NegotiateConnection = 0
ConnectionAccepted = 1
ConnectionRejected = 2
KeepAlive = 3
Success = 4
Failed = 5
StartLogin = 6
LoginChallenge = 7
FinishLogin = 8
Register = 9
AvailableCharacter = 10
StartCreateCharacter = 11
NewCharacterOptions = 12
FinishCreateCharacter = 13
SelectCharacter = 14
SendMessage = 15
ShowMessage = 16
AddObject = 17
DeleteObject = 18
UpdateObject = 19
GetMapCRC = 20
MapCRC = 21
GetMap = 22
MapReply = 23
InteractObject = 24
UpdateStats = 25
UpdateInventory = 26
Disconnect = 27
StartMovement = 28
EndMovement = 29
MovementValid = 30
MovementInvalid = 31
ServerInformation = 32
BadLogin = 33
DeleteCharacter = 34
StartCharacterList = 35
InvalidRequest = 36

MAX_VALID_PACKET = InvalidRequest
'''Highest allowed value of a packet type, used for validation.'''

UnknownType = 65535


##
## Packet Header Flags
##

HeaderFlag_zlib = 1
'''Set in the packet header if the body is zlib-compressed.'''

##
## Networking base classes
##

class Packet(object):
    '''
    The base class of all packets, containing only a header with no body.
    '''
    
    def __init__(self):
        '''
        Creates a new empty packet, either blank or from binary data.
        
        @type data: binary data
        @param data: Data to build the packet from.
        '''
        # Packet header attributes.
        self.PacketType = UnknownType
        '''Packet type, one of the constants in xVLib.Packets.'''
    
    def GetBinaryForm(self):
        '''
        Encodes the packet to a binary string for network transmission.
        
        Do not subclass this method for custom packets; instead, subclass the
        GetBinaryBody() interface method.
        
        @return: Network-safe binary string containing the packet.
        '''
        # let's figure out what we're sending
        flags = 0
        body = self.GetBinaryBody()
        if body:
            # there's a body that needs to be compressed
            compressed = self.CompressIfNeeded(body)
            if compressed:
                bodywriter = cStringIO.StringIO()
                BinaryStructs.SerializeBinary(bodywriter, compressed)
                body = bodywriter.getvalue()
                bodywriter.close()
                flags |= HeaderFlag_zlib
        
        # okay, build the packet
        packetwriter = cStringIO.StringIO()
        
        # first, the header
        BinaryStructs.SerializeUint16(packetwriter, self.PacketType)
        BinaryStructs.SerializeUint16(packetwriter, flags)
        
        # then the body
        if body:
            packetwriter.write(body)
        
        # return the packet data
        retval = packetwriter.getvalue()
        packetwriter.close()
        return retval
    
    def DecodeFromData(self, data):
        '''
        Decodes a packet from data.
        
        @type data: Binary data
        @param data: Data from which to decode the packet.
        
        @raise IncompletePacket: Raised if not enough data is present.
        @raise CorruptPacket: Raised if the data is invalid.
        '''
        # Wrap the buffer in a string.
        stream = cStringIO.StringIO(data)
        
        # Read in the header.
        try:
            ph_type = BinaryStructs.DeserializeUint16(stream)
            ph_flags = BinaryStructs.DeserializeUint16(stream)
        except BinaryStructs.EndOfFile: 
            # Packet seems incomplete
            raise IncompletePacket
        
        # Validate the packet header.
        if ph_type > MAX_VALID_PACKET:
            # Unknown type; corrupt packet.
            raise CorruptPacket("Invalid packet type in header.")
        
        # Now try reading the body.
        compressed = bool(ph_flags & HeaderFlag_zlib)
        self.GetBodyFromBinary(stream, compressed)
        
    
    def CompressIfNeeded(self, data):
        '''
        Compresses a chunk of data if it results in a smaller size.
        
        @type data: binary string
        @param data: Chunk of data to compress.
        
        @return: The compressed data if smaller than original, or None if not.
        '''
        # make the initial compression
        compressed = zlib.compress(data)
        if len(compressed) < len(data):
            # compression is good
            return compressed
        # compression isn't good
        return None
    
    def Decompress(self, stream):
        '''
        Attempts to decompress a chunk of data.
        
        @raise IncompletePacket: Raised if there is not enough data.
        
        @return: Decompressed chunk of data.
        '''
        
        # Try to deserialize the data from the stream.
        try:
            data = BinaryStructs.DeserializeBinary(stream)
        except BinaryStructs.EndOfFile:
            raise IncompletePacket
        
        # Attempt to decompress the data
        try:
            decompressed = zlib.decompress(data)
        except:
            # bad data
            raise CorruptPacket
        
        # Return the data.
        return decompressed
    
    ##
    ## Interface Methods
    ## Must be implemented by all subclasses
    ##
    
    def GetBinaryBody(self):
        '''
        Returns a binary representation of the packet body.
        
        This method must be reimplemented by any subclass which has a body.
        Packets which do not have a body do not need to reimplement this; the
        default behavior is to return no body.
        
        @return: Binary data representing the packet body, or None if no body.
        '''
        # default behavior: no body
        return None
    
    def GetBodyFromBinary(self, stream, compressed=False):
        '''
        Decodes the packet body from a data stream (i.e. StringIO, etc.)
        
        This method must be reimplemented by any subclass which has a body.
        Packets which do not have a body do not need to reimplement this; the
        default behavior is to return no body.
        
        @type stream: Stream (file-like) object, such as StringIO
        @param stream: Stream from which to read and decode packet data.
        
        @type compressed: Boolean value
        @param compressed: Set to True if the body is zlib-compressed.
        
        @raise IncompletePacket: Raised if the stream does not contain enough
        data to construct the body.  This tells the connection to continue
        waiting for additional data.
        
        @raise CorruptPacket: Raised if the stream contains invalid data.  This
        tells the connection to discard the packet and take appropriate action.
        '''
        # not implemented in the base class (no body)
        pass


PacketTypes = {}
'''
dict which maps packet types to the appropriate packet classes.

This maps directly to the classes, not to objects.
'''


def InitPackets():
    '''
    Initializes the packet type mapper.
    
    This function must be called before any packets can be decoded.
    '''
    # populate the packet type mapper
    pass    # TODO: Implement
