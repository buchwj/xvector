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
Database-backed IP ban manager for both IPv4 and IPv6.

To manage our IP bans, we define ban records as a database table  Ban records
can either be permanent or temporary and can include a short comment explaining
the ban.  IP bans utilize CIDR notation to allow bans on ranges of addresses.
'''

import socket
import struct
from sqlalchemy import Column, Boolean, DateTime, String, BigInteger, Integer
from sqlalchemy import SmallInteger
from . import Database

_IPv4Struct = struct.Struct("!I")
_IPv6Struct = struct.Struct("!QII")


class IPBanRecord(Database.Base):
    '''
    Record for a single IP ban.
    '''
    
    ##
    ## Database configuration
    ##
    __tablename__ = "ipbans"
    
    ##
    ## Internal IP address storage schema.
    ##
    Low64 = Column(BigInteger(unsigned=True))
    '''Low 64 bits of an IPv6 address.  Set to None for IPv4 addresses.'''
    Mid32 = Column(Integer(unsigned=True))
    '''"Middle" 32 bits of an IPv6 address.  Set to None for IPv4 addresses.'''
    High32 = Column(Integer(unsigned=True), primary_key=True)
    '''High 32 bits of an IPv6 address, or the entire IPv4 address.'''
    CIDR = Column(SmallInteger(unsigned=True))
    '''CIDR notation prefix size.  0 to 32 for IPv4, 0 to 128 for IPv6.'''
    
    ##
    ## Ban time options
    ##
    Created = Column(DateTime)
    '''Date and time at which the ban was created.'''
    Permanent = Column(Boolean)
    '''If True, the ban is treated as permanent.'''
    Expires = Column(DateTime)
    '''Date and time at which the ban will expire.'''
    
    ##
    ## Misc. information
    ##
    Comment = Column(String(64))
    '''Optional comment explaining the reason for the ban.'''
    
    ##
    ## String conversion functions
    ##
    
    def ToString(self):
        '''
        Returns the banned address in CIDR notation.
        '''
        # IPv4 or IPv6?
        if self.Low64 != 0 or self.Mid32 != 0:
            # IPv6
            packed = _IPv6Struct.pack(self.Low64, self.Mid32, self.High32)
            address = socket.inet_ntop(socket.AF_INET6, packed)
            return "%s/%i" % (address, self.CIDR)
        else:
            # IPv4
            packed = _IPv4Struct.pack(self.High32)
            address = socket.inet_ntoa(packed)
            return "%s/%i" % (address, self.CIDR)
    
    def FromString(self, address):
        '''
        Fills in the database record from an address given in CIDR notation.
        
        @type address: string
        @param address: CIDR notation address to store.
        
        @raise ValueError: Raised if an invalid address is supplied.
        '''
        # IPv4 or IPv6?
        if address.find(":") == -1:
            # IPv4
            parts = address.split("/")
            if len(parts) > 2: raise ValueError
            elif len(parts) == 2: addr, cidr = parts
            else:
                # no CIDR prefix specified, assuming /32
                addr = parts[0]
                cidr = 32
            try:
                self.High32 = _IPv4Struct.unpack(socket.inet_aton(addr))[0]
            except: raise ValueError
            self.Low64 = 0
            self.Mid32 = 0
            self.CIDR = cidr
        else:
            # IPv6
            parts = address.split("/")
            if len(parts) > 2: raise ValueError
            elif len(parts) == 2: addr, cidr = parts
            else:
                # no CIDR prefix specified, assuming /128
                addr = parts[0]
                cidr = 128
            try:
                chunk = socket.inet_pton(socket.AF_INET6, addr)
            except: raise ValueError
            self.Low64, self.Mid32, self.High32 = _IPv6Struct.unpack(chunk)
            self.CIDR = cidr
    
    def __repr__(self):
        return self.ToString()
