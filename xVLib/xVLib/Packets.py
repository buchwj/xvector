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
import traceback
import logging
from xVLib import BinaryStructs, Version


ProtocolRevision = 0
'''Current revision of the network protocol.'''


class IncompletePacket(Exception): pass
'''Raised when a packet cannot be decoded because it is incomplete.'''


class CorruptPacket(Exception): pass
'''Raised when a packet cannot be decoded because it is corrupt.'''

##
## Constants
##

MaxCompressedSize = 65536
'''Maximum size of a compressed data block, in bytes.'''
# We don't want individual packets getting anywhere close to 64KB.

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
        
        # Internal flags
        self._HasBody = False
        '''Subclasses which have bodies should set this to True.'''
    
    def GetBinaryForm(self):
        '''
        Encodes the packet to a binary string for network transmission.
        
        Do not subclass this method for custom packets; instead, subclass the
        SerializeBody() interface method.
        
        @return: Network-safe binary string containing the packet.
        '''
        # let's figure out what we're sending
        flags = 0
        body = self.SerializeBody()
        if body:
            # there's a body that needs to be compressed
            compressed = self.CompressIfNeeded(body)
            if compressed != None:
                bodywriter = cStringIO.StringIO()
                BinaryStructs.SerializeBinary(bodywriter, compressed,
                                              maxlen=MaxCompressedSize)
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
    
    def DecodeFromData(self, stream):
        '''
        Decodes a packet from a data stream.
        
        @type stream: Stream (file-like) object
        @param stream: Stream from which to decode the packet.
        
        @raise IncompletePacket: Raised if not enough data is present.
        @raise CorruptPacket: Raised if the data is invalid.
        '''
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
        self._GetBodyFromBinary(stream, compressed)
    
    def _GetBodyFromBinary(self, stream, compressed=False):
        '''
        Internal wrapper method used to abstract the body decompression.
        
        @type stream: file-like object
        @param stream: Stream to read from
        
        @type compressed: bool
        @param compressed: If True, decompress before decoding.
        
        @raise IncompletePacket: Raised if the body is incomplete.
        @raise CorruptPacket: Raised if the body is corrupt.
        '''
        if self._HasBody:
            if compressed:
                decompressed = self.Decompress(stream)
                data = cStringIO.StringIO(decompressed)
            else:
                data = stream
            self.DeserializeBody(data)
            if compressed:
                data.close()
    
    def CompressIfNeeded(self, data):
        '''
        Compresses a chunk of data if it results in a smaller size.
        
        @type data: binary string
        @param data: Chunk of data to compress.
        
        @return: The compressed data if smaller than original, or None if not.
        '''
        # make the initial compression
        compressed = zlib.compress(data)
        if (len(compressed) < len(data)
            and len(compressed) <= MaxCompressedSize):
            # compression is good
            return compressed
        # compression isn't good (or is too large for a compression block)
        return None
    
    def Decompress(self, stream):
        '''
        Attempts to decompress a chunk of data.
        
        @raise IncompletePacket: Raised if there is not enough data.
        @raise CorruptPacket: Raised if the data is corrupt.
        
        @return: Decompressed chunk of data.
        '''
        
        # Try to deserialize the data from the stream.
        try:
            data = BinaryStructs.DeserializeBinary(stream,
                                                   maxlen=MaxCompressedSize)
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
    
    def SerializeBody(self):
        '''
        Returns a network-safe binary representation of the packet body.
        
        This method must be reimplemented by any subclass which has a body.
        Packets which do not have a body do not need to reimplement this; the
        default behavior is to serialize no body.
        
        @return: Network-safe binary representation of the packet body.
        '''
        # default behavior: no body
        return None
    
    def DeserializeBody(self, stream):
        '''
        Decodes the packet body from a data stream (i.e. StringIO, etc.)
        
        This method must be reimplemented by any subclass which has a body.
        Packets which do not have a body do not need to reimplement this; the
        default behavior is to not deserialize a body.
        
        @type stream: Stream (file-like) object, such as StringIO
        @param stream: Stream from which to read and decode packet data.
        
        @raise IncompletePacket: Raised if the stream does not contain enough
        data to construct the body.  This tells the connection to continue
        waiting for additional data.
        
        @raise CorruptPacket: Raised if the stream contains invalid data.  This
        tells the connection to discard the packet and take appropriate action.
        '''
        # not implemented in the base class (no body)
        pass


ProtocolSignature = b'\xa0\xd0'
'''Protocol signature of official protocol.'''


class VersionMismatch(Exception): pass
'''Raised if the the client and server version do not match.'''


class NegotiateConnectionPacket(Packet):
    '''Packet class for the NegotiateConnection packet type.'''
    
    def __init__(self):
        '''Creates a new NegotiateConnection packet.'''
        # Inherit base class behavior.
        super(NegotiateConnectionPacket,self).__init__()
        
        # Declare our type.
        self.PacketType = NegotiateConnection
        self._HasBody = True
    
        # No body attributes for this one, they're all engine constants.
    
    def SerializeBody(self):
        # Create a stream to work with
        data = cStringIO.StringIO()
        
        # Lots of version info.  But first, the protocol signature.
        data.write(ProtocolSignature)
        BinaryStructs.SerializeUint16(data, ProtocolRevision)
        BinaryStructs.SerializeUint16(data, Version.MajorVersion)
        BinaryStructs.SerializeUint16(data, Version.MinorVersion)
        
        # Return the body
        return data.getvalue()
    
    def DeserializeBody(self, stream):
        # check the protocol signature
        signature = stream.read(len(ProtocolSignature))
        if len(signature) != len(ProtocolSignature):
            raise IncompletePacket
        if signature != ProtocolSignature:
            raise CorruptPacket
        
        # check the version
        try:
            revision = BinaryStructs.DeserializeUint16(stream)
            major = BinaryStructs.DeserializeUint16(stream)
            minor = BinaryStructs.DeserializeUint16(stream)
        except BinaryStructs.EndOfFile:
            raise IncompletePacket
        except:
            msg = "Unhandled exception while deserializing packet type 0.\n\n"
            msg += traceback.format_exc()
            logging.error(msg)
            raise CorruptPacket
        if (revision != ProtocolRevision or major != Version.MajorVersion
            or minor != Version.MinorVersion):
            # no tolerance for different versions right now...
            raise VersionMismatch


class ConnectionAcceptedPacket(Packet):
    '''Packet class for the ConnectionAccepted packet type.'''
    
    ##
    ## packet constants
    ##
    Flag_NoRegister = 1
    '''Login screen flag indicating that in-client registration is disabled.'''
    
    def __init__(self):
        '''Creates a blank ConnectionAccepted packet.'''
        # Inherit base class behavior.
        super(ConnectionAcceptedPacket,self).__init__()
        self._HasBody = True
        
        # Declare body attributes.
        self.RegistrationDisabled = False
        '''If True, in-client registration is disabled.'''
        self.ServerName = u""
        '''Unicode string containing the server name.'''
        self.ServerNewsURL = u""
        '''Unicode string containing the server news URL.'''

    def SerializeBody(self):
        # create a buffer
        data = cStringIO.StringIO()
        
        # calculate the login screen flags
        flags = 0
        if self.RegistrationDisabled: flags |= self.Flag_NoRegister
        BinaryStructs.SerializeUint8(data, flags)
        
        # store the other fields
        try:
            BinaryStructs.SerializeUTF8(data, self.ServerName)
            BinaryStructs.SerializeUTF8(data, self.ServerNewsURL)
        except:
            raise IncompletePacket
        
        # return the packet
        retval = data.getvalue()
        data.close()
        return retval
    
    def DeserializeBody(self, stream):
        # read the values
        try:
            flags = BinaryStructs.DeserializeUint8(stream)
            self.ServerName = BinaryStructs.DeserializeUTF8(stream, 64)
            self.ServerNewsURL = BinaryStructs.DeserializeUTF8(stream, 256)
        except BinaryStructs.EndOfFile:
            raise IncompletePacket
        except BinaryStructs.MaxLengthExceeded:
            raise CorruptPacket
        except:
            msg = "Unhandled exception in DeserializeBody, packet type 1.\n\n"
            msg += traceback.format_exc()
            logging.error(msg)
            raise CorruptPacket
        
        # process the flags
        if flags & self.Flag_NoRegister: self.RegistrationDisabled = True
        else: self.RegistrationDisabled = False


class ConnectionRejectedPacket(Packet):
    '''
    Packet class for the ConnectionRejected packet type.
    '''
    
    ##
    ## Error Codes (documented in docs/protocol/protocol_core)
    ##
    Error_Other = 0
    Error_Outdated = 1
    Error_Revision = 2
    Error_Signature = 3
    Error_Banned = 4
    Error_SecurityUpdate = 5
    Error_NoSlots = 6
    
    
    def __init__(self):
        # Inherit base class behavior.
        super(ConnectionRejectedPacket, self).__init__()
        self._HasBody = True
        
        # Set packet type.
        self.PacketType = ConnectionRejected
        
        # Declare body values.
        self.RejectionCode = 0
        '''Error code for the rejected connection.'''
    
    def SerializeBody(self):
        # All we have to do is write the rejection code...
        data = cStringIO.StringIO()
        BinaryStructs.SerializeUint8(data, self.RejectionCode)
    
    def DeserializeBody(self, stream):
        # Read in the rejection code.
        try:
            self.RejectionCode = BinaryStructs.DeserializeUint8(stream)
        except BinaryStructs.EndOfFile:
            raise IncompletePacket
        except:
            msg = "Unhandled exception in DeserializeBody, packet type 2.\n\n"
            msg += traceback.format_exc()
            logging.error(msg)
            raise CorruptPacket


class KeepAlivePacket(Packet):
    '''Packet class for the KeepAlive packet type.'''
    
    def __init__(self):
        # Inherit base class behavior.
        super(KeepAlivePacket,self).__init__()
        
        # Set packet type.
        self.PacketType = KeepAlive


class SuccessPacket(Packet):
    '''Packet class for the Success packet type.'''
    
    def __init__(self):
        # Inherit base class behavior.
        super(SuccessPacket,self).__init__()
        self._HasBody = True
        
        # Set packet type.
        self.PacketType = Success
        
        # Declare body attributes.
        self.RequestSerial = 0
        '''Serial number of the request this is in reply to.'''
        self.ReasonCode = 0
        '''Success code, if applicable to the request.'''
    
    def SerializeBody(self):
        # Implemented from protocol documentation.
        data = cStringIO.StringIO()
        BinaryStructs.SerializeUint32(data, self.RequestSerial)
        BinaryStructs.SerializeUint16(data, self.ReasonCode)
        retval = data.getvalue()
        data.close()
        return retval
    
    def DeserializeBody(self, stream):
        # Read values.
        try:
            self.RequestSerial = BinaryStructs.DeserializeUint32(stream)
            self.ReasonCode = BinaryStructs.DeserializeUint16(stream)
        except BinaryStructs.EndOfFile:
            raise IncompletePacket
        except:
            msg = "Unhandled exception in DeserializeBody, packet type 4.\n\n"
            msg += traceback.format_exc()
            logging.error(msg)
            raise CorruptPacket


class FailedPacket(SuccessPacket):
    '''Packet class for the Failed packet type.'''
    
    def __init__(self):
        super(FailedPacket,self).__init__()
        self.PacketType = Failed


PacketTypes = {
               NegotiateConnection: NegotiateConnectionPacket,
               ConnectionAccepted: ConnectionAcceptedPacket,
               ConnectionRejected: ConnectionRejectedPacket,
               KeepAlive: KeepAlivePacket,
               Success: SuccessPacket,
               Failed: FailedPacket,
               }
'''
dict which maps packet types to the appropriate packet classes.

This maps directly to the classes, not to objects.

If you want to create a packet object of a known type, you can make a call to
C{xVLib.Packets.PacketTypes[type]()} to get a blank packet object.
'''


def BuildPacketFromStream(stream):
    '''
    Attempts to build a packet from a data stream.
    
    @raise IncompletePacket: Raised if not enough data is present.
    @raise CorruptPacket: Raised if something is wrong with the data.
    
    @return: A Packet object, or an object of a Packet subclass.
    '''
    # try peeking ahead at the packet type
    startpos = stream.tell()
    try:
        type = BinaryStructs.DeserializeUint16(stream)
        stream.seek(startpos)
    except:
        # not enough data, make sure we rewind
        stream.seek(startpos)
        raise IncompletePacket
    
    # check the type
    if type < 0 or type > MAX_VALID_PACKET:
        # packet type is out of bounds
        raise CorruptPacket
    
    # now build up a packet of the appropriate type
    try:
        PacketProto = PacketTypes[type]
    except KeyError:
        # unrecognized packet type
        raise CorruptPacket
    NewPacket = PacketProto()
    
    # and now fill in the packet with the data...
    NewPacket.DecodeFromData(stream)
    return NewPacket
