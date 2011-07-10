# xVector Engine Core Library
# Copyright (c) 2010 James Buchwald
# (Except for the code in this file that is borrowed, as noted.)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""
Provides methods of encoding and decoding common binary data structures to and
from files.
"""

import struct

# Some common basic structs that are very useful to have on hand
Uint32Struct = struct.Struct("<I")
'''Pre-made struct object for serialization of unsigned 32-bit integers.'''

Sint32Struct = struct.Struct("<i")
'''Pre-made struct object for serialization of signed 32-bit integers.'''

Uint16Struct = struct.Struct("<H")
'''Pre-made struct object for serialization of unsigned 16-bit integers.'''

Sint16Struct = struct.Struct("<h")
'''Pre-made struct object for serialization of signed 16-bit integers.'''

class EndOfFile(IOError): pass
'''Special version of IOError for use when EOF is encountered.'''

def UnpackStruct(structobj, fileobj):
    """
    Reads and unpacks a struct from an open file object, performing needed
    error checking for cases such as EOF.
    
    @type structobj: C{struct.Struct}
    @param structobj: Compiled Struct object to use for unpacking
    
    @type fileobj: C{file}
    @param fileobj: Open file object to read in the data from
    
    @raise IOError: Raised if an EOF is reached unexpectedly.
    
    @return: A tuple containing all of the unpacked variables.
    """
    tmpstr = fileobj.read(structobj.size)
    if len(tmpstr) != structobj.size:
        raise EndOfFile
    return structobj.unpack(tmpstr)


def SerializeUTF8String(fileobj, string):
    """
    Serializes a string of variable length into a file using UTF-8 encoding.
    
    The string passed in can be either ASCII or Unicode.  In both cases it
    will be serialized to the file using the UTF-8 encoding.
    
    @type fileobj: C{file}
    @param fileobj: File object to serialize the string to.
    
    @type string: string
    @param string: String to serialize into the file.
    """
    # figure out what we're serializing
    toSerialize = str(string).encode('utf-8')
    width = len(toSerialize)
    
    # serialize
    widthbin = Uint32Struct.pack(width)
    stringbin = struct.pack("<%ds" % width, toSerialize)
    fileobj.write(widthbin)
    fileobj.write(stringbin)


def DeserializeUTF8String(fileobj, maxlen=0):
    """
    Deserializes a string of variable length from a file using UTF-8.
    
    @type fileobj: C{file}
    @param fileobj: File object to deserialize the string from.
    
    @type maxlen: integer
    @param maxlen: Maximum length of string to read in.  Anything extra
    will be truncated.  A value of zero allows unlimited length.
    
    @raise IOError: Raised if an EOF is hit during deserialization.
    
    @return: The deserialized Unicode string.
    """
    # figure out what we're deserializing
    widthbin = UnpackStruct(Uint32Struct, fileobj)
    
    # deserialize the string
    stringstruct = struct.Struct("<%ds" % widthbin)
    encoded = UnpackStruct(stringstruct, fileobj)
    
    # decode and process the string
    decoded = encoded.decode('utf-8')
    if maxlen > 0 and len(decoded) > maxlen:
        decoded = decoded[:maxlen]
    return decoded


def SerializeUint32(streamobj, uint):
    """
    Serializes an unsigned 32-bit integer to a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to write to.
    
    @type uint: unsigned 32-bit integer
    @param uint: Unsigned 32-bit integer to write to stream.
    """
    tmpstr = Uint32Struct.pack(uint)
    streamobj.write(tmpstr)


def DeserializeUint32(streamobj):
    """
    Deserializes an unsigned 32-bit integer from a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to read from.
    
    @return: Unsigned 32-bit integer that was read from the stream.
    """
    return UnpackStruct(Uint32Struct, streamobj)


def SerializeSint32(streamobj, sint):
    '''
    Serializes a signed 32-bit integer to a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to write to.
    
    @type sint: signed 32-bit integer
    @param sint: Signed 32-bit integer to write to stream.
    '''
    tmpstr = Sint32Struct.pack(sint)
    streamobj.write(tmpstr)


def DeserializeSint32(streamobj):
    '''
    Deserializes a signed 32-bit integer from a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to read from.
    
    @return: Signed 32-bit integer that was read from the stream.
    '''
    return UnpackStruct(Sint32Struct, streamobj)


def SerializeUint16(streamobj, uint):
    '''
    Serializes an unsigned 16-bit integer to a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to write to.
    
    @type uint: unsigned 16-bit integer
    @param uint: unigned 16-bit integer to write to stream.
    '''
    tmpstr = Uint16Struct.pack(uint)
    streamobj.write(tmpstr)


def DeserializeUint16(streamobj):
    '''
    Deserializes an unsigned 16-bit integer from a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to read from.
    
    @return: Unsigned 16-bit integer that was read from the stream.
    '''
    return UnpackStruct(Uint16Struct, streamobj)


def SerializeSint16(streamobj, sint):
    '''
    Serializes a signed 16-bit integer to a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to write to.
    
    @type sint: signed 16-bit integer
    @param sint: Signed 16-bit integer to write to stream.
    '''
    tmpstr = Sint16Struct.pack(sint)
    streamobj.write(tmpstr)


def DeserializeSint16(streamobj):
    '''
    Deserializes a signed 16-bit integer from a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to read from.
    
    @return: Signed 16-bit integer that was read from the stream.
    '''
    return UnpackStruct(Sint16Struct, streamobj)


def SerializeBinary(streamobj, binary):
    '''
    Serializes a chunk of binary data to a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to write to.
    
    @type binary: str
    @param binary: Binary data to write to the stream.
    '''
    binlen = len(binary)
    binstruct = struct.Struct("<%ds" % binlen)
    tmpstr = binstruct.pack(binary)
    SerializeUint32(streamobj, binlen)
    streamobj.write(tmpstr)


def DeserializeBinary(streamobj):
    '''
    Deserializes a chunk of binary data from a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to read from.
    
    @return: Binary data read from the stream.
    '''
    binlen = DeserializeUint32(streamobj)
    binstruct = struct.Struct("<%ds" % binlen)
    return UnpackStruct(binstruct, streamobj)


SerializeASCII = SerializeBinary
'''Function alias for ASCII serialization; no different from binary data.'''


DeserializeASCII = DeserializeBinary
'''Function alias for ASCII deserialization; same as binary data.'''
