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
Main processing loop of the server.

The server's main loop is implemented as a green thread; it runs in the
background when the I/O green threads are blocking.  It is guaranteed to yield
to other green threads at least once per cycle.
'''

import logging
import traceback

from xVServer import ServerNetworking

class MainLoopEnd(Exception): pass
'''Raised when the main loop is gracefully terminated.'''

mainlog = logging.getLogger("Server.Main")

def MainLoop():
    '''
    Main processing loop of the server.
    '''
    # enter loop
    mainlog.info("Server started.")
    try:
        while 1:
            # poll the network
            ServerNetworking.PollNetwork()
    except KeyboardInterrupt:
        # server interrupted... clean up after the try block
        pass
    except MainLoopEnd:
        # looks like we're done... clean up after the try block
        pass
    except:
        # UNHANDLED FATAL EXCEPTION!
        msg = "Unhandled exception in main loop.\n\n"
        msg += traceback.format_exc()
        mainlog.log(logging.FATAL, msg)
    finally:
        # clean up
        mainlog.info("Server shutting down.")
