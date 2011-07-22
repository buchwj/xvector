#!/usr/bin/env python
#
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

from distutils.core import setup

long_description = "The xVector Engine is an open source 2D MMORPG engine "
long_description += "programmed in Python.  xVector makes it easy to create "
long_description += "and distribute your own MMORPG with no programming "
long_description += "experience while also providing developers with a "
long_description += "powerful plugin and scripting API.  This package provides"
long_description += " the client application for the engine."

# okay, we need to find our data files
import os
resfiles = []
startpath = os.path.join("xVClient", "res")
for triple in os.walk(startpath):
    base = os.path.relpath(triple[0], "xVClient")
    dirfiles = triple[2]
    for singlefile in dirfiles:
        if singlefile[len(singlefile)-1] != '~':
            resfiles.append(os.path.join(base, singlefile))

setup(name='xVClient',
      author="James R. Buchwald",
      author_email="buchwj@rpi.edu",
      version="0.0.1",
      description="Client for the xVector 2D MMORPG Engine",
      long_description=long_description,
      url="http://www.xvector.org",
      license='GPLv2',
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)",
        "Topic :: Games/Entertainment :: Role-Playing",
      ],
      
      packages=['xVClient', 'xVClient.ui'],
      scripts=['xVClient/Client.py'],
      package_data={'xVClient.ui': ['*.ui'],
                    'xVClient': resfiles},
      data_files=[('', ['LICENSE', 'CREDITS'])],
      requires=['xVLib (==0.0.1)'],
      provides=['xVClient'],
)
