#!/usr/bin/env python

##
## Documentation Build Script for xVector MMORPG Engine
##     (Experimental)
## Copyright (c) 2011 James R. Buchwald
##

## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software Foundation,
## Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import imp
import time

# attempt import of epydoc
try:
    from epydoc import docbuilder
    from epydoc.docwriter.html import HTMLWriter
except ImportError:
    print "FATAL ERROR: Could not import epydoc."
    print "Please ensure that epydoc is installed on your PYTHONPATH."
    sys.exit()

# detect xVector packages
client_path = None
xvlib_path = None
mapedit_path = None
server_path = None

def DetectPackage(pkgname, first_path=None):
    '''@raise ImportError: Raised if package not detected.'''
    # attempt import of package
    try:
        loc = imp.find_module(pkgname, first_path)[1]
        sys.path.append(first_path)
        return loc
    except ImportError:
        # not detected on PYTHONPATH
        if not first_path: raise
        DetectPackage(pkgname, None)

try:
    client_path = DetectPackage("xVClient", ["../client"])
except ImportError:
    print "WARNING: xVClient not found in the PYTHONPATH or parent directory."
    print "Documentation will not be generated for xVClient."

try:
    xvlib_path = DetectPackage("xVLib", ["../xVLib"])
except ImportError:
    print "WARNING: xVLib not found in the PYTHONPATH or parent directory."
    print "Documentation will not be generated for xVLib."

try:
    mapedit_path = DetectPackage("xVMapEdit", ["../mapeditor"])
except ImportError:
    print "WARNING: xVMapEdit not found in the PYTHONPATH or parent directory."
    print "Documentation will not be generated for xVLib."

try:
    server_path = DetectPackage("xVServer", ["../server"])
except ImportError:
    print "WARNING: xVServer not found in the PYTHONPATH or parent directory."
    print "Documentation will not be generated for xVServer."

# build documentation index
pkgs = filter(None, [client_path, xvlib_path, mapedit_path, server_path])
if len(pkgs) < 1:
    print "FATAL ERROR: No packages were found to generate documentation from."
    sys.exit()

print "Generating documentation..."
start = time.time()
doc_index = docbuilder.build_doc_index(pkgs)

# write documentation as HTML
writer = HTMLWriter(doc_index,
                    prj_name="xVector MMORPG Engine",
                    prj_url="http://www.xvector.org",
                    css="api.css")
try:
    writer.write("api")
except Exception as err:
    print " ** Error while writing HTML documentation: %s" % err.args[1]
    sys.exit()

# complete
print " ** Documentation generated in %f seconds." % (time.time() - start)

