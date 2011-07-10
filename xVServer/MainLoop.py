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

from gevent import Greenlet, sleep
import logging
import traceback

class MainLoopEnd(Exception): pass
'''Raised when the main loop is gracefully terminated.'''

mainlog = logging.getLogger("Server.Main")

class MainLoopThread(Greenlet):
    '''
    Greenlet that runs the main processing loop of the server.
    '''
    
    def __init__(self):
        '''
        Initializes the new greenlet.
        '''
        # Inherit base class behavior.
        Greenlet.__init__(self)

    def _run(self):
        '''
        Main processing loop of the server.
        '''
        mainlog.warning("Main loop launching!")
        # enter loop
        try:
            mainlog.warning("In try block...")
            while 1:
                # do processing stuff
                
                # yield to other green threads
                mainlog.warning("About to sleep...")
                sleep(0)
                mainlog.warning("Done sleeping...")
        except MainLoopEnd:
            # looks like we're done... clean up here
            pass    # TODO: Implement
        except:
            # UNHANDLED FATAL EXCEPTION!
            msg = "Unhandled exception in main loop.\n\n"
            msg += traceback.format_exc()
            mainlog.log(logging.FATAL, msg)
