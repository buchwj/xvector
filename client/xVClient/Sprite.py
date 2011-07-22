# -*- coding: utf-8 -*-

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

"""
Classes that handle sprites, plus code to manage them.

Aside from lots of classes related to sprites, this module
also contains several functions that manage the collection
of SpriteSet objects.  After being loaded, these can be
accessed from anywhere, and any changes will be reflected
in all modules that import this module.
"""

from PyQt4 import QtCore, QtGui
import ConfigParser
import os
import re
import sys
import logging
import traceback

from . import ClientPaths

mainlog = logging.getLogger("Client.Main")

# And here, of course, are those nasty little global variables
# that we need in this case for cross-module sprite access.
spritesets = None
"""The dictionary of spritesets as loaded by LoadAllSprites()"""


class SpriteLoadFailure(Exception): pass
"""Raised if the sprites fail to load for any reason."""


class NonAnimationException(Exception): pass
'''Raised if SpriteInfoParser.GetAnimationBaseID() is called for a static sprite.'''


class SpriteInfoParser(object):
    """
    Loads metadata for different spritesheets.
    This is primarily used within the SpriteSet class
    to allow for sprites within the same type to be spread
    across multiple files and be different sizes.
    """

    # constants
    main_section = "SpriteSheet"
    credits_section = "Credits"

    def __init__(self, filepath):
        # Grab a config file parser to the metadata file
        cfgfilepath = ClientPaths.GetSpriteFile(filepath)
        self.parser = ConfigParser.SafeConfigParser(self.GetDefaults())
        self.parser.read(cfgfilepath)
        
        # Build the animation table
        self.animtable = []
        for i in range(self.animcount):
            self.animtable.append(self.GetAnimationBlock(i))
        
    @property
    def type(self):
        try:
            return self.parser.get(self.main_section, "Type")
        except ValueError:
            return ""

    @property
    def width(self):
        try:
            return self.parser.getint(self.main_section, "SpriteWidth")
        except ValueError:
            return 0

    @property
    def height(self):
        try:
            return self.parser.getint(self.main_section, "SpriteHeight")
        except ValueError:
            return 0

    @property
    def animcount(self):
        try:
            return self.parser.getint(self.main_section, "AnimationCount")
        except ValueError:
            return 0

    @property
    def author(self):
        try:
            return self.parser.get(self.credits_section, "Author")
        except ValueError:
            return ""

    @property
    def site(self):
        try:
            return self.parser.get(self.credits_section, "Site")
        except ValueError:
            return ""
    
    def GetAnimationBlock(self, n):
        '''
        Gets the boundaries of the given animation block.
        
        @type n: integer
        @param n: Sequence number of this animation in the file.
        
        @note:
        "Sequence ID" in this case refers to the position within the single
        file, with the top-left tile being 0 and increasing to the right.
        It is not the unique ID of the sprite in the full spriteset.
        
        @return: An integer tuple in the form of (starttile, endtile).
        '''
        # do we have this animation?
        animsect = "Animation" + str(n)
        if not self.parser.has_section(animsect):
            # nope
            raise IndexError("Animation " + str(n) + " not found.")
        
        # get animation information
        try:
            start = self.parser.getint(animsect, "Start")
            end = self.parser.getint(animsect, "End")
        except ConfigParser.Error as e:
            raise SpriteLoadFailure(e)
        if start < 0 or end < 0:
            raise SpriteLoadFailure("Animation " + str(n) + " is out of bounds.")
    
    def GetAnimationBaseID(self, n):
        '''
        Gets the animation sequence ID.
        
        @note:
        "Sequence ID" in this case refers to the position within the single
        file, with the top-left tile being 0 and increasing to the right.
        It is not the unique ID of the sprite in the full spriteset.
        
        @type n: integer
        @param n: Sequence ID of the sprite in question.
        
        @raise NonAnimationException
        Raised if the sequence given by C{n} is not an animation frame.
        
        @return: The sequence ID of the first frame of the animation.
        '''
        for start, end in self.animtable:
            if start <= n <= end:
                return start
        raise NonAnimationException

    def GetDefaults(self):
        """
        Returns a dictionary of the default values
        for a metafile.
        """
        defaults = dict()
        defaults['Type'] = "General"
        defaults['SpriteWidth'] = 32
        defaults['SpriteHeight'] = 32
        defaults['AnimationCount'] = 0
        return defaults


class Sprite(object):
    """
    A single sprite.
    """
    
    def __init__(self, width, height, type="General", id=0):
        """
        Initializes a new empty sprite with the given dimensions.
        
        Optionally, you can supply a type and ID number for the sprite.
        These can be set later through modifier methods.
        """
        # Initialize the QPixmap portion
        self._img = QtGui.QPixmap(width, height)
        '''Underlying pixmap to be rendered.'''
        
        # Clear to transparency (otherwise alpha-blending won't work later)
        self._img.fill(QtCore.Qt.transparent)
        
        # Declare some new attributes
        self.sprite_type = type
        """Type of this sprite (string)"""
        
        self.sprite_id = id
        """ID of this sprite (integer)"""
    
    @property
    def img(self):
        '''
        Property method for the underyling image data of the sprite.
        
        This is very useful in subclasses if overridden.  It allows the underlying
        image data to point to any pixmap and to change randomly.  For an example
        of when this is useful, see the AnimatedSprite subclass.
        '''
        return self._img
    
    @img.setter
    def img(self, newimg):
        self._img = newimg


class AnimatedSprite(Sprite):
    '''A sprite which consists of several frames.'''
    
    def __init__(self, width, height, delay=10):
        '''Initializes a blank animated sprite.'''
        # set up the underlying sprite infrastructure
        super(self, AnimatedSprite).__init__(width, height)
        
        # set our time-control variables
        self.delay = delay
        self.current_frame = 0
        
        # and set up our frameset
        self.frames = []
    
    @property
    def img(self):
        '''Property method for the current frame of the animation.'''
        return self.frames[self.current_frame]
    
    @img.setter
    def img(self, newimg):
        self.frames[self.current_frame] = newimg
    
    def PumpAnimation(self, curtime):
        '''
        Advances to the appropriate frame.
        
        Called from the main loop once per frame.
        
        @type curtime: integer
        @param curtime: Current engine "tick" (in milliseconds)
        
        @note:
        You should only expect the engine to call this about once every 25ms (f=40Hz).
        In other words, your sprite-based animations are limited to about 40 frames
        per second.  You probably won't need to go that high, though.
        '''
        # calculate stuff
        bigDelay = len(self.frames) * self.delay
        relativeTick = curtime % bigDelay
        self.current_frame = relativeTick // self.delay


class SpritesheetException(Exception): pass
"""Raised if a non-fatal error occurs while loading sprites."""


class SpriteSet(list):
    """
    Loads sprites from the appropriate directory and provides a mechanism
    to access them.

    A spriteset inherits from the Python C{dict}; as such, sprites
    can be accessed by their IDs using an expression of the form
    C{spriteset[id]}.  For example, to access sprite 5, the code would be
    C{spriteset[5]}.
    """

    def __init__(self):
        """
        Creates a spriteset with default values.
        """
        
        self.type = "General"
        '''The type of sprite contained in this set.'''
        
        self._idct = 1
        '''
        Counter variable used internally for ID assignment to multiple files.
        '''
        
        self._animations = []
        '''
        List of all animations contained in self.
        Used internally for framerate control.
        '''

    def LoadFile(self, metafile):
        """
        Loads sprites from a file.

        Do not call this function directly; call LoadSprites() instead,
        otherwise ID numbering orders may not be preserved, resulting
        in bugs.
        """
        # grab the metafile
        meta = SpriteInfoParser(metafile)
        
        start_id = self._idct
        this_file = 0

        # now grab the image file
        filepath = metafile[:len(metafile)-4] + "png"
        if not os.path.isfile(filepath):
            # its not a file? okay then...
            raise SpritesheetException(os.path.basename(filepath) \
                    + " does not exist.")
        sheet = QtGui.QPixmap(filepath)

        # check the dimensions - there must not be
        # any fractions of tiles in the sheet
        if sheet.width() % meta.width != 0:
            raise SpritesheetException(os.path.basename(filepath) \
                    + " contains fractional sprites.")
        if sheet.height() % meta.height != 0:
            raise SpritesheetException(os.path.basename(filepath) \
                    + " contains fractional sprites.")

        # get dimensions
        width = meta.width
        height = meta.height
        type = meta.type
        
        # add a blank sprite with id 0, if one does not exist
        if len(self) < 1:
            Blank = Sprite(width, height, type, 0)
            painter = QtGui.QPainter()
            painter.begin(Blank.img)
            clearBrush = QtGui.QBrush(QtGui.QColor(0,0,0,0))
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(clearBrush)
            targetRect = QtCore.QRect(0,0,width,height)
            painter.fillRect(targetRect, clearBrush)
            painter.end()
            self.append(Blank)

        # okay, let's start looping on through the set!
        # y-
        # ^
        # |              COORDINATE SYSTEM IN USE
        # +---> x+
        tiles_wide = sheet.width() // meta.width
        tiles_high = sheet.height() // meta.height
        for i in range(tiles_wide * tiles_high):
            # calculate all of our coordinates
            cur_xtile = i % tiles_wide
            cur_ytile = i // tiles_wide
            cur_xcoordUL = cur_xtile * meta.width
            cur_ycoordUL = cur_ytile * meta.height
            cur_xcoordBR = cur_xcoordUL + meta.width
            cur_ycoordBR = cur_ycoordUL + meta.height

            # extract the sprite
            try:
                # this will except if this isn't an animation frame
                baseID = meta.GetAnimationBaseID(i)
                
                # if we make it here, this is an animation.
                # create the new animation if this is the first frame
                if baseID > len(self):
                    anim = AnimatedSprite(width, height, type, self._idct)
                    self.append(AnimatedSprite(anim))
                    self._animations.append(anim)
                else:
                    # animation already exists, add a frame to it
                    anim = self[start_id + baseID]
                
                # load the frame
                frame = len(anim.frames)
                anim.frames[frame] = QtGui.QPixmap(width, height)
                anim.frames[frame].fill(QtCore.Qt.transparent)
                painter = QtGui.QPainter()
                painter.begin(anim.frames[frame])
                painter.drawPixmap(QtCore.QPoint(0,0), sheet,
                      QtCore.QRect(QtCore.QPoint(cur_xcoordUL,cur_ycoordUL),
                                   QtCore.QPoint(cur_xcoordBR,cur_ycoordBR)))
                painter.end()
            except NonAnimationException:
                # we have a static sprite
                newsprite = Sprite(width,height,type,self._idct)
                painter = QtGui.QPainter()
                painter.begin(newsprite.img)
                painter.drawPixmap(QtCore.QPoint(0,0), sheet,
                    QtCore.QRect(QtCore.QPoint(cur_xcoordUL,cur_ycoordUL),
                                 QtCore.QPoint(cur_xcoordBR,cur_ycoordBR)))
                painter.end()
                # record the sprite
                self.append(newsprite)
            finally:
                self._idct = self._idct + 1
        
    def PumpAnimation(self, curtime):
        '''
        Updates all animations in this spriteset to the correct frame.
        
        @type curtime: integer
        @param curtime: Current engine "tick" (in milliseconds).
        
        @note:
        You should only expect the engine to call this about once every 25ms (f=40Hz).
        In other words, your sprite-based animations are limited to about 40 frames
        per second.  You probably won't need to go that high, though.
        '''
        for anim in self._animations:
            anim.PumpAnimation(curtime)


class NoSpriteException(Exception): pass
'''Raised if a nonexistant sprite is requested.'''


class SpriteDirectoryNotFound(Exception): pass
'''Raised if no sprite directory can be found for the given server.'''


class SpriteManager(dict):
    '''
    Manages the sprites for a single server.
    
    This subclasses dict to allow easy access to the spritesets; this object
    maps the names of the spritesets to the spritesets.
    '''
    
    def __init__(self, name=None):
        '''
        Creates a new sprite manager and loads its sprites.
        
        If the server name is specified and a sprite directory for the server
        cannot be found, the default sprites will be loaded instead.  If the
        default sprites cannot be found, the SpriteDirectoryNotFound exception
        will be raised.
        
        @type name: string
        @param name: Name of server.  Set to None to use default sprites.
        
        @raise SpriteDirectoryNotFound: Raised if no sprite directories,
        including the default, can be found.
        '''
        # Declare attributes.
        self.ServerName = name
        '''Name of the server these sprites are connected to.'''
        
        self.SpriteDir = None
        '''Directory where the sprites are located.'''
        
        # Locate the sprite directory.
        if name != None:
            # It's a server-specific sprite directory.
            self.SpriteDir = os.path.join(ClientPaths.ServerResourceDir(name),
                                          ClientPaths.SpritesPrefix)
            if not os.path.isdir(self.SpriteDir):
                # Server sprite directory not found.
                msg = "Server sprite directory for %s not found." % name
                mainlog.error(msg)
                raise SpriteDirectoryNotFound
        else:
            # Default sprites.
            self.SpriteDir = os.path.join(ClientPaths.BaseMasterPath,
                                          ClientPaths.SpritesPrefix)
            if not os.path.isdir(self.SpriteDir):
                # Sprite directory not found.
                msg = "Default sprite directory not found at\n"
                msg += self.SpriteDir
                mainlog.error(msg)
                raise SpriteDirectoryNotFound
        
        # Load the sprites.
        self._LoadAllSprites()
    
    def _LoadSpriteType(self, type, fileprefix):
        '''
        Loads one type of sprite.
        '''
        # create the empty sprite set
        spriteset = SpriteSet()
        spriteset.type = type
    
        # enumerate the available resource files
        try:
            pattern = ClientPaths.GetRegexForExtension(".meta")
            potentials = os.listdir(self.SpriteDir)
            files = filter(pattern.match, potentials)
        except:
            # something went wrong
            msg = "The sprite directory could not be opened.\n\n"
            msg += "Details:\n" + traceback.format_exc()
            mainlog.error(msg)
            raise SpriteLoadFailure(msg)
    
        # check each file for a match
        pattern = re.compile(r"^" + fileprefix + r"(?P<id>\d+)\.meta$")
        matches = {}
        for fileobj in files:
            matched = pattern.match(fileobj)
            if matched == None:
                continue        # not a match!
            matches[int(matched.group("id"))] = fileobj
        
        # now load all of the items
        counter = 0
        for fileinfo in sorted(matches.items()):
            counter += 1
            filename = fileinfo[1]
            try:
                spritefile = os.path.join(self.SpriteDir, filename)
                spriteset.LoadFile(spritefile)
            except:
                # problem loading that one...
                counter -= 1
                err = "Failed to load spritesheet from %s.\n\n" % filename
                err += "Details:\n" + traceback.format_exc()
                mainlog.error(err)
        
        # Done!
        return spriteset
    
    def _LoadAllSprites(self):
        '''
        Loads the sprites from the sprite directory.
        '''
        # load the main sprites
        self['tiles'] = self._LoadSpriteType("tile", "tiles")
        self['items'] = self._LoadSpriteType("item", "items")
        self['npcs'] = self._LoadSpriteType("NPC", "npcs")
    
        # finally, add an empty "runtime" set for on-the-fly sprites
        self['runtime'] = SpriteSet()
        self['runtime'].type = "runtime"
