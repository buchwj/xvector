#!/usr/bin/env python

# xVector Engine
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
distutils setup script for the client and map editor
"""

import os
from xVClient import ClientVersion

from distutils.core import setup
import platform
if platform.system() == "Windows":
    try:
        import py2exe
    except ImportError:
        msg = "py2exe not found.  You will not be able to create an EXE."
        print "warning:", msg
else:
    print "You are about to see a warning about 'windows'."
    print "Please ignore this unless you want to build an EXE."

# okay, we're going to enumerate our resource directories now.
import re

resources = []

# first up are the sprites
matcherPNG = re.compile(r".+\.png$")
matcherMETA = re.compile(r".+\.meta$")
matcherSPRITE = lambda s: matcherPNG.match(s) or matcherMETA.match(s)
spritedir = os.path.join('xVClient', 'sprites')
spritefiles_potential = os.listdir(spritedir)
spritefiles = filter(matcherSPRITE, spritefiles_potential)
spritefiles_final = [os.path.join(spritedir, s) for s in spritefiles]
resources.append(('sprites', spritefiles_final))

setup(name='xVector',
      version=ClientVersion.GetVersionString(),
      description='xVector MMORPG Engine (client and map editor)',
      author='James Buchwald',
      author_email='nullmech@xvector.org',
      url='http://www.xvector.org',
      license='GPLv2',
      packages=['xVClient', 'xVMapEdit', 'xVLib', 'xVServer'],
      requires=['PyQt4(>=4.7)'],
      provides=['xVClient', 'xVMapEdit', 'xVLib', 'xVServer'],
      scripts=['xVClient/Client.py',
               'xVMapEdit/MapEditor.py',
               'xVClient/HTTPFetcher.py',
              ],
      data_files=resources,
      cmdclass={},
      windows=['xVClient/Client.py',
               'xVMapEdit/MapEditor.py',
               'xVClient/HTTPFetcher.py',
              ],
      zipfile='core.dat',
      options={'py2exe':{'includes':['sip']}})
