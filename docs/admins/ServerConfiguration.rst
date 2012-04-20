.. Documentation on the ServerConfiguration.xml file.

*************************
Server Configuration File
*************************

Introduction
============

Every server has its own server configuration file which stores some of the
highest-level settings.  This file tells the server how to run, where to find
any files it needs, etc.  If you are setting up a new server, you are advised
to start from a copy of the default ServerConfiguration.xml file and modify it
as necessary; this way, you ensure that all required settings are present.

Default Values
==============

Most options have a preset default value built into the server.  If for some
reason you would like to use the default value for a setting, you can either
omit the setting entirely or set its value to ``!!default!!``.  For example,
if you wanted to use the default database engine, the start of your Database
section might look something like this::

  <Database>
      <Type>!!default!!</Type>

General Section
===============

The general section contains the most basic server settings.  These are very
non-technical settings and allow you to greatly customize the way your server
is presented to players.

ServerName
----------

**This setting is required.**

The ServerName setting allows you to define a name for your server that will be
presented to players when they connect.  You can set this to whatever you want;
Unicode characters are supported, and there is no maximum length.

Example::

  <ServerName>Test Server</ServerName>

ServerNewsURL
-------------

The ServerNewsURL setting allows you to set an optional URL to a web page
containing the latest news related to your server.  This page will be displayed
to players on the login screen.  This is a great way to communicate information
about updates and special events to your players.

Example::

  <ServerNewsURL>http://www.xvector.org/official-server-news/</ServerNewsURL>

DisableRegistration
-------------------

This setting allows you to optionally disable the built-in registration
system.  Turning on this option will cause the server to reject any incoming
registration requests as well as instruct all clients to disable the
registration screen.  You may want to do this for a number of reasons; you
might want to restrict registrations during a closed beta, or you might want to
use your own registration form on your website.

This setting is disabled by default.

**Allowed Values:** True, False

Example::

  <DisableRegistration>True</DisableRegistration>

Database Section
================

The server needs to store all of its information somewhere.  It is rather
flexible about *where* the data is stored, however; all it needs is some sort
of SQL database, and it is perfectly happy to fall back on an SQLite file-based
database if no heavy-duty database servers are available.  This section of the
configuration file controls which database is used for storing data.

Type
----

**This setting is required.**

This setting tells the server what kind of database to use.  There are three
options that are suitable for most servers:

*sqlite*

  SQLite is the default database engine used by the server, and it is also the
  simplest option available.  SQLite stores all of its data to a file on the
  computer; no extra software is needed to make it work.  This simplicity comes
  at a price, however.  Its performance can be quickly degraded under larger
  loads, and it is not scalable to multiple servers.  SQLite is the recommended
  choice for development servers, but production servers are advised to use one
  of the two options below.

*mysql*

  MySQL is a very popular choice of database for production servers.  It is
  very easy to set up and use, and it can run on both Windows and Linux.  This
  is the recommended option for administrators with limited prior database
  experience.  If you choose this option, you'll need to set up a MySQL server;
  you can get the software from http://www.mysql.com.

*postgresql*

  PostgreSQL is another popular option of database for production servers.  It
  takes a bit more effort to set up and use than MySQL does, so it is not
  recommended for new server administrators.  There isn't really any advantage
  to choosing either MySQL or PostgreSQL over each other, so just choose
  whichever server you feel comfortable with.  If you choose this option,
  you'll need to set up a PostgreSQL server; you can get the software from
  http://www.postgresql.org.

**Allowed Values:** sqlite, mysql, postgresql, others\*

\*The server can use any database type supported by the SQLAlchemy library.

Example::

  <Type>sqlite</Type>

Host
----

This setting tells the server which host the database server is running on.
If you are using an SQLite database, leave this setting blank.  Otherwise, set
it to the host of the database server (often ``localhost`` if the database
server is running on the same machine).

Example::

  <Host>localhost</Host>

Port
----

This setting tells the server which port to connect to the database server on.
Unless your database server is running on a non-standard port for some reason,
you should leave this as the default.  This setting is not used with SQLite
databases.

Example::

  <Port>!!default!!</Port>

Name
----

**This setting is required.**

This setting tells the server which database to use.  For SQLite databases,
this should be set to the filepath to save the database file to.  For all other
database engines, this should be set to the name of the database on the server.

Example::

  <!-- A common development server setting for an SQLite database. -->
  <Name>xvector.sqlite</Name>
  
Username
--------

This setting tells the server which username to connect to the database server
as.  This setting is not used with SQLite databases.

Example::

  <Username>xvector</Username>

Password
--------

This setting tells the server which password to use when connecting to the
database server.  This setting is not used with SQLite databases.

Example::

  <!-- You should really pick a better password than this... -->
  <Password>12345</Password>

Resources
=========

The Resources section tells the server where resources such as map files are
located.  It also instructs the server on how to make these resources available
to connected players.

AutoUpdater
-----------

The xVector Engine client ships with a built-in autoupdater for game resources.
Your server can instruct any clients which connect to automatically download
the latest versions of resource files such as graphics and sound files.  This
setting allows you to control how this is accomplished.

The autoupdater requires you to host your resource files somewhere on a web
server.  The files must all be based in the same directory on the same server;
you cannot put half on one website and half on another.

The autoupdater is completely optional and disabled by default.

Enabled
^^^^^^^

This setting tells the server whether the autoupdater is enabled.
The default value is false.

**Allowed Values:** True, False

Example::

  <Enabled>True</Enabled>

URL
^^^

This setting tells the server what URL the autoupdater files are located
at.  You must place the files there yourself; the server only tells the client
where the files are located.  This must be a directory, not a specific file.
The trailing slash is optional.

Example::

  <URL>http://www.xvector.org/autoupdater/</URL>

ExternalMaps
------------

By default, the xVector Engine server will provide the latest copies of map
files to clients directly.  For larger production servers, however, this may be
an inefficient means of transferring the map files.  The server is not
optimized for transmitting files; as such, it is recommended that larger
servers host their map files on a separate Web server.  By setting the
appropriate ExternalMaps setings, the server can instruct the client on where
to acquire the latest map files.

The server will not replicate map files to the web server itself.  A utility
daemon/service is planned which will accomplish this task; at present, however,
it has not been created.  This feature will be available in an early release.

Enabled
^^^^^^^

This setting tells the server whether the map files should be provided to
clients from an external web server.  It is disabled by default.

**Allowed Values:** True, False

Example::

  <Enabled>False</Enabled>

URL
^^^

This setting tells the server where the external map files are located.  This
value is passed on to clients.  It has no effect if the external maps are not
enabled.  This should be a directory on a Web server, not an individual file.
The trailing slash is optional.

Example::

  <URL>http://www.xvector.org/externmaps/</url>

Network
=======

The Network section tells the server how to make use of the available network
resources.  Naturally, this is a highly technical section.  If you're unsure
about any of these settings, it is recommended to leave them as the defaults;
the default values have been chosen to allow the server to work straight out of
the box.

Address
-------

The Address section tells the server which network interfaces and which ports
to use.  It allows for independent configuration of IPv4 and IPv6 connectivity,
both of which support the following options.

Enabled
^^^^^^^

This setting tells the network engine whether or not to use this type of
internet protocol.  By default, the IPv4 protocol is enabled, and the IPv6
protocol is disabled.  At least one protocol must be enabled in order for the
server to function.

**Allowed Values:** True, False

Example::

  <Enabled>True</Enabled>

Interface
^^^^^^^^^

This setting tells the network engine which interface to listen on for a
particular internet protocol.  By default, these are set to the "global
interface" which listens on all interfaces ("0.0.0.0" for IPv4, or "::" for
IPv6).

Example::

  <Interface>127.0.0.1</Interface>

Port
^^^^

This setting tells the network engine which port to listen on for a particular
internet protocol.  The default port for all protocols is 24020; the only time
you should change this is if there is a conflict with this port, either on the
server machine or at the firewall.  Additionally, it is not recommended to use
any ports below 1024 or above 49151; these are reserved for other things.

Example::

  <Port>24020</Port>

Connections
-----------

This section tells the server how many connections to accept, both overall and
from each individual IP address.  This allows you to control how much traffic
your server handles at any given time, and helps you to prevent individual
users from hoarding all of the server resources.

Max
^^^

This setting tells the server how many total connections to allow at any given
time.  The default is 50 connections.

Example::

  <Max>50</Max>

PerIP
^^^^^

This setting tells the server how many connections to allow at once from any
single IP address.  IPv4 and IPv6 addresses are, of course, counted separately.
The default is 2 connections per address.

Example::

  <PerIP>2</PerIP>

Engine
------

This section is the most technical part of the network settings.  It tells the
server precisely how to operate the network engine.  Most of these settings are
only for performance-tuning purposes, and the average user will not need to
change these settings.

UsePoll
^^^^^^^

**Always set to False on Windows.**

This setting tells the server whether to use the poll() function to check for
any network connections that need to be operated on.  On servers with larger
numbers of connections, poll() is a more efficient way to do this; on smaller
servers, the default select() function is faster.  Which function works best
may vary from server to server.  poll() is not available on Windows.  The
default is False (that is, to use the select() function).

**Allowed Values:** True, False

Example::

  <UsePoll>False</UsePoll>

Logging
=======

This section tells the server how to keep logs of its activities.

Directory
---------

This setting tells the server where to store its log files.  It should be set
to a directory which is writable by the user as which the server is running.
If you leave this setting as "!!default!!", the server will select an
appropriate location for the platform on which the server is running; however,
it will make no attempt to find a location that is writable.  A trailing slash
is not necessary.

Example::

  <Directory>/var/log/xvector/</Directory>

Rotator
-------

This section tells the server how to rotate its log files.  Rotating log files
prevents any individual log file from growing too large to handle.  It also
greatly simplifies the process of backing up and removing older logs in order
to free up more disk space.

MaxSize
^^^^^^^

This setting tells the server what the maximum size of an individual log file
should be.  It is specified in bytes.  The default is 4194304 bytes, or 4 MB.

Example::

  <MaxSize>4194304</MaxSize>

LogCount
^^^^^^^^

This setting tells the server how many old log files to keep at a time before
it begins to delete the old ones.  The default is 10 log files.

Example::

  <LogCount>10</LogCount>
