#!/usr/bin/env python

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
Main script for the server.
'''

# MONKEY PATCHING!!!
from gevent import monkey; monkey.patch_all()

from gevent.pool import Pool
from gevent.server import StreamServer
import sys
import os
import logging
from logging import handlers
from xVServer import ServerGlobals, Configuration, MainLoop, ServerNetworking

mainlog = logging.getLogger("Server.Main")

class _EarlyServerExit(Exception): pass
'''
Raised to exit the server early (i.e. bad command line arguments).
'''

class ServerApplication(object):
    '''
    Main application class of the server.
    '''
    def __init__(self):
        '''Initializes a new server application.'''
        # declare CLI configuration attributes
        self.ConfigFilePath = ServerGlobals.DefaultConfigPath
        '''Path to the main configuration file.'''
        self.DaemonMode = False
        '''If True, the server will run as a daemon.'''
        self.DaemonUser = None
        '''If running in daemon mode, the user to run as.'''
        self.DaemonPid = None
        '''If running in daemon mode, the pidfile to use.'''
        self.DaemonPath = None
        '''If running in daemon mode, the path to run under.'''
        self.Config = None
        '''Main configuration values, stored as a dict.'''
        self.ChatLogger = None
        '''Special logger for logging chat messages.'''
        self.EarlyHandler = None
        '''Early log handler.'''
        
        # now our greenthreads and stuff like that...
        self.MainLoopThread = None
        '''Greenthread in which the main processing loop runs.'''
        self.NetworkPool = None
        '''Greenlet pool containing all of the connection handlers.'''
        
        # set up early logging support
        self.EarlyHandler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        self.EarlyHandler.setFormatter(formatter)
        self.EarlyHandler.setLevel(logging.WARN)
        mainlog.addHandler(self.EarlyHandler)
    
    def ParseCLIArgs(self):
        '''Parses the command line arguments.'''
        # Our state tracking variables...
        nextIsValue = False
        prevArg = None
        
        # Are there any command line arguments?
        if len(sys.argv) < 2:
            # no command line arguments, run defaults
            return
        
        # Loop through the arguments.
        for arg in sys.argv[1:]:
            if nextIsValue:
                # this is a value to the previous argument
                if prevArg == "--config":
                    # value is a configuration file path
                    self.ConfigFilePath = arg
                elif prevArg == "--daemon-user":
                    # value is the daemon user
                    self.DaemonUser = arg
                elif prevArg == "--daemon-pid":
                    # value is the daemon pidfile
                    self.DaemonPid = arg
                elif prevArg == "--daemon-path":
                    # value is the daemon root path
                    self.DaemonPath = arg
                nextIsValue = False
            else:
                # this is an argument
                prevArg = arg
                if arg == "--help":
                    self.ShowCLIHelp()
                    raise _EarlyServerExit
                elif arg == "--version":
                    self.ShowVersionInfo()
                    raise _EarlyServerExit
                elif arg == "--license":
                    self.ShowLicenseInfo()
                    raise _EarlyServerExit
                elif arg == "--config":
                    # next argument will be a value
                    nextIsValue = True
                elif arg == "--daemon":
                    # platform supported?
                    if sys.platform == "win32":
                        print "Error: Daemon mode not supported on Windows.\n"
                        self.ShowCLIHelp()
                        raise _EarlyServerExit
                    else:
                        self.DaemonMode = True
                elif arg == "--daemon-user":
                    # platform supported?
                    if sys.platform == "win32":
                        print "Error: Daemon mode not supported on Windows.\n"
                        self.ShowCLIHelp()
                        raise _EarlyServerExit
                    else:
                        nextIsValue = True
                elif arg == "--daemon-pid":
                    # platform supported?
                    if sys.platform == "win32":
                        print "Error: Daemon mode not supported on Windows.\n"
                        self.ShowCLIHelp()
                        raise _EarlyServerExit
                    else:
                        nextIsValue = True
                elif arg == "--daemon-path":
                    # platform supported?
                    if sys.platform == "win32":
                        print "Error: Daemon mode not supported on Windows.\n"
                        self.ShowCLIHelp()
                        raise _EarlyServerExit
                    else:
                        nextIsValue = True
                else:
                    # unknown argument.
                    print "Unrecognized argument %s\n" % arg
                    self.ShowCLIHelp()
                    raise _EarlyServerExit
        
        # any problems?
        if nextIsValue:
            # value wasn't completed...
            print "Argument %s must take a value.\n" % prevArg
            self.ShowCLIHelp()
            raise _EarlyServerExit
        if self.DaemonMode and not self.DaemonUser:
            # daemon configuration incomplete
            print "--daemon-user must be set if running in daemon mode.\n"
            self.ShowCLIHelp()
            raise _EarlyServerExit
        if self.DaemonMode and not self.DaemonPid:
            # use the default
            self.DaemonPid = "/var/run/xVServer"
        if self.DaemonMode and not self.DaemonPath:
            # use the default
            self.DaemonPath = "/"
    
    def ShowCLIHelp(self):
        '''Shows the command line help arguments.'''
        print "Usage: %s [args]\n" % sys.argv[0]
        print "Allowed arguments:"
        print "\t--help\t\t\tShow this message."
        print "\t--version\t\tShow version information."
        print "\t--license\t\tShow license information."
        print "\t--config [file]\t\tSet main configuration file."
        if sys.platform != "win32":
            # daemon mode available
            print "\t--daemon\t\tRun as daemon."
            print "\t--daemon-user [user]\tUser to run daemon as."
            print "\t--daemon-pid [file]\tPID file to track daemon with."
            print "\t--daemon-path [dir]\tPath to run daemon under."
    
    def ShowVersionInfo(self):
        '''Shows the version information.'''
        args = (ServerGlobals.MajorVersion, ServerGlobals.MinorVersion,
                ServerGlobals.LetterVersion)
        print "xVector Server %i.%02i%s" % args
    
    def ShowLicenseInfo(self):
        '''Shows the license information.'''
        print "NO WARRANTY.  Licensed under the GNU General Public License v2."
        print "You MUST accept the terms of the license to use the program."
        print "See the LICENSE file shipped with the program for the license."
    
    def ConfigureLogger(self):
        '''Configures the logger.'''
        # We need a format...
        format = "%(asctime)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format)
        
        # Configure the main logger.
        MainLogger = logging.getLogger("Server.Main")
        MainLogger.setLevel(logging.DEBUG)
        baselogpath = os.path.join(self.Config['Logging.Directory.Path'],
                                   "main.log")
        maxbytes = self.Config['Logging.Rotator.MaxSize']
        maxlogs = self.Config['Logging.Rotator.LogCount']
        MainHandler = handlers.RotatingFileHandler(baselogpath,
                                                           maxBytes=maxbytes,
                                                           backupCount=maxlogs)
        MainHandler.setFormatter(formatter)
        MainFilter = logging.Filter("Server.Main")
        MainHandler.addFilter(MainFilter)
        MainLogger.addHandler(MainHandler)
        
        # Configure the chat logger.
        ChatLogger = logging.getLogger("Server.Chat")
        ChatLogger.setLevel(logging.INFO)
        chatlogpath = os.path.join(self.Config['Logging.Directory.Path'],
                                   "chat.log")
        ChatHandler = handlers.RotatingFileHandler(chatlogpath,
                                                           maxBytes=maxbytes,
                                                           backupCount=maxlogs)
        ChatFilter = logging.Filter("Server.Chat")
        ChatHandler.addFilter(ChatFilter)
        ChatHandler.setFormatter(formatter)
        ChatLogger.addHandler(ChatHandler)
    
    def GoDaemon(self, user):
        '''
        Switches to daemon mode. (Not supported on Win32)
        
        @type user: string
        @param user: Username or UID (as string) of user to run daemon as.
        '''
        # Make sure this isn't win32.
        if sys.platform == "win32":
            mainlog.critical("Daemon mode not supported on Win32.")
            raise _EarlyServerExit
        
        # This is awkward, but use an in-method import...
        # (We'll only ever call this once, so it's okay)
        try:
            import daemon
        except ImportError:
            # looks like python-daemon isn't installed
            msg = "Package 'python-daemon' required for daemon mode."
            mainlog.critical(msg)
            raise _EarlyServerExit
        try:
            import lockfile
        except ImportError:
            # looks like python-lockfile isn't installed
            msg = "Package 'python-lockfile' required for daemon mode."
            mainlog.critical(msg)
            raise _EarlyServerExit
        import pwd
        
        # Set up the daemon...
        context = daemon.DaemonContext()
        try:
            if user.isdigit():
                record = pwd.getpwuid(int(user))
            else:
                record = pwd.getpwnam(user)
        except KeyError:
            msg = "Daemon user %s not found." % user
            mainlog.critical(msg)
            raise _EarlyServerExit
        uid, gid = record[2:4]
        if uid == 0:
            # root? no way
            msg = "Daemon cannot be run as user root."
            mainlog.critical(msg)
            raise _EarlyServerExit
        context.uid = uid
        context.gid = gid
        context.working_directory = self.DaemonPath
        context.pidfile = lockfile.FileLock(self.DaemonPid)
        
        # And off we go!
        with context:
            return self._Run_Core()

    def Run(self):
        '''Runs the application.'''        
        try:
            # parse command line arguments
            self.ParseCLIArgs()
            
            # switch to daemon mode if necessary
            if self.DaemonMode and self.DaemonUser:
                return self.GoDaemon(self.DaemonUser)
            else:
                return self._Run_Core()
        except _EarlyServerExit:
            # bail out
            return -1
        
    def _Run_Core(self):
        '''Runs the main part of the application.'''
        # okay, now let's try loading the main configuration file
        self.Config = Configuration.LoadConfigFile(self.ConfigFilePath)
        if not self.Config:
            # bail out
            return -1
        
        # configure the logger
        self.ConfigureLogger()
        
        # create the main loop greenlet
        self.MainLoopThread = MainLoop.MainLoopThread()
        self.MainLoopThread.start()
        
        # create the network greenlet pool
        self.MainLoopThread.join()
        
        # clean up
        logging.shutdown()
        
        # exit successfully
        return 0


if __name__ == "__main__":
    # run the application
    ServerGlobals.Application = ServerApplication()
    app = ServerGlobals.Application
    retcode = app.Run()
    sys.exit(retcode)
