#!/usr/bin/env python

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
Subprocess utility that retrieves resources from an HTTP server.
The client spawns a process of this upon connection to a server if the
server instructs the client to retrieve maps from an independent HTTP server.

This is the backend to both the auto-updater and the HTTP map fetcher used by
the client.  We run this script as a subprocess in order to fetch resources
asynchronously (without blocking the GUI event loop).

Usage:
    $ ./HTTPFetcher.py <<host>> <<port>> <<basedir>>

    To update a file, write mapname and newline to stdin.
    If update successful, CRC32 checksum of file is written to stdout (with \n).
    If update fails, the HTTP error code is written to stderr (with newline).
        If the error was not HTTP related, the error code is -1.
    
    Requested resources must not begin with a slash or contain ".." anywhere in
    the path.  In addition, they can only contain letters, numbers, spaces, and
    the following characters: _-()./
    Resources requested which do not match these restrictions will not be
    retrieved, and an error code of -1 will be written to stderr.
'''

import sys
import httplib
import urllib
import zlib
import gzip
import StringIO
import traceback
import re
import os
from xVLib import Directories

# Globals

Connection = None
'''Main connection object.'''

# Functions

def BadArgsError():
    '''Called when invalid arguments are passed. Shows a warning and quits.'''
    print "This is a helper program for the xVector Engine Client."
    print "It retrieves up-to-date copies of maps from the server during"
    print "gameplay. You should not need to run this yourself; however, if"
    print "you really want to, documentation is in the source code."
    sys.exit(-1)

def InitConnection(host, port):
    '''
    Initializes the connection to the server.
    '''
    # configure globals
    global Connection
    
    # open connection
    Connection = httplib.HTTPConnection(host, port)

def Retrieve(host, port, url, outpath, recurse=0):
    '''
    Retrieves the requested resource from the server.
    '''
    # configure globals
    global Connection
    
    # have we exceeded our recursion limit?
    if recurse >= 3:
        # something went wrong, bail out
        return -1
    
    # first of all, check if the connection object even exists
    if not Connection:
        # create the connection object
        InitConnection(host, port)
    
    # Okay, now try to send the request.
    # This might fall through if the connection was dropped.
    try:
        headers = {
                   'Keep-Alive': '300', 
                   'Accept-Encoding': 'zlib, deflate',
                   'User-Agent': 'HTTPFetcher/0.1 (xVector Updater)',
                  }
        Connection.request("GET", url, None, headers)
    except httplib.NotConnected:
        # connection dropped; reconnect and recurse
        InitConnection(host, port)
        return Retrieve(host, port, url, outpath, recurse+1)
    except:
        # something else went wrong
        return -1
    
    # Now receive the response...
    try:
        response = Connection.getresponse()
        # Any good?  (Read the data early so we can make other requests.)
        data = response.read()
        if response.status != httplib.OK:
            # Something went wrong, return the status code.
            return response.status
        
        # Process the response
        if response.getheader('Content-Encoding',None) == 'deflate':
            # zlib deflate compression
            try:
                # decompress without header
                data = zlib.decompress(data, -15)
            except zlib.error as e:
                # decompression failed
                return -1
        elif response.getheader('Content-Encoding',None) == 'gzip':
            # gzip compression
            wrapper = StringIO.StringIO(data)
            gzipper = gzip.GzipFile(fileobj=wrapper)
            buf = gzipper.read()
            gzipper.close()
            data = buf
        
        # Create the directories that need to be created.
        dir = os.path.split(outpath)[0]
        if dir:
            Directories.mkdir(dir)
        
        # Okay, save the data to the file.
        # We _would_ use an atomic write here, but since 90% of the time we're
        # overwriting an existing file and os.rename() doesn't like to do that
        # on Windows, we don't bother.
        fileobj = file(outpath, "wb")
        fileobj.write(data)
        fileobj.close()
        return 0
    except:
        # some sort of connection problem - kill and try again
        try:
            Connection.close()
        except:
            # ignore any errors
            pass
        Connection = None
        return Retrieve(host, port, url, outpath, recurse+1)
        

if __name__ == "__main__":
    # validate command line arguments
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        basedir = urllib.quote(sys.argv[3])
        
        # do we need to add a beginning slash?
        if basedir[0] != '/':
            basedir = '/' + basedir
        
        # do we need to add a trailing slash?
        if basedir[-1] != '/':
            basedir += '/'
    except:
        BadArgsError()
    
    # enter our polling loop
    try:
        while True:
            # any requests on stdin?
            outpath = sys.stdin.readline().strip()
            if outpath:
                # validate outpath
                if not outpath:
                    # no request, no response
                    continue
                elif outpath[0] == '/':
                    # bad...
                    sys.stderr.write("-1\n")
                    sys.stderr.flush()
                    continue
                elif re.search(r"\.\.", outpath):
                    # looks like an attempt to modify higher-level files
                    sys.stderr.write("-1\n")
                    sys.stderr.flush()
                    continue
                elif re.search(r"[^a-zA-Z0-9./()_ \-]", outpath):
                    # we don't like those characters
                    sys.stderr.write("-1\n")
                    sys.stderr.flush()
                    continue
                
                # fetch the resource
                url = basedir + urllib.quote(outpath)
                try:
                    code = Retrieve(host, port, url, outpath)
                    if code == 0:
                        # Success! Calculate a CRC32 checksum.
                        fileobj = file(outpath, "rb")
                        crc = 0
                        while True:
                            # Read blocks of 32KB at a time.
                            chunk = fileobj.read(32768)
                            if not chunk:
                                break
                            crc = zlib.crc32(chunk, crc)
                        
                        # Dump the checksum to stdout, then move on.
                        sys.stdout.write("%X\n" % (crc & 0xffffffff))
                        sys.stdout.flush()
                    else:
                        # Something went wrong, report the error and move on.
                        sys.stderr.write(str(code) + "\n")
                        sys.stderr.flush()
                except:
                    # something really bad happened
                    sys.stderr.write("-1\n")
                    sys.stderr.flush()
    except:
        # clean up
        if Connection:
            try:
                Connection.close()
            except:
                # ignore
                pass
        sys.exit(0)
