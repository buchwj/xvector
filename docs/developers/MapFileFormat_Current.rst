.. Documentation for map file format (current version)

********************************
Map File Format, Current Version
********************************

Overview
========

This is the first version of the map file format.  Actually, it is
really a composite of many of the earliest formats built upon
each other; the format was kept as Revision 1 until the necessity of
backwards compatibility forced an advancement to Revision 2.

R1 is a very simple format and does not support much more than layered
tiles.  R1 does not support item placement or NPCs; these will be
added in later formats (or possibly later versions of R1).

As always, there are actually two different map file formats, one for
the client and one for the server.  Luckily for us, the server mapfile
is just an extended version of the client format - they're binary
compatible out to the beginning of the server data, and the client code
will ignore the server data altogether.  We do this so that we can hide
unnecessary information (ie. item locations, hidden triggers, etc.) from
the client to prevent cheating (the less the player knows, the better -
consider what would happen if the player could open up a local copy of
a map and find the destinations of all the teleporters in a teleport maze).
As such, server-specific data must come last so that it can be trimmed out
before the maps are sent off to the client.

One might ask why we use our own map file format instead of Python's excellent
pickle and cPickle modules.  The answer is quite simple: pickle was never
designed to be secure.  It's quite easy to construct a pickled object that,
when unpickled, will execute arbitrary code on the client machine.  Such an
implementation in a client-server game would allow a hacker to mount a
man-in-the-middle attack against a client by injecting a packet containing
a maliciously crafted "map" file; this could go as far as to download and
install a rootkit on the victim's machine.  This is not acceptable behavior,
and so we must implement our own map file format.

Individual Data Formats
=======================

Throughout this document you will find tables listing fields and their data
types.  Some of these data types (int, float, etc.) are self-explanatory.
Others (utf-8) require some elaboration due to their implementation.

To begin, it should be noted that all data (where applicable) in the map file
uses little-endian encoding.

UTF-8 strings (type utf-8 in this document) are variable-length strings aligned
with a single-byte width.  These strings are, of course, encoded using UTF-8.
They begin with a single 32-bit unsigned integer which indicate the length of
the encoded string, and are immediately followed by the encoded string.  For
a more formal description of the string format, see :ref:`string-format`.

Meta-Header
===========

Like all versions of the map file, the V1 format begins with the "meta-header".
It is used within xVLib to  identify the map file's version. It is universal to
all mapfile formats used by xVector; its structure does not change between
revisions of the mapfile format.

**Metaheader Structure**

+---------+-----------------------------------------------+
|Type     |Field                                          |
+=========+===============================================+
|uint32   |Magic number (0xB0501)                         |
+---------+-----------------------------------------------+
|uint32   |Version ID (1 for Revision 1 maps)             |
+---------+-----------------------------------------------+
|uint32   |Minimum version for backwards compatibility    |
+---------+-----------------------------------------------+
|uint32   |Content flags                                  |
+---------+-----------------------------------------------+

The content flags are a 32-bit integer containing XOR'd boolean values as
follows:

+---+------------------------------------------------------------------+
|Bit|Flag                                                              |
+===+==================================================================+
|0  |Stripped (set to true when the server has removed information in  |
|   |order to send this map to the client)                             |
+---+------------------------------------------------------------------+

Header
======

Immediately following the meta-header is the real header.  This header is more
likely to change between versions of the map file format, so we handle it
separately from the meta-header.

**Header Structure**

+---------+-------------------------------------------------+
|Type     |Field                                            |
+=========+=================================================+
|utf-8    |Map name (max length = unlimited)                |
+---------+-------------------------------------------------+
|uint32   |Map width, in tiles                              |
+---------+-------------------------------------------------+
|uint32   |Map height, in tiles                             |
+---------+-------------------------------------------------+
|uint32   |Map depth, in layers                             |
+---------+-------------------------------------------------+
|uint32   |Depth at which players and objects are rendered  |
+---------+-------------------------------------------------+
|utf-8    |Map connected by the north border                |
+---------+-------------------------------------------------+
|utf-8    |Map connected by the east border                 |
+---------+-------------------------------------------------+
|utf-8    |Map connected by the south border                |
+---------+-------------------------------------------------+
|utf-8    |Map connected by the west border                 |
+---------+-------------------------------------------------+
|utf-8    |Background image for the map                     |
+---------+-------------------------------------------------+
|sint16   |Background scroll rate in X (positive is right)  |
+---------+-------------------------------------------------+
|sint16   |Background scroll rate in Y (positive is down)   |
+---------+-------------------------------------------------+
|float    |Background parallax rate in X (positive is right)|
+---------+-------------------------------------------------+
|float    |Background parallax rate in Y (positive is down) |
+---------+-------------------------------------------------+

.. note:: All background-related options are ignored if any of the border maps
   are defined.  This is due to complications which may arise if bordering maps
   use different background parameters.  In such a situation, it is advised to
   merge the bordering maps into a single map and then set background settings
   for the combined map.

Tiles
=====

Next up are the tiles.  Each tile is given by a relatively simple structure
as described below.

**Tile Structure**

+---------+--------------------------------+
|Type     |Field                           |
+=========+================================+
|uint32   |Tile flags                      |
+---------+--------------------------------+
|uint32   |X coordinate of tile            |
+---------+--------------------------------+
|uint32   |Y coordinate of tile            |
+---------+--------------------------------+
|uint32   |Z coordinate of tile            |
+---------+--------------------------------+
|uint32   |ID number of tile sprite        |
+---------+--------------------------------+

The tile flags are a bitwise-OR'd combination of the following:

**Tile Flags**

+--------+--------------------------------------------------------------------+
|Bit     |Flag                                                                |
+========+====================================================================+
|0-29    |Unused                                                              |
+--------+--------------------------------------------------------------------+
|30      |End of tiles (notifies the loader that there are no more tiles)     |
+--------+--------------------------------------------------------------------+

These tile structures appear in the file one after the other.  They do not need
to be ordered by coordinates; the loader will sort them out during load.  The
tradeoff for this is a slightly larger filesize due to the stored coordinates,
but this is mostly insignificant.  Should the loader encounter a tile with x-
or y-coordinates that are out of the bounds given in the header, the tile will
be discarded and an exception raised; however, the loader will attempt to
continue loading the map file.

The loader will continue reading the tile structures until the End of Tiles
flag is read.  This flag should NOT be followed by the remaining fields; it is
taken to indicate the end of the tiles section (which is, in this early version 
of the map format, the last section).  Storing additional data beyond flag 31 
will result in a corrupt map file, and an exception will be raised if such data
is encountered.
