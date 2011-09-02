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
import datetime
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
    id = Column(Integer, primary_key=True)
    
    ##
    ## Internal IP address storage schema.
    ##
    Low64 = Column(BigInteger(unsigned=True), index=True)
    '''Low 64 bits of an IPv6 address.  Set to None for IPv4 addresses.'''
    Mid32 = Column(Integer(unsigned=True))
    '''"Middle" 32 bits of an IPv6 address.  Set to None for IPv4 addresses.'''
    High32 = Column(Integer(unsigned=True))
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
            self.CIDR = int(cidr)
                
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
            self.CIDR = int(cidr)
    
    def __repr__(self):
        return "<IPBanRecord (%s)>" % self.ToString()

    ##
    ## Ban check methods
    ##
    
    def ValidBan(self):
        '''
        Checks that this ban is valid (i.e. not expired).
        
        @return: Boolean.
        '''
        if self.Permanent: return True
        now = datetime.datetime.now()
        return now < self.Expires
    
    def MatchString(self, address):
        '''
        Matches an address as a string.
        
        @type address: string
        @param address: Address to check for match.
        
        @raise ValueError: Raised if an invalid address is supplied.
        '''
        # IPv4 or IPv6?
        if address.find(":") == -1:
            # IPv4
            try:
                packed = socket.inet_aton(address)
            except: raise ValueError
            return self.MatchPackedIPv4(packed)
        else:
            # IPv6
            try:
                packed = socket.inet_pton(socket.AF_INET6, address)
            except: raise ValueError
            return self.MatchPackedIPv6(packed)
    
    def MatchPackedIPv4(self, packed):
        '''
        Matches a packed IPv4 address (i.e. the return value of inet_aton).
        
        @type packed: string
        @param packed: Packed IPv4 address.
        
        @return: Boolean, True if the address matches this ban.
        '''
        # If this is an IPv6 address ban, automatically dematch.
        if self.Low64 > 0 or self.Mid32 > 0: return False
        
        # Extract address information.
        addr = _IPv4Struct.unpack(packed)[0]
        
        # Strip non-prefix bits.
        deltaCIDR = 32 - self.CIDR
        addr &= 0xffffffff - (2 ** deltaCIDR - 1)
        
        # Check for match.
        return addr == self.High32
    
    def MatchPackedIPv6(self, packed):
        '''
        Matches a packed IPv6 address (i.e. the return value of inet_pton).
        
        @type packed: string
        @param packed: Packed IPv6 address.
        
        @return: Boolean, True if the address matches this ban.
        '''
        # If this is an IPv4 address an, automatically dematch.
        if self.Low64 == 0 and self.Mid32 == 0: return False
        
        # Extract address information.
        low, mid, high = _IPv6Struct.unpack(packed)
        if (low == 0 and mid == 0) and (self.Low64 > 0 or self.Mid32 > 0):
            # This got passed an IPv4 address (why?), no match.
            return False
        
        # Figure out where the CIDR split is.
        if self.CIDR < 64:
            # Low 64
            deltaCIDR = 64 - self.CIDR
            high = 0
            mid = 0
            low &= 0xffffffffffffffff - (2 ** deltaCIDR - 1)
        elif self.CIDR < 96:
            # Mid 32
            deltaCIDR = 96 - self.CIDR
            high = 0
            mid &= 0xffffffff - (2 ** deltaCIDR - 1)
            # low = low
        else:
            # High 32
            deltaCIDR = 128 - self.CIDR
            high &= 0xffffffff - (2 ** deltaCIDR - 1)
            # mid = mid
            # low = low
        
        # Check for match.
        return high == self.High32 and mid == self.Mid32 and low == self.Low64


def _IsBanned_IPv4(address):
    '''
    Checks the database for a matching IPv4 ban record.
    
    @type address: string
    @param address: IPv4 address to check.
    
    @return: Boolean.
    '''
    # Query.
    session = Database.MainSession
    query = session.query(IPBanRecord).filter(IPBanRecord.Low64 == 0).all()
    for record in query:
        if record.MatchString(address): return True
    return False


def _IsBanned_IPv6(address):
    '''
    Checks the database for a matching IPv6 ban record.
    
    @type address: string
    @param address: IPv6 address to check.
    
    @return: Boolean.
    '''
    # Query.
    session = Database.MainSession
    query = session.query(IPBanRecord).filter(IPBanRecord.Low64 != 0).all()
    for record in query:
        if record.MatchString(address): return True
    return False


def IsBanned(address):
    '''
    Convenience function that checks the database for any matching ban records.
    
    @type address: string
    @param address: Address to check (either IPv4 or IPv6)
    
    @return: Boolean.
    '''
    # IPv4 or IPv6?
    if address.find(":") == -1:
        # IPv4
        return _IsBanned_IPv4(address)
    else:
        # IPv6
        return _IsBanned_IPv6(address)
