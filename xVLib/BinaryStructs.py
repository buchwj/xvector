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
UintStruct = struct.Struct("<I")
"""Pre-made struct object for serialization of unsigned integers."""

SintStruct = struct.Struct("<i")
"""Pre-made struct object for serialization of signed integers."""

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
        raise IOError("Unexpected EOF reached while reading data.")
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
    widthbin = UintStruct.pack(width)
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
    widthbin = UnpackStruct(UintStruct, fileobj)
    
    # deserialize the string
    stringstruct = struct.Struct("<%ds" % widthbin)
    stringbin = fileobj.read(stringstruct.size)
    if len(stringbin) != stringstruct.size:
        # EOF
        raise IOError("EOF reached during deserialization")
    encoded = stringstruct.unpack(stringbin)[0]
    
    # decode and process the string
    decoded = encoded.decode('utf-8')
    if maxlen > 0 and len(decoded) > maxlen:
        decoded = decoded[:maxlen]
    return decoded


def SerializeUint(streamobj, uint):
    """
    Serializes an unsigned integer to a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to write to.
    
    @type uint: unsigned integer
    @param uint: Unsigned integer to write to stream.
    """
    tmpstr = UintStruct.pack(uint)
    streamobj.write(tmpstr)


def DeserializeUint(streamobj):
    """
    Deserializes an unsigned integer from a stream.
    
    @type streamobj: stream
    @param streamobj: Stream object (such as a file) to read from.
    
    @return: Unsigned integer that was read from the stream.
    """
    tmpstr = streamobj.read(UintStruct.size)
    return UintStruct.unpack(tmpstr)[0]
