# xVector Engine Client
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
Asynchronous processing code that runs in the background of the client.
'''

import asyncore
from PyQt4 import QtCore


class BackgroundProcessor(QtCore.QObject):
    '''
    Manages tasks to be processed in the background.
    '''
    
    def __init__(self, parent=None):
        '''
        Creates a new background processor.
        '''
        # Inherit base class behavior.
        super(BackgroundProcessor,self).__init__(parent)
        
        # Declare attributes.
        self.Retrievers = set()
        
        # Tell the Qt event loop that we want to process in the background.
        self.startTimer(0)
    
    def RegisterRetriever(self, retriever):
        '''
        Registers a retriever for I/O processing.
        
        @type retriever: Retriever.Retriever
        @param retriever: Retriever object to register.
        '''
        # Do we already have this retriever?
        if retriever in self.Retrievers:
            # We have it, ignore
            return 
        
        # Register the retriever.
        self.Retrievers.add(retriever)
    
    def UnregisterRetriever(self, retriever):
        '''
        Unregisters a retriever.
        
        @type retriever: Retriever.Retriever
        @param retriever: Retriever object to unregister.
        '''
        # Do we have this retriever?
        if retriever in self.Retrievers:
            # Remove it.
            self.Retrievers.remove(retriever)
    
    def timerEvent(self, event):
        '''
        Called by the Qt event loop whenever we can do background processing.
        '''
        # Handle any pending network events.
        asyncore.loop(timeout=0, count=1)
        
        # Handle processing on all Retriever instances.
        try:
            for retriever in self.Retrievers:
                retriever.ProcessIO()
        except:
            # Sometimes we get errors from the iteration, that's OK
            pass
