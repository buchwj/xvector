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

import sys
import os
import logging
import traceback
from logging import handlers
from xml.etree.cElementTree import ParseError
from xVServer import ServerGlobals, MainLoop, ServerNetworking, ServerConfig
from xVServer import Database
from xVLib import Version
from xVLib.ConfigurationFile import ConfigurationFile

if sys.platform == "win32":
    import win32service, win32event
    import subprocess

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
        ##
        ## CLI configuration attributes
        ##
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
        self.CreateTables = False
        '''If set to True, will try to create DB tables and then exit.'''
        
        ##
        ## NT service configuration attributes (for Win32 only)
        ##
        if sys.platform == "win32":
            self.ServiceName = None
            '''Name of the NT service.'''
            self.InstallService = False
            '''If True, install the specified NT service.'''
            self.StartService = False
            '''If True, run as an NT service.'''
            self.UninstallService = False
            '''If True, uninstall the specified NT service.'''
        
        ##
        ## Runtime attributes
        ##
        self.Config = None
        '''Main configuration values, stored as a dict.'''
        self.ChatLogger = None
        '''Special logger for logging chat messages.'''
        self.EarlyHandler = None
        '''Early log handler.'''
        
        ##
        ## High-level network objects
        ##
        self.Connections = None
        '''Main connection manager.'''
        self.Servers = []
        '''Iterable list of network server objects.'''
        
        # set up early logging support
        self.EarlyHandler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        self.EarlyHandler.setFormatter(formatter)
        self.EarlyHandler.setLevel(logging.INFO)
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
                elif prevArg == "--service-name":
                    # value is the name of the NT service
                    self.ServiceName = arg
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
                elif arg == "--createtables":
                    self.CreateTables = True
                elif arg == "--service-install":
                    if sys.platform == "win32":
                        self.InstallService = True
                elif arg == "--service-start":
                    # "Hidden" command not shown in help.
                    # This should only be called by Windows when the service
                    # is started.
                    if sys.platform == "win32":
                        self.StartService = True
                elif arg == "--service-uninstall":
                    if sys.platform == "win32":
                        self.UninstallService = True
                elif arg == "--service-name":
                    if sys.platform == "win32":
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
        if self.DaemonMode and self.CreateTables:
            # can't mix these
            print "Cannot use --daemon and --createtables simultaneously."
    
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
        else:
            # NT service mode available
            print "\t--service-install\tInstall as an NT service."
            print "\t--service-uninstall\tUninstall the NT service."
            print "\t--service-name\t\tName of the NT service."
        
        print "\nDatabase management commands:"
        print "\t--createtables\t\tCreate all database tables and exit."
    
    def ShowVersionInfo(self):
        '''Shows the version information.'''
        args = (Version.MajorVersion, Version.MinorVersion,
                Version.LetterVersion)
        print "xVector Server %i.%02i%s" % args
    
    def ShowLicenseInfo(self):
        '''Shows the license information.'''
        print "NO WARRANTY.  Licensed under the GNU General Public License v2."
        print "You MUST accept the terms of the license to use the program."
        print "See the LICENSE file shipped with the program for the license."

    if sys.platform == "win32":
        
        def InstallService(self, name):
            '''
            Installs the server as an NT service with the given name.
            
            @type name: string
            @param name: Name of the NT service to install.
            '''
            # get handle to the service manager
            mgr = win32service.OpenSCManager(None,  # local computer
                                             None,
                                            win32service.SC_MANAGER_ALL_ACCESS)
            if mgr == None:
                err = "Could not get handle to service manager."
                mainlog.critical(err)
                raise _EarlyServerExit
            
            # figure out what command to use
            if __file__.find("library.zip") > 0:
                # running as frozen executable
                cmd = sys.executable
            else:
                # running as native script
                cmd = sys.executable + sys.argv[0]
            for arg in sys.argv[1:]:
                if arg == "--service-install":
                    continue
                cmd += " %s" % arg
            cmd += " --service-run"
            
            # create the service
            service = win32service.CreateService(
                                mgr,
                                self.ServiceName, self.ServiceName,
                                win32service.SERVICE_ALL_ACCESS,
                                win32service.SERVICE_WIN32_OWN_PROCESS,
                                win32service.SERVICE_AUTO_START,
                                win32service.SERVICE_ERROR_NORMAL,
                                cmd, None, None, None, None, None)
            if service == None:
                # failed to create the service
                mainlog.critical("Could not install the NT service.")
                win32service.CloseServiceHandle(mgr)
                raise _EarlyServerExit
            
            # clean up
            win32service.CloseServiceHandle(mgr)
            win32service.CloseServiceHandle(service)
        
        def UninstallService(self, name):
            '''
            Uninstalls the NT service with the given name.
            '''
            # grab a handle to the manager
            try:
                mgr = win32service.OpenSCManager(None, None,
                                            win32service.SC_MANAGER_ALL_ACCESS)
            except win32service.error as err:
                msg = "Failed to open service manager: %s" % err[2]
                mainlog.critical(msg)
                raise _EarlyServerExit
            
            # get a handle to the service
            try:
                svc = win32service.OpenService(mgr, name,
                                               win32service.SERVICE_ALL_ACCESS)
            except win32service.error as err:
                msg = "Failed to open service: %s" % err[2]
                mainlog.critical(msg)
                raise _EarlyServerExit
            
            # stop the service if needed
            state = win32service.QueryServiceStatus(svc)
            if state.dwCurrentState != win32service.SERVICE_STOPPED:
                try:
                    win32service.ControlService(svc, 
                                             win32service.SERVICE_CONTROL_STOP)
                except win32service.error as err:
                    msg = "Failed to stop service: %s" % err[2]
                    mainlog.error(msg)
            
            # delete the service
            try:
                win32service.DeleteService(svc)
            except win32service.error as err:
                msg = "Failed to remove service: %s" % err[2]
    
    def ConfigureLogger(self):
        '''Configures the logger.'''
        # We need a format...
        format = "%(asctime)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(format)
        
        # Configure the main logger.
        MainLogger = logging.getLogger("Server.Main")
        MainLogger.setLevel(logging.DEBUG)
        baselogpath = os.path.join(self.Config['Logging/Directory'],
                                   "main.log")
        maxbytes = self.Config['Logging/Rotator/MaxSize']
        maxlogs = self.Config['Logging/Rotator/LogCount']
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
        chatlogpath = os.path.join(self.Config['Logging/Directory'], 
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

    def InitNetwork(self):
        '''Initializes the network.'''
        # create the connection manager
        try:
            self.Connections = ServerNetworking.ConnectionManager()
        except:
            msg = "Could not create connection manager; server cannot start."
            mainlog.critical(msg)
            raise _EarlyServerExit
        
        # now initialize the network server objects
        try:
            # IPv4 and IPv6 use independent server objects
            if self.Config['Network/Address/IPv4/Enabled']:
                self.Servers.append(ServerNetworking.IPv4Server())
            if self.Config['Network/Address/IPv6/Enabled']:
                self.Servers.append(ServerNetworking.IPv6Server())
            
            # Make sure that there's at least one operational server object
            if len(self.Servers) < 1:
                msg = "At least one of either IPv4 or IPv6 must be enabled."
                mainlog.critical(msg)
                raise _EarlyServerExit
        except ServerNetworking.NetworkStartupError:
            msg = "Could not create network server; server cannot start."
            mainlog.critical(msg)
            raise _EarlyServerExit
        except _EarlyServerExit:
            raise
        except:
            msg = "Unhandled exception while creating network server.\n\n"
            msg += traceback.format_exc()
            mainlog.critical(msg)
            raise _EarlyServerExit
    
    def CleanupNetwork(self):
        '''Cleans up after the network.'''
        pass    # TODO: Implement

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
        transformers = ServerConfig.KnownTransformers
        try:
            self.Config = ConfigurationFile(self.ConfigFilePath,
                                        defaults=ServerConfig.DefaultValues,
                                        transformers=transformers)
        except IOError as err:
            # file i/o error
            args = (self.ConfigFilePath, err[1])
            msg = "Error reading configuration file %s: %s." % args
            mainlog.critical(msg)
            return -1
        except ParseError as err:
            # syntax error
            args = (self.ConfigFilePath, err)
            msg = "In configuration file %s: %s." % args
            mainlog.critical(msg)
            return -1
        
        # configure the logger
        self.ConfigureLogger()
        
        # start up the database engine
        try:
            Database.InitDB(self.Config)
        except:
            # bail out
            return -1
        
        # Any database management commands to execute?
        if self.CreateTables:
            Database.CreateTables()
            return 0
        
        # set up the network
        try:
            self.InitNetwork()
        except _EarlyServerExit:
            # bail out
            return -1
        
        # enter the main loop
        MainLoop.MainLoop()
        
        # clean up
        self.CleanupNetwork()
        logging.shutdown()
        
        # exit successfully
        return 0


def Main():
    '''Runs the application.'''
    # run the application
    ServerGlobals.Application = ServerApplication()
    app = ServerGlobals.Application
    retcode = app.Run()
    sys.exit(retcode)
