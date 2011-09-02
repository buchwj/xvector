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
Code that manages the database engine.
'''

import logging
from sqlalchemy import create_engine

mainlog = logging.getLogger("Server.Main")


Engine = None
'''SQLAlchemy database engine.'''


Session = None
'''
Session class for SQLAlchemy.

This is initially defined in __init__.py for the xVServer package, but must be
bound to an engine following engine creation.
'''


MainSession = None
'''
Main Session instance for SQLAlchemy.

This is a Session object, NOT the return of sessionmaker().  For that, see the
Session variable.
'''


Base = None
'''
Declarative base object for SQLAlchemy.

This is initially defined in __init__.py for the xVServer package, but must be
bound to an engine following engine creation.
'''


class DatabaseStartupError(Exception): pass
'''Raised if the database engine cannot be started.'''


def _InitDB_sqlite(config):
    '''
    Initializes the sqlite database.
    
    @type config: xVLib.ConfigurationFile.ConfigurationFile
    @param config: Handle to the main configuration file object.
    '''
    # Construct the database URI.
    try:
        uri = "sqlite:///%s" % config['Database/Name']
    except KeyError:
        # Database improperly configured
        msg = "Database name must be specified for sqlite databases."
        mainlog.critical(msg)
        raise DatabaseStartupError
    
    # Connect to the database.
    global Engine, MainSession
    try:
        Engine = create_engine(uri)
    except Exception as err:
        msg = "Could not open sqlite database: %s" % err[0]
        mainlog.critical(msg)
        raise DatabaseStartupError
    Session.configure(bind=Engine)
    MainSession = Session()


def _InitDB_other(config):
    '''
    Initializes network database servers.
    
    @type config: xVLib.ConfigurationFile.ConfigurationFile
    @param config: Handle to the main configuration file object.
    '''
    # Make sure we have all of the settings. 
    try:
        type = config['Database/Type']
        username = config['Database/Username']
        password = config['Database/Password']
        host = config['Database/Host']
        port = config['Database/Port']
        dbname = config['Database/Name']
    except KeyError as err:
        msg = "Database configuration is incomplete: %s" % err[0]
        raise DatabaseStartupError
    
    # Authentication block.
    auth = ""
    if username != "": auth += username
    if password != "": auth += ":" + password
    if auth != "": auth += "@"
    
    # Address block.
    address = host
    if port > 0: address += ":" + str(port)
    
    # Put it all together.
    uri = "%s://%s%s/%s" % (type, auth, address, dbname)
    
    # Connect to database.
    global Engine, MainSession
    try:
        Engine = create_engine(uri)
    except Exception as err:
        msg = "Error connecting to database: %s" % err[0]
        mainlog.critical(msg)
        raise DatabaseStartupError
    Session.configure(bind=Engine)
    MainSession = Session()


def InitDB(config):
    '''
    Initializes the database connection.
    
    @type config: xVLib.ConfigurationFile.ConfigurationFile
    @param config: Handle to the main configuration file object.
    '''
    # Check database type
    if config['Database/Type'] == "sqlite":
        _InitDB_sqlite(config)
    else:
        _InitDB_other(config)


def CreateTables():
    '''
    Creates the tables.
    '''
    print "Creating database tables..."
    try:
        Base.metadata.create_all(Engine)
    except Exception as err:
        print "Error:", err[0]
