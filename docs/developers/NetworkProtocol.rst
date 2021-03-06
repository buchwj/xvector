.. Network protocol documentation.

****************
Network Protocol
****************

Introduction
============

This is the main documentation for the network protocol used by the xVector
Engine.  It is a TCP-based protocol with variable-length messages, and the
engine supports both IPv4 and IPv6 connections.

Despite using a stream-based socket type (TCP), the protocol is described as
being "packet-based".  Packets are written one at a time to the TCP stream, and
are guaranteed by the nature of TCP to arrive in the same order that they were
sent.

The client and server operate very differently from one another.  The engine's
network code is ultimately designed with one major principle in mind: "never
trust the client."  Clients can be tampered with by would-be hackers and
cheaters, so all processing must be done server-side.  The client and server
can be seen as analogous to a model/view framework: The client is the view,
displaying the game to the player, while the server acts as the model, managing
the data set behind the world.

With this in mind, the protocol is designed as a set of "requests" that the
client is allowed to make of the server.  When the server receives such a
request, it decides whether or not the request is allowed, and informs the
client of its decision as either "Success" or "Failed".  The server does not
have to provide a reason to the client for any failures.  Many requests are
simple enough that a simple "Success" or "Failed" will suffice as a reply.
Other requests are more complex in nature, and the server will reply with a
specialized packet if the operation succeeds.

To keep track of responses to requests, each request packet provides in its
body a 32-bit serial number.  When the server replies, it will set a "Reply"
flag in the packet header and refer to this serial number in the packet body.
This allows the client to keep track of which response is tied to which
request.

In the client code, requests are implemented as classes which have a number
of callback methods.  After being constructed, Request objects should be
passed to the RequestManager which assigns a serial number to the request,
creates an appropriate request packet, and dispatches it to the server.  When
the client receives a packet from the server which is flagged as a reply,
it is passed to the RequestManager for handling.  If the serial number of the
reply matches that of a pending Request object, the appropriate callback method
will be called by the RequestManager.

The server is more authoritative than the client.  Rather than making requests
and waiting for a confirmation or rejection, the server just pushes data out to
the clients.  It does not expect any acknowledgment from the client, except in
special cases where information is requested from the client (i.e. during a
connection negotiation or challenge-response login).

One important point regarding the formatting of data in the protocol must be
raised.  Data in the protocol is encoded as little-endian; this is the opposite
of traditional network byte order.  The reason for this is simply reusability
of code in the engine; the map file format, which was programmed first, uses
little-endian byte order.  In order to reuse the serialization code, the
network code must also use little-endian byte order.

Packet Structure
================

The overall structure of a packet is fairly simple; it consists of an four-byte
header followed by a body of variable length specific to the packet type.  The
body of the packet may be compressed using zlib (deflate); if this is the case,
it will be indicated in the packet header.

.. _string-format:

UTF-8 and Binary Strings
========================

Many packet types in this protocol require the use of either UTF-8 or binary
strings.  The protocol defines a common encoding structure for these types
which allows for variable-length strings.  This structure is described below.

**Variable-Length String Structure**

+----------+-------------------------------------------------+
|Type      |Field                                            |
+==========+=================================================+
|uint32    |length of string (bytes)                         |
+----------+-------------------------------------------------+
|bytes     |string (sequence of bytes with the given length) |
+----------+-------------------------------------------------+

Packet Header
=============

All packets begin with a header.  The header is four bytes in length and
consists of two unsigned 16-bit integers.  The structure is described below:

**Packet Header Structure**

+---------+------------------+
|Type     |Field             |
+=========+==================+
|uint16   |Packet type       |
+---------+------------------+
|uint16   |Packet flags      |
+---------+------------------+

The packet type field is simply an unsigned 16-bit integer corresponding to
the type ID of the packet.  Currently supported packet types are as follows.

**Supported Packet Types, Sorted by ID**

+-----+--------------------------------------------------+
|ID   |Type                                              |
+=====+==================================================+
|0    |NegotiateConnection (client -> server)            |
+-----+--------------------------------------------------+
|1    |ConnectionAccepted (server -> client)             |
+-----+--------------------------------------------------+
|2    |ConnectionRejected (server -> client)             |
+-----+--------------------------------------------------+
|3    |KeepAlive (both ways)                             |
+-----+--------------------------------------------------+
|4    |Success (server -> client)                        |
+-----+--------------------------------------------------+
|5    |Failed (server -> client)                         |
+-----+--------------------------------------------------+
|6    |StartLogin (client -> server)                     |
+-----+--------------------------------------------------+
|7    |LoginChallenge (server -> client)                 |
+-----+--------------------------------------------------+
|8    |FinishLogin (client -> server, request)           |
+-----+--------------------------------------------------+
|9    |Register (client -> server, request)              |
+-----+--------------------------------------------------+
|10   |AvailableCharacter (server -> client)             |
+-----+--------------------------------------------------+
|11   |StartCreateCharacter (client -> server, request)  |
+-----+--------------------------------------------------+
|12   |NewCharacterOptions (server -> client)            |
+-----+--------------------------------------------------+
|13   |FinishCreateCharacter (client -> server, request) |
+-----+--------------------------------------------------+
|14   |SelectCharacter (client -> server, request)       |
+-----+--------------------------------------------------+
|15   |SendMessage (client -> server)                    |
+-----+--------------------------------------------------+
|16   |ShowMessage (server -> client)                    |
+-----+--------------------------------------------------+
|17   |AddObject (server -> client)                      |
+-----+--------------------------------------------------+
|18   |DeleteObject (server -> client)                   |
+-----+--------------------------------------------------+
|19   |UpdateObject (server -> client)                   |
+-----+--------------------------------------------------+
|20   |GetMapCRC (client -> server)                      |
+-----+--------------------------------------------------+
|21   |MapCRC (server -> client)                         |
+-----+--------------------------------------------------+
|22   |GetMap (client -> server)                         |
+-----+--------------------------------------------------+
|23   |MapReply (server -> client)                       |
+-----+--------------------------------------------------+
|24   |InteractObject (client -> server, request)        |
+-----+--------------------------------------------------+
|25   |UpdateStats (server -> client)                    |
+-----+--------------------------------------------------+
|26   |UpdateInventory (server -> client)                |
+-----+--------------------------------------------------+
|27   |Disconnect (both ways)                            |
+-----+--------------------------------------------------+
|28   |StartMovement (client -> server)                  |
+-----+--------------------------------------------------+
|29   |EndMovement (client -> server)                    |
+-----+--------------------------------------------------+
|30   |MovementValid (server -> client)                  |
+-----+--------------------------------------------------+
|31   |MovementInvalid (server -> client)                |
+-----+--------------------------------------------------+
|32   |ServerInformation (server -> client)              |
+-----+--------------------------------------------------+
|33   |BadLogin (server -> client)                       |
+-----+--------------------------------------------------+
|34   |DeleteCharacter (client -> server, request)       |
+-----+--------------------------------------------------+
|35   |StartCharacterList (server -> client)             |
+-----+--------------------------------------------------+
|36   |InvalidRequest (server -> client)                 |
+-----+--------------------------------------------------+
|37   |UserNotFound (server -> client)                   |
+-----+--------------------------------------------------+

The packet flags are a set of bitwise flags XOR'd together into a 16-bit
integer.  These are general flags that describe the packet format and are
described below:

**Packet Header Flags**

+-------+-------------------------+
|Value  |Flag                     |
+=======+=========================+
|1      |zlib compression flag    |
+-------+-------------------------+

zlib Compression
================

If the zlib compression flag is set in the header, the entire packet body is
zlib-compressed.  This is stored in the packet in a sort of "meta-body", the
structure of which is described below.

**zlib meta-body structure**

+-------+----------------------------+
|Type   |Field                       |
+=======+============================+
|binary |compressed data             |
+-------+----------------------------+

Establishing a Connection
=========================

A connection is established through the use of the NegotiateConnection,
ConnectionAccepted, and ConnectionRejected packet types.  The main purpose of
these packets is to determine the version and format of the protocol used in
the connection.  As usual, the client doesn't have much say in the matter; if
the server doesn't like the protocol version offered by the client, the
connection is rejected.  Unlike most "Failed"-style responses, however, the
server actually provides the reason for the rejection (although only as a
simple one-byte error code).  The body structures of the three packet types
involved are described below.

**Body Structure, NegotiateConnection Packets**

+-------+-------------------------------------------------+
|Type   |Field                                            |
+=======+=================================================+
|uint16 |Protocol signature (A0 D0 for official protocol) |
+-------+-------------------------------------------------+
|uint16 |Protocol revision number                         |
+-------+-------------------------------------------------+
|uint16 |Engine major version number                      |
+-------+-------------------------------------------------+
|uint16 |Engine minor version number                      |
+-------+-------------------------------------------------+

Note: The protocol signature field is for differentiating between the official
protocol and any unofficial modifications.  A server which implements
customizations to the protocol should declare a different protocol signature to
ensure that only customized clients can connect.

**Body Structure, ConnectionAccepted Packets**
 
+--------+-------------------------------------------------+
|Type    |Field                                            |
+========+=================================================+
|uint8   |Login screen flags                               |
+--------+-------------------------------------------------+
|utf-8   |Server name (max length = 64 characters)         |
+--------+-------------------------------------------------+
|utf-8   |Server news URL (max length = 256 characters)    |
+--------+-------------------------------------------------+
|utf-8   |Server update URL (max length = 256 characters)  |
+--------+-------------------------------------------------+

**Body Structure, ConnectionRejected Packets**

+--------+------------------------------+
|Type    |Field                         |
+========+==============================+
|uint8   |Rejection code                |
+--------+------------------------------+

Connection negotiation is initiated by the client.  Immediately following
establishment of a TCP connection, the client must send a NegotiateConnection
packet to the server declaring its intentions.  This packet must be sent
prior to any other packets, including KeepAlive; should another type of packet
be received prior to successful negotiation, the server will close the
connection.

Once the server receives the NegotiateConnection packet, it will determine
whether or not it can support the client based on the version information
provided, along with whatever else it wants to decide with (a banned IP list,
for example).  Depending on its decision, it will reply with either
ConnectionAccepted or ConnectionRejected.  If it replies with the latter, it
will also provide a rejection code and then close the connection.  Rejection
codes are listed below.

**ConnectionRejected Rejection Codes**

+---------+-----------------------------------+
|Code     |Reason                             |
+=========+===================================+
|0        |Other error                        |
+---------+-----------------------------------+
|1        |Outdated engine version            |
+---------+-----------------------------------+
|2        |Unsupported protocol revision      |
+---------+-----------------------------------+
|3        |Protocol signature mismatch        |
+---------+-----------------------------------+
|4        |Banned                             |
+---------+-----------------------------------+
|5        |Engine security update required    |
+---------+-----------------------------------+
|6        |No available connection slots      |
+---------+-----------------------------------+

If, on the other hand, the server replies with a ConnectionAccepted packet,
it will provide UTF-8 strings containing the server name and a URL to the
server news feed.  Once the server sends the ConnectionAccepted packet, it
considers the connection to be active and will accept other packet types
(including KeepAlive).  This connection will be maintained until one side
sends a Disconnect packet or the server has not received any data from the
client in 60 seconds.

The ConnectionAccepted packet begins with a one-byte set of flags describing
the login process which the client must next complete.  The flags are listed
below.

**ConnectionAccepted, Login Screen Flags**

+----------+---------------------------------------------------+
|Value     |Flag                                               |
+==========+===================================================+
|1         |Registration disabled                              |
+----------+---------------------------------------------------+
|2         |Auto-updates enabled (server update URL required)  |
+----------+---------------------------------------------------+

KeepAlive
=========

There may be times when a connection is established but no information is
passed between client and server.  To prevent the server from thinking that
the connection has timed out, the client should send a KeepAlive packet after
30 seconds of inactivity.  The KeepAlive packet has no body structure.  When
the server receives a KeepAlive packet, it will reply with a KeepAlive packet
of its own.  If the client does not receive any data from the server within the
next 30 seconds (thus completing the 60-second timeout period), it should treat
the connection as dead and handle it as such.

Server Information
==================

The server has some global configuration values which must be communicated to
the client at various times.  The ServerInformation packet provides a mechanism
for pushing this information to the client whenever necessary.  It is not a
response to any other packet, and no response is expected from the client; it
only serves to inform the client of what the server is thinking.  Each packet
consists of a value code and a new value.  The structure is shown below.

**Body Structure, ServerInformation Packets**

+---------+-------------------------+
|Type     |Field                    |
+=========+=========================+
|uint16   |Value code               |
+---------+-------------------------+
|utf-8    |New value                |
+---------+-------------------------+

As the new value is stored in the packet as a Unicode string, you cannot safely
store binary data as a new value (if a byte has a value of 255, it will cause
the decoder to corrupt the data).  Instead, any binary data should be encoded
in base64 before being sent as the new value.  The actual type of the new value
depends on what value is being updated; this is indicated by the value code.  A
list of value codes is given below.

**ServerInformation Value Codes**

+--------+-------------+--------------------------------------------------+
|Code    |Value Type   |Value Name                                        |
+========+=============+==================================================+
|0       |utf-8        |Map mirror URL (default: none; "None" for none)   |
+--------+-------------+--------------------------------------------------+

The client should be ready to handle these notifications at any time, as there
are no restrictions on when the server may send them.

Requests: Success and Failed Packets
====================================

The Success and Failed packets are two of the most important packets in the
protocol.  Since the vast majority of client actions are requests needing no
specialized responses, Success and Failed are the two response packets most
commonly used by the server.  Each provide single 16-bit integer fields in
their bodies for passing reason codes to the client; the meaning of these
codes varies depending on the type of request made by the client.  Both
packets have identical body structures, given below.

**Body Structure, Success and Failed Packets**

+--------+--------------------------+
|Type    |Field                     |
+========+==========================+
|uint32  |Request serial            |
+--------+--------------------------+
|uint16  |Reason code               |
+--------+--------------------------+

In addition, the server can send an InvalidAction packet as a response.  This
is sent if a request is not permitted at a given time.  Its body structure is
described below.

**Body Structure, InvalidAction Packets**

+---------+-------------------+
|Type     |Field              |
+=========+===================+
|uint32   |Request serial     |
+---------+-------------------+

Login Process
=============

Login is accomplished by a challenge-response mechanism over TLS.  The login
process begins when, following a successful connection negotiation, the client
sends a StartLogin packet to the server.

**Body Structure, StartLogin Packet**

+-------+--------------------------+
|Type   |Field                     |
+=======+==========================+
|utf-8  |Username (max length = 32)|
+-------+--------------------------+

Immediately after the client sends this packet, it must begin negotiating
a TLS wrapper on top of the existing connection.  The server must also do
so; in order for the TLS layer to be established, both sides must negotiate
the layer.

Next, the server checks if the user exists.  If the user does not exist, a
UserNotFound packet is sent to the client (with no body), and the TLS wrapper
is removed.  Otherwise, the server generates a 32-byte login challenge and
sends it to the client with the user's salt in a LoginChallenge packet.

**Body Structure, LoginChallenge Packet**

+--------+-----------------------------------+
|Type    |Field                              |
+========+===================================+
|binary  |Challenge (length = 32)            |
+--------+-----------------------------------+
|binary  |Salt (length = 16)                 |
+--------+-----------------------------------+

Both sides must now compute the solution to the challenge as follows:

``
passhash := sha512(salt + password + salt)
solution := sha512(challenge + passhash + challenge)
``

The client has 15 seconds to compute and send the solution to the server.  It
is sent in a FinishLogin request to the server.

**Body Structure, FinishLogin Packet**

+---------+-------------------------------+
|Type     |Field                          |
+=========+===============================+
|uint32   |Request serial                 |
+---------+-------------------------------+
|binary   |Solution (length = 64)         |
+---------+-------------------------------+

As soon as the server receives this packet, it must remove the TLS wrapper from
the connection.  The server will then reply with the standard request response
packets.

Registration
============

The engine provides a simple mechanism for allowing players to create new
accounts through the client.  This is an optional feature, though it is enabled
by default; it may be disabled in the server configuration if another mechanism
(such as a web-based interface) will be used instead.  This section of the
protocol specification describes only the built-in registration mechanism; it
is up to the server operator to devise any alternative mechanisms if desired.

Note that the client should not attempt to register by this mechanism if the
server set the "registration disabled" flag in the ConnectionAccepted packet.
Any attempt to register made when registration is disabled in the server will
automatically result in a response of Failed.

Registration is fairly simple.  It occurs through a single request; the client
sends a Register packet containing basic account information.  It should be
noted that the password is not sent in plaintext with this method; it is hashed
with a salt on the client side before being transmitted to the server.  As
such, the client is responsible for generating both the salt and the hash.  The
hash should be computed using SHA-512; the salt should be 16 bytes long (any
other length will be rejected).  The password hash should be computed as follows:

``passhash := sha512(salt + password + salt)``

The structure of the Register packets is described below.

**Body Structure, Register Packets**

+----------+-----------------------------------------+
|Type      |Field                                    |
+==========+=========================================+
|uint32    |Request serial                           |
+----------+-----------------------------------------+
|utf-8     |Desired username (max length = 32)       |
+----------+-----------------------------------------+
|binary    |Password salt (length = 16)              |
+----------+-----------------------------------------+
|binary    |Password hash (length = 64)              |
+----------+-----------------------------------------+
|utf-8     |Email (max length = 64)                  |
+----------+-----------------------------------------+

When the server receives a Register packet, it will determine whether or not
the registration is valid; if it is, it will create a new account in the
database and send a Success packet (code=0).  Otherwise, it will send a Failed
packet with one of the following error codes:

**Registration Error Codes**

+---------+-----------------------------------------+
|Code     |Meaning                                  |
+=========+=========================================+
|0        |Invalid username                         |
+---------+-----------------------------------------+
|1        |Invalid password salt                    |
+---------+-----------------------------------------+
|2        |Invalid password hash                    |
+---------+-----------------------------------------+
|3        |Invalid email                            |
+---------+-----------------------------------------+
|4        |Username already taken                   |
+---------+-----------------------------------------+
|5        |Email already in use                     |
+---------+-----------------------------------------+
|6        |Registration disabled                    |
+---------+-----------------------------------------+

If the server sends a Success packet, it will automatically process the login,
and the client may continue as if it had successfully logged in.

Character Selection and Creation
================================

Once the client has successfully logged in, the server provides a list of
characters associated with the account.  The client may select to use or delete
any of these characters, or may optionally create a new character.  This
process begins immediately following login; the server will first send a
StartCharacterList packet (having no body structure) to instruct the client to
clear its displayed client list, then send an AvailableCharacter packet for
each character belonging to the account.  The structure of the
AvailableCharacter packet is described below.

**Body Structure, AvailableCharacter Packets**

+---------+-----------------------------------+
|Type     |Field                              |
+=========+===================================+
|utf-8    |Character name                     |
+---------+-----------------------------------+
|uint32   |Character level                    |
+---------+-----------------------------------+
|uint32   |Base sprite                        |
+---------+-----------------------------------+
|uint32   |Hair overlay sprite                |
+---------+-----------------------------------+
|uint32   |Body overlay sprite                |
+---------+-----------------------------------+
|uint32   |Legs overlay sprite                |
+---------+-----------------------------------+
|uint32   |Helmet overlay sprite              |
+---------+-----------------------------------+
|uint32   |Chest armor overlay sprite         |
+---------+-----------------------------------+
|uint32   |Legs overlay sprite                |
+---------+-----------------------------------+
|uint32   |Boots overlay sprite               |
+---------+-----------------------------------+
|uint32   |Gloves overlay sprite              |
+---------+-----------------------------------+
|uint32   |Weapon overlay sprite              |
+---------+-----------------------------------+
|uint32   |Offhand (shield) overlay sprite    |
+---------+-----------------------------------+

If the account has no characters associated with it, there will be no packets
of this type sent by the server.  The client now has several options:

 1) Select an existing character to use, sending a SelectCharacter request.
 2) Delete an existing character, sending a DeleteCharacter request.
 3) Create a new character, sending a StartCreateCharacter request.

Selecting a character is a simple process.  The client simply sends a
SelectCharacter request to the server and waits for a reply.  The body
structure of the SelectCharacter packet is shown below.

**Body Structure, SelectCharacter Packets**

+---------+---------------------------+
|Type     |Field                      |
+=========+===========================+
|uint32   |Request serial             |
+---------+---------------------------+
|utf-8    |Character name             |
+---------+---------------------------+

If the character exists and belongs to the account, the server will activate
the character and send a Success packet to the client.  Otherwise, the server
will send a Failed packet with an error code of 0.

Deleting a character works in a similar way.  The client sends a
DeleteCharacter request to the server, the structure of which is given below.

**Body Structure, DeleteCharacter Packets**

+---------+----------------------------+
|Type     |Field                       |
+=========+============================+
|uint32   |Request serial              |
+---------+----------------------------+
|utf-8    |Character name              |
+---------+----------------------------+

As before, the server will send Success if the deletion succeeds or Failed if
it did not.  If it sends Success, however, it will refresh the client's list by
sending a StartCharacterList followed by an AvailableCharacter packet for each
remaining character.  If no characters remain, only the StartCharacterList
packet will be sent.

Character creation is by far the most complex of the three operations.  The
client must first request to begin character creation by sending a 
StartCreateCharacter request (having no body structure) to the server.  If the
player already has the maximum number of characters, the server will send a
Failed packet with error code 0, and the process ends.  Otherwise, it will send
a Success packet followed by a NewCharacterOptions packet.  For right now there
is really only one option to be described: how many stat points are available
to be distributed.  The body structure of this packet is described below.

**Body Structure, NewCharacterOptions Packets**

+---------+------------------------------+
|Type     |Field                         |
+=========+==============================+
|uint16   |Stat points to distribute     |
+---------+------------------------------+

Once the client receives this packet, it can display the character creation
screen to the user.  This has significant potential to be a long period of
time without any communication; the client should still make sure to send
Keep-Alive packets during this time to prevent the connection from being
dropped.  Once the user has finished designing the character, the client sends
a FinishCreateCharacter request to the server containing the options selected
by the player.  The body structure of this packet is described below.

**Body Structure, FinishCreateCharacter Packets**

+---------+------------------------------------+
|Type     |Field                               |
+=========+====================================+
|utf-8    |Character name (max length = 32)    |
+---------+------------------------------------+
|uint32   |Strength                            |
+---------+------------------------------------+
|uint32   |Dexterity                           |
+---------+------------------------------------+
|uint32   |Constitution                        |
+---------+------------------------------------+
|uint32   |Agility                             |
+---------+------------------------------------+
|uint32   |Intelligence                        |
+---------+------------------------------------+
|uint32   |Wisdom                              |
+---------+------------------------------------+
|uint32   |Base sprite                         |
+---------+------------------------------------+
|uint32   |Hair overlay sprite                 |
+---------+------------------------------------+
|uint32   |Body overlay sprite                 |
+---------+------------------------------------+
|uint32   |Legs overlay sprite                 |
+---------+------------------------------------+

If the character is successfully created, the server will send a Success packet
followed by an AvailableCharacter packet for the new character.  Otherwise, it
will send a Failed packet with one of the following error codes.

**Error Codes, FinishCreateCharacter Request**

+----------+-----------------------------------------------+
|Code      |Meaning                                        |
+==========+===============================================+
|0         |Unknown error                                  |
+----------+-----------------------------------------------+
|1         |Invalid character name                         |
+----------+-----------------------------------------------+
|2         |Character name already in use                  |
+----------+-----------------------------------------------+
|3         |Invalid stat assignment                        |
+----------+-----------------------------------------------+
|4         |Invalid sprite selection                       |
+----------+-----------------------------------------------+
