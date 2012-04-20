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
Login processing with network code to support it.
'''

import time
import os
from xVLib import Packets
from . import ServerPacketRouter, Database, Accounts
from .Accounts import Account


##
## A few constants...
##

ChallengeLength = 32
'''Length of the random challenge, in bytes.'''

LoginDelay = 5
'''Minimum number of seconds between login attempts.'''


##
## Network handlers
##

class WaitForLoginRouter(ServerPacketRouter.BaseServerPacketRouter):
    '''
    Single-connection packet router for the wait-for-login state.
    '''
    
    def __init__(self):
        # Inherit from base class.
        super(WaitForLoginRouter, self).__init__()
        
        # Set up login handlers.
        self.Handlers[Packets.StartLogin] = StartLoginHandler
        self.Handlers[Packets.Register] = RegisterHandler


def GenerateChallenge():
    '''
    Generates a random login challenge.
    '''
    return os.urandom(ChallengeLength)

    
def StartLoginHandler(packet):
    '''
    Packet handler for the StartLogin packet type.
    
    @type packet: xVLib.Packets.StartLoginPacket
    @param packet: Packet to handle.
    '''
    # Check the timeout on the login.
    delta = time.time() - packet.Connection.LastLogin
    if delta < LoginDelay:
        # Timeout not complete.
        reply = Packets.BadLoginPacket(packet.Connection)
        reply.Reason = Packets.BadLoginPacket.Reason_WaitForLogin
        reply.SendPacket()
        return
    packet.Connection.LastLogin = time.time()
    
    # Does the account exist?
    session = Database.MainSession
    query = session.query(Account)
    account = query.filter(Account.Username==packet.Username).one()
    if not account:
        # Account does not exist, send BadLogin reply
        reply = Packets.BadLoginPacket(packet.Connection)
        reply.Reason = Packets.BadLoginPacket.Reason_BadUsername
        reply.SendPacket()
        return
    
    # Generate login challenge and send reply.
    packet.Connection.Account = account
    reply = Packets.LoginChallengePacket(packet.Connection)
    reply.Salt = account.PasswordSalt
    challenge = GenerateChallenge()
    packet.Connection.LoginChallenge = challenge
    reply.Challenge = challenge
    reply.SendPacket()
    
    # Adjust network state to accept challenge solutions.
    packet.Connection.SetState(packet.Connection.State_Login)


def RegisterHandler(packet):
    '''
    Packet handler for the Register packet type.
    
    @type packet: xVLib.Packets.RegisterPacket
    @param packet: Packet to handle.
    '''
    # Go ahead and try to register
    creator_ip = packet.Connection.Address[0]
    try:
        NewAccount = Accounts.Register(packet.Username,
                                       packet.PasswordHash,
                                       packet.Salt,
                                       packet.Email,
                                       creator_ip)
    except ValueError:
        pass
    except Accounts.UsernameTaken:
        pass
    except:
        pass


class LoginRouter(ServerPacketRouter.BaseServerPacketRouter):
    '''
    Single-connection packet router for the login state.
    '''
    
    def __init__(self):
        # Inherit from base class.
        super(LoginRouter, self).__init__()
        
        # Set up login handlers.
        # TODO: Implement
