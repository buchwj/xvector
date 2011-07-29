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
Non-blocking interface to the HTTPFetcher utility.
'''

from subprocess import PIPE
import os.path
import re
import sys
import collections
import logging
from xVLib import Directories, async_subprocess
from . import ClientGlobals

mainlog = logging.getLogger("Client.Main")

PythonScriptRE = re.compile(r'\.py$')

class NoFetcherException(Exception): pass
'''Raised if HTTPFetcher cannot be found.'''


def _DetectHTTPFetcher():
    '''
    Attempts to detect the location of the HTTPFetcher script.
    
    @raise NoFetcherException: Raised if HTTPFetcher cannot be found.
    
    @return: Tuple containing the arguments needed to launch the script.
    '''
    # Make a list of possible fetchers.
    ScriptPath = os.path.dirname(__file__)
    PossibleFetchers = []
    if sys.platform == "win32":
        PossibleFetchers.append("HTTPFetcher.exe")
        PossibleFetchers.append(os.path.join(ScriptPath, "HTTPFetcher.exe"))
    PossibleFetchers.append("HTTPFetcher.py")
    PossibleFetchers.append(os.path.join(ScriptPath, "HTTPFetcher.py"))
    
    # Scan the possible fetchers.
    for fetcher in PossibleFetchers:
        if os.path.isfile(fetcher):
            # Found it... do we need to call Python on it?
            # (Yes, we could put #!/usr/bin/env python in the top of the
            #  script, but this doesn't work on Win32 and also depends on the
            #  user setting the executable bit on the script file.  Easier to
            #  invoke Python on the script directly.)
            if PythonScriptRE.search(fetcher):
                return (sys.executable, os.path.realpath(fetcher))
            else:
                return (os.path.realpath(fetcher),)
    
    # No fetcher found.
    raise NoFetcherException


class Retriever(object):
    '''
    Manages an instance of the HTTPFetcher.py script.
    
    Each instance of this object will create one HTTPFetcher instance.  By
    creating multiple instances of this object, you can fetch multiple files
    simultaneously.
    
    Keep in mind that each instance can only connect to a single server.  As
    a result, you need separate Retrievers for the metaserver, any automatic
    update servers, and any HTTP-based map file servers.
    '''
    
    ##
    ## Result Codes
    ##
    
    Result_OK = 0
    '''Result code passed to the callback when the request was successful.'''
    Result_NotFound = 404
    '''Result code passed to the callback when the server sent a 404.'''
    Result_Forbidden = 403
    '''Result code passed to the callback when the server sent a 403.'''
    Result_ServerError = 500
    '''Result code passed to the callback when the server sent a 500.'''
    Result_Failed = -1
    '''Result code passed to the callback when something else failed.'''
    Result_Crashed = -2
    '''Result code passed to the callback when HTTPFetcher crashed.'''
    
    def __init__(self, host, port, workingdir):
        '''
        Creates a new Retriever instance.
        
        @type host: string
        @param host: Name of host to connect to.
        
        @type port: integer
        @param port: Server port to connect to.
        
        @type workingdir: string
        @param workingdir: Working directory of the HTTPFetcher instance.
        
        @raise NoFetcherException: Raised if HTTPFetcher cannot be found.
        '''
        # Declare our attributes.
        self.Host = host
        '''Remote address to which this Retriever is connected.'''
        
        self.Port = port
        '''Remote port to which this Retriever is connected.'''
        
        self.Instance = None
        '''Handle to the HTTPFetcher instance.'''
        
        self.RequestQueue = collections.deque()
        '''Queue of pending requests to pass to the HTTPFetcher instance.'''
        
        self.CurrentRequest = None
        '''Request which the HTTPFetcher instance is currently processing.'''
        
        # If needed, create the working directory.
        self.WorkingDir = os.path.realpath(workingdir)
        '''
        Working directory of the HTTPFetcher instance.
        '''
        if not os.path.isdir(self.WorkingDir):
            Directories.mkdir(self.WorkingDir)
        
        # Spawn an instance of HTTPFetcher.py.
        self.Args = _DetectHTTPFetcher() + (self.Host, str(self.Port))
        '''Arguments which the HTTPFetcher was started with, as a tuple.'''
        self._RestartInstance()
        
        # Register for I/O processing.
        App = ClientGlobals.Application
        App.BackgroundProcessor.RegisterRetriever(self)
    
    def _RestartInstance(self):
        '''
        Force-restarts the HTTPFetcher instance with the same arguments.
        '''
        # do we need to terminate the current instance?
        if self.Instance:
            if self.Instance.returncode == None:
                self.Instance.kill()
            del self.Instance
        
        # we'll need to adjust any relative paths in our PYTHONPATH
        newpath = [os.path.realpath(x) for x in sys.path]
        strpath = ""
        for part in newpath:
            strpath += "%s%s" % (part, os.pathsep)
        strpath = strpath[:len(strpath)-len(os.pathsep)]
        environment = os.environ.copy()
        environment["PYTHONPATH"] = strpath
        self.Instance = async_subprocess.AsyncPopen(self.Args, stdin=PIPE,
                                                    stdout=PIPE, stderr=PIPE,
                                                    bufsize=1,
                                                    cwd=self.WorkingDir,
                                                    env=environment)
    
    def FetchResource(self, remotepath, localpath, callback_when_done):
        '''
        Asynchronously downloads a file to the local filesystem.
        
        The Retriever accomplishes this by queueing the request and immediately
        returning.  The request will be passed to the HTTPFetcher instance as
        soon as possible.  When the HTTPFetcher instance returns its reply, the
        Retriever instance will call the provided callback to inform you of the
        result.
        
        The provided callback can be any callable object (such as a method)
        that accepts two arguments: an integer representing the result code of
        the request, and a string containing the CRC32 checksum of the file.
        Try to keep the callback's runtime as short as possible; the Retriever
        instance will wait until it returns before moving on.  The recommended
        strategy for using callbacks is to somehow pass a message containing
        the result to the main loop so that your main code can execute it on
        the next cycle.
        
        @type remotepath: string
        @param remotepath: Remote path of file to retrieve.
        
        @type localpath: string
        @param localpath: Local path to write the file to.  This must be in the
        HTTPFetcher's working directory or a subdirectory thereof, otherwise
        the request will automatically fail.
        
        @type callback_when_done: callable object
        @param callback_when_done: Method to call when the request is complete.
        '''
        # enqueue the request
        request = (remotepath, localpath, callback_when_done)
        self.RequestQueue.append(request)
    
    def ProcessIO(self):
        '''
        Called from the main loop to handle I/O to and from the HTTPFetcher.
        
        This should be called once per cycle of the main loop.  It checks for
        completion of the current request, calls the request's callback if
        necessary, and submits a request to the HTTPFetcher if it is ready to
        accept a request.
        
        @raise FetcherCrashed: Raised if the HTTPFetcher instance crashed.
        '''
        # make sure HTTPFetcher hasn't crashed
        if self.Instance.poll() != None:
            # Okay, this is bad - it crashed.
            msg = "Retriever instance crashed, restarting."
            mainlog.warning(msg)
            if self.CurrentRequest:
                # Fail the request.
                self.CurrentRequest[2](self.Result_Crashed, None)
                self.CurrentRequest = None
            
            # Restart the instance.
            self._RestartInstance()
        
        # need to check for a response?
        if self.CurrentRequest:
            output, errors = self.Instance.communicate()
            if errors:
                # something went wrong with the request
                print errors
                code = int(errors.strip())
                self.CurrentRequest[2](code, None)
                self.CurrentRequest = None
            elif output:
                # success
                crc = output.strip()
                self.CurrentRequest[2](self.Result_OK, crc)
                self.CurrentRequest = None
        
        # need to push another request?
        if not self.CurrentRequest and len(self.RequestQueue) > 0:
            self.CurrentRequest = self.RequestQueue.popleft()
            request_str = "%s %s\n" % self.CurrentRequest[0:2]
            self.Instance.communicate(request_str)
    
    def Shutdown(self):
        '''
        Shuts down the HTTPFetcher instance.
        '''
        # Kill the process and wait for it to exit.  wait() should return
        # almost immediately since we're sending SIGTERM.  If we don't wait,
        # we'll get zombie processes, and that's not very good.
        self.Instance.terminate()
        self.Instance.wait()
        
        # Deregister.
        App = ClientGlobals.Application
        App.BackgroundProcessor.UnregisterRetriever(self)
    
    def __del__(self):
        '''
        Called right before object deletion.
        '''
        # Shut down if we haven't already.
        try:
            self.Shutdown()
        except:
            # Doesn't matter
            pass

