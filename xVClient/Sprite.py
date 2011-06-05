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

import ClientPaths
import ErrorReporting

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


class SpriteSet(dict):
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
        self.sprites = list()
        '''Contains all of the sprites belonging to this set ordered by ID.'''
        
        self.type = "General"
        '''The type of sprite contained in this set.'''
        
        self._idct = 0
        '''
        Counter variable used internally for ID assignment to multiple files.
        '''
        
        self._animations = []
        '''
        List of all animations contained in self.sprites.
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
            width = meta.width
            height = meta.height
            type = meta.type
            
            try:
                # this will except if this isn't an animation frame
                baseID = start_id + meta.GetAnimationBaseID(i)
                
                # if we make it here, this is an animation.
                # create the new animation if this is the first frame
                if baseID not in self.sprites:
                    self.sprites[baseID] = AnimatedSprite(width, height,type,self._idct)
                    self._animations.append(self.sprites[baseID])
                anim = self.sprites[baseID]
                
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
                self[newsprite.sprite_id] = newsprite
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


class NoSpriteException(Exception):
    """
    Simple exception that is raised if a sprite
    that does not exist is requested.
    """
    pass


# We now move on to the cross-module support code.
# These functions can be called by treating the Sprite module as an object;
# doing so will preserve the state of the module across every module that
# calls it.

def _LoadSpriteType(type, fileprefix, basedir=""):
    """
    Loads one type of sprite.
    """
    # create the empty sprite set
    spriteset = SpriteSet()
    spriteset.type = type

    # enumerate the available resource files
    try:
        pattern = ClientPaths.GetRegexForExtension(".meta")
        potentials = os.listdir(ClientPaths.GetSpriteDir(basedir))
        files = filter(pattern.match, potentials)
    except Exception as e:
        # something went wrong
        msg = "The sprite directory could not be opened.\n\n"
        msg += "Details:\n" + str(e.args)
        ErrorReporting.ShowError(msg, ErrorReporting.FatalError)
        raise SpriteLoadFailure(msg)

    # check each file for a match
    pattern = re.compile(r"^" + fileprefix + r"(?P<id>\d+)\.meta$")
    matches = {}
    for f in files:
        matched = pattern.match(f)
        if matched == None:
            continue        # not a match!
        matches[int(matched.group("id"))] = f
    
    # now load all of the items
    counter = 0
    for fileinfo in sorted(matches.items()):
        counter += 1
        filename = fileinfo[1]
        try:
            spritefile = ClientPaths.GetSpriteFile(filename,basedir)
            spriteset.LoadFile(spritefile)
        except Exception as e:
            # problem loading that one...
            counter -= 1
            err = "Failed to load spritesheet from '" + filename + "'.\n\n"
            err += "Details:\n" + str(e.args[0])
            ErrorReporting.ShowError(err, ErrorReporting.FatalError)
            sys.exit()

    # Done!
    print "Found", counter, type, "spritesheets."
    return spriteset


def LoadAllSprites(basedir=""):
    """
    Loads all of the sprites for immediate access.
    """
    global spritesets
    spritesets = {}

    print "Loading sprites..."

    # load the main sprites
    spritesets['tiles'] = _LoadSpriteType("tile","tiles",basedir)
    spritesets['items'] = _LoadSpriteType("item","items",basedir)
    spritesets['npcs'] = _LoadSpriteType("NPC", "npcs",basedir)

    # finally, add an empty "runtime" set for on-the-fly sprites
    spritesets['runtime'] = SpriteSet()
    spritesets['runtime'].type = "runtime"

    # announce our success
    print "Sprites loaded."


def GetSpriteSet(type):
    """
    Returns a handle to the spriteset of the requested type.

    If no spriteset is found for the requested type, a KeyError will
    be raised.

    The currently supported types (by default) are C{tiles}, C{items},
    C{npcs}, and C{runtime}.
    
    @deprecated: Refactoring has made this unnecessary.  Will be removed
    at some point.  In the future, directly access the C{spritesets} member
    of this module.
    """
    # check the type
    global spritesets
    if type not in spritesets:
        # sorry, we don't have that type of sprite
        raise KeyError("Sorry, we don't have that type of sprite!")

    # get the spriteset
    return spritesets[type]
