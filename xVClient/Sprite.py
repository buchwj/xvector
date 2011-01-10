# xVector Engine Client
# Copyright (c) 2010 James Buchwald

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

import ClientPaths
import ErrorReporting

# And here, of course, are those nasty little global variables
# that we need in this case for cross-module sprite access.
_spritesets = None
"""The dictionary of spritesets as loaded by LoadAllSprites()"""


class SpriteLoadFailure(Exception): pass
"""Raised if the sprites fail to load for any reason."""


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
        
    @property
    def type(self):
        return self.parser.get(self.main_section, "Type")

    @property
    def width(self):
        return self.parser.getint(self.main_section, "SpriteWidth")

    @property
    def height(self):
        return self.parser.getint(self.main_section, "SpriteHeight")

    @property
    def author(self):
        return self.parser.get(self.credits_section, "Author")

    @property
    def site(self):
        return self.parser.get(self.credits_section, "Site")

    def GetDefaults(self):
        """
        Returns a dictionary of the default values
        for a metafile.
        """
        defaults = dict()
        defaults['Type'] = "General"
        defaults['SpriteWidth'] = 32
        defaults['SpriteHeight'] = 32
        return defaults


class Sprite(QtGui.QPixmap):
    """
    A single sprite.
    
    This can be used directly as a QPixmap for rendering, but it
    also contains additional information related to the sprite.
    """
    
    def __init__(self, width, height, type="General", id=0):
        """
        Initializes a new empty sprite with the given dimensions.
        
        Optionally, you can supply a type and ID number for the sprite.
        These can be set later through modifier methods.
        """
        # Initialize the QPixmap portion
        super(Sprite, self).__init__(width,height)
        
        # Clear to transparency (otherwise alpha-blending won't work later)
        self.fill(QtGui.QColor("transparent"))
        
        # Declare some new attributes
        self.sprite_type = type
        """Type of this sprite (string)"""
        
        self.sprite_id = id
        """ID of this sprite (integer)"""


class SpritesheetException(Exception): pass
"""Raised if a non-fatal error occurs while loading sprites."""


class SpriteSet(dict):
    """
    Loads sprites from the appropriate directory and provides a mechanism
    to access them.

    A spriteset actually inherits from the Python C{dict}; as such, sprites
    can be accessed by their IDs using an expression of the form
    C{spriteset[id]}.  For example, to access sprite 5, the code would be
    C{spriteset[5]}.
    """

    def __init__(self):
        """
        Creates a spriteset with default values.
        """
        self.sprites = list()
        self.type = "General"
        self._idct = 0

    def LoadFile(self, metafile):
        """
        Loads sprites from a file.

        Do not call this function directly; call LoadSprites() instead,
        otherwise ID numbering orders may not be preserved, resulting
        in bugs.
        """
        # grab the metafile
        meta = SpriteInfoParser(metafile)

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
            newsprite = Sprite(width,height,type,self._idct)
            self._idct = self._idct + 1
            painter = QtGui.QPainter()
            painter.begin(newsprite)
            painter.drawPixmap(QtCore.QPoint(0,0), sheet,
                QtCore.QRect(QtCore.QPoint(cur_xcoordUL,cur_ycoordUL),
                             QtCore.QPoint(cur_xcoordBR,cur_ycoordBR)))

            # record the sprite
            self[newsprite.sprite_id] = newsprite


class NoAnimationException(Exception):
    """
    Simple exception that signals that an animation
    does not exist.
    """
    pass

class NoSpriteException(Exception):
    """
    Simple exception that is raised if a sprite
    that does not exist is requested.
    """
    pass

#
# ANIMATIONS
#
# Animations are basically ordered lists of sprites, each
# with a time-to-show value attached in a tuple within the
# list.  They can be created either on-the-fly (ie. for player
# animations that vary with the equipped armor) or from the
# sprites/animations.dat file at startup.
#
# Please note that the time-to-show must be a multiple of 100ms.
# Times are rounded up correctly; if you set a frame to show for
# 150ms it will be displayed for 200ms.
#
# (Yes, you are effectively limited to a maximum of 10 frames
# per second.)
#

class AnimationFile(object):
    """
    Manages the sprites/animations.dat file, which
    defines all of the sprite-based animations used
    by the engine, each as a unique configuration
    section within the file.
    """

    def __init__(self, app):
        # preset some variables
        self.clientapp = app
        self.animcache = {}

        # grab a configuration file parser
        self.parser = ConfigParser.SafeConfigParser(self.GetDefaults())
        self.parser.read(ClientPaths.GetSpriteFile("animations.dat"))

    def GetAnimation(self, name):
        """
        Loads an animation from the file and returns
        it as an Animation object.
        """
        # First of all - have we cached this animation?
        if name in self.animcache:
            # Yep, use the cached copy
            return self.animcache[name]

        # Okay, so it's not in the cache... load it!
        # Does it even exist in the file?
        if not self.parser.has_section(name):
            # Nope, it doesn't exist
            raise NoAnimationException(name)

        # Okay, it exists - now load it.
        anim = Animation(self.clientapp, name)
        opts = self.parser.options(name)
        for i in range((len(opts)-1) / 3):
            # About that range() statement there:
            # So we have 3 options for every frame.
            # Now, aside from the frames, there is only one
            # other option, Loop=True|False.  So len(opts)-1
            # gives us the number of per-frame options, and
            # dividing by 3 gives us the number of frames.
            try:
                # prepare option information
                timeopt = "time" + str(i)
                spriteopt = "sprite" + str(i)
                typeopt = "type" + str(i)

                # get the options
                time = int(self.parser.get(name, timeopt))
                type = self.parser.get(name, spriteopt)
                sprite = int(self.parser.get(name, typeopt))
                anim.AddSprite(sprite, type, time)
            except:
                # invalid frame
                print "[warning] while loading animation '" + name + "':"
                print "\tframe " + str(i) + " is invalid."
        try:
            anim.SetLoop(self.parser.getboolean(name, "Loop"))
        except:
            anim.SetLoop(True)
        # all done!
        return anim

    def GetDefaults(self):
        """
        Returns a dictionary containing the default values
        for the animations.dat file.
        """
        return {"Loop": True}

class Animation(QtCore.QObject):
    """
    A single animation that can be displayed.  An animation
    is simply a timed sequence of individual sprites; this
    sequence is stored in the sprites/animations.dat file
    as an individual configuration file section.
    """

    def __init__(self, app, name, parent=None):
        super(Animation,self).__init__(parent)
        self.clientapp = app
        self.name = name
        self.frames = list()
        self.loop = False
        self.curframe = 0       # counts current frame displayed
        self.curtick = 0        # counts number of 100ms intervals passed
        self.running = False

    def AddSprite(self, spriteid, type, time):
        """
        Adds a sprite to the animation sequence for the
        specified amount of time (in milliseconds).  The
        time given will be rounded to the nearest tick of
        the main timer.
        """
        # check that the sprite exists
        if type not in self.clientapp.sprites:
            # the type doesn't even exist!
            raise NoSpriteException("'" + type + "' is not a type of sprite")
        if spriteid >= len(self.clientapp.sprites[type]) or spriteid < 0:
            # the sprite is out of bounds
            raise NoSpriteException(type + " sprite " + str(spriteid) \
                    + " does not exist.")
        # okay, go ahead and register the sprite in the animation
        self.frames.append(((time + 50) / 100, \
                            self.clientapp.sprites[type].GetSprite(spriteid)))

    def DoesLoop(self):
        """
        Checks whether or not this animation loops.
        """
        return self.loop

    def SetLoop(self, loop):
        """
        Sets whether or not this animation loops.
        """
        self.loop = loop

    def Play(self):
        """
        Starts running the animation.
        """
        self.running = True

    def Pause(self):
        """
        Pauses the animation, remembering the current frame.
        """
        self.running = False

    def Stop(self):
        """
        Stops the animation and goes back to the first frame.
        """
        self.running = False
        self.curframe = 0

    def timerEvent(self, event):
        """
        Called when the main timer sends us a timer event.
        """
        if self.running:
            # animation is running, so check if we need to animate
            self.curtick += 1
            frametime, sprite = self.frames[self.curtick]
            if self.curtick >= frametime:
                # advance the frame
                self._AdvanceFrame()

    def _AdvanceFrame(self):
        """
        Called internally to advance to the next frame.
        """
        if self.curframe + 1 >= len(self.frames):
            # does this sprite loop?
            if self.loop:
                # yes, go back to frame 0
                self.curframe = 0
            else:
                # no, pause the animation
                self.Pause()
        else:
            # proceed to next frame
            self.curframe += 1
        # reset the timing mechanism
        self.curtick = 0

    def GetCurrentSprite(self):
        """
        Returns the sprite of the current frame.
        Do not trust this to be valid later; this sprite
        may change over time as the animation proceeds.
        """
        frametime, sprite = self.frames[self.curframe]
        return sprite

class StaticAnimation(Animation):
    """
    Wrapper around the animation class for a single-sprite
    animation.  Also, it doesn't hook itself to the main
    timer, so it doesn't waste processor time advancing itself.
    """

    def __init__(self, type, id):
        self.type = type
        self.spriteid = id
        self.AddSprite(100, type, id)

    def GetSpriteType(self):
        """
        Gets the type of the sprite.
        """
        return self.type

    def GetSpriteId(self):
        """
        Gets the ID of the sprite.
        """
        return self.spriteid


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
        ErrorReporting.ShowError(msg, ErrorReporting.ERROR_FATAL)
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
            ErrorReporting.ShowError(err, ErrorReporting.ERROR_WARNING)

    # Done!
    print "Found", counter, type, "spritesheets."
    return spriteset


def LoadAllSprites(basedir=""):
    """
    Loads all of the sprites for immediate access.
    """
    global _spritesets
    _spritesets = {}

    print "Loading sprites..."

    # load the main sprites
    _spritesets['tiles'] = _LoadSpriteType("tile","tiles",basedir)
    _spritesets['items'] = _LoadSpriteType("item","items",basedir)
    _spritesets['npcs'] = _LoadSpriteType("NPC", "npcs",basedir)

    # finally, add an empty "runtime" set for on-the-fly sprites
    _spritesets['runtime'] = SpriteSet()
    _spritesets['runtime'].type = "runtime"

    # announce our success
    print "Sprites loaded."


def GetSpriteSet(type):
    """
    Returns a handle to the spriteset of the requested type.

    If no spriteset is found for the requested type, a KeyError will
    be raised.

    The currently supported types (by default) are C{tiles}, C{items},
    C{npcs}, and C{runtime}.
    """
    # check the type
    global _spritesets
    if type not in _spritesets:
        # sorry, we don't have that type of sprite
        raise KeyError("Sorry, we don't have that type of sprite!")

    # get the spriteset
    return _spritesets[type]
