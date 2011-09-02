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
Account management code.
'''

from sqlalchemy import Column, Integer, String, Boolean, DateTime
import base64
import datetime
from . import Database

##
## A few constants...
##

UsernameMaxLength = 32
'''Maximum length of username.'''
EmailMaxLength = 64
'''Maximum length of email address.'''


class Account(Database.Base):
    '''
    User account.
    '''
    
    ##
    ## Database configuration
    ##
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    '''User ID.'''
    
    ##
    ## Login information
    ##
    Username = Column(String(UsernameMaxLength), unique=True, index=True)
    '''Username. Indexed for faster lookup.'''
    B64PasswordHash = Column(String(88))
    '''Password.  Stored as a base64-encoded salted SHA-512 hash.'''
    B64PasswordSalt = Column(String(24))
    '''Password salt, 16 bytes in length, encoded as base64.'''
    
    ##
    ## Extra information
    ##
    Email = Column(String(64))
    '''Email address associated with this account.'''
    
    ##
    ## Account standing information
    ##
    Enabled = Column(Boolean, default=True)
    '''Whether or not this account is enabled.'''
    Banned = Column(Boolean, default=False)
    '''Whether or not this account is banned.'''
    BanExpires = Column(DateTime)
    '''Time at which the ban on this account expires.'''
    
    ##
    ## Account creation information
    ##
    CreationTime = Column(DateTime)
    '''Time at which the account was created.'''
    CreatorIP = Column(String(45))
    '''IP address from which this account was created.'''
    
    ##
    ## Convenience properties
    ##
    
    @property
    def PasswordHash(self):
        '''Property for getting and setting the unencoded password hash.'''
        return base64.b64decode(self.B64PasswordHash)
    
    @PasswordHash.setter
    def PasswordHash(self, hash):
        self.B64PasswordHash = base64.b64encode(hash)
    
    @property
    def PasswordSalt(self):
        '''Property for getting and setting the unencoded password salt.'''
        return base64.b64decode(self.B64PasswordSalt)
    
    @PasswordSalt.setter
    def PasswordSalt(self, hash):
        self.B64PasswordSalt = base64.b64encode(hash)


class UsernameTaken(Exception): pass
'''Raised during registration if the username is already taken.'''


def Register(username, passwordhash, salt, email, creator):
    '''
    Registers a new account using the provided information.
    
    @type username: string (max length=32 characters)
    @param username: Username of the new account.
    
    @type passwordhash: string (length=64 characters)
    @param passwordhash: SHA-512 hash (unencoded) of salt + password.
    
    @type salt: string (length=16 characters)
    @param salt: Password salt to associate with this account.
    
    @type email: string (max length=64 characters)
    @param email: Email address to associate with this account.
    
    @type creator: string (max length=45 characters)
    @param creator: IP address that this registration is occurring from.
    
    @raise UsernameTaken: Raised if the username is already in use.
    @raise ValueError: Raised if any values are invalid.
    
    @return: The newly created account.
    '''
    # Check value lengths.
    if len(username) < 1 or len(username) > UsernameMaxLength:
        raise ValueError("Invalid username length")
    if len(passwordhash) != 64:
        raise ValueError("Password hash must be 64 characters in length.")
    if len(salt) != 16:
        raise ValueError("Password salt must be 16 characters in length.")
    if len(email) < 1 or len(email) > EmailMaxLength:
        raise ValueError("Invalid email length")
    if len(creator) < 1 or len(creator) > 45:
        raise ValueError("Invalid creator IP address length")
    
    # Check if the username is already in use.
    session = Database.MainSession
    query = session.query(Account).filter(Account.Username == username)
    if query.count() > 0:
        # Username is already in use
        raise UsernameTaken
    
    # Do a (very simple) check of the email address
    if email.find('@') == -1:
        raise ValueError("Invalid email address specified.")
    
    # Register!
    NewAccount = Account()
    NewAccount.Username = username
    NewAccount.PasswordHash = passwordhash
    NewAccount.PasswordSalt = salt
    NewAccount.Email = email
    NewAccount.CreatorIP = creator
    NewAccount.CreationTime = datetime.datetime.utcnow()
    
    session.add(NewAccount)
    session.commit()
    return NewAccount
