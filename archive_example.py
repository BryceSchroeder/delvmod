#!/usr/bin/env python
#
# A simple example of how to use delv to manipulate archives.
#
# Copyright 2014-2015 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
# Wiki: http://www.ferazelhosting.net/wiki/delv
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Please do not make trouble for me or the Technical Documentation Project by
# using this software to create versions of the "Cythera Data" file which 
# have bypassed registration checks.
# Also, remember that the "Cythera Data" file is copyrighted by Ambrosia and
# /or Glenn Andreas, and publishing modified versions without their permission
# would violate that copyright. 
#
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 
ABOUT = """This file created by the Python module delv, written by 
Bryce Schroeder as part of the Technical Documentation Project; more
information can be found at http://www.ferazelhosting.net/wiki/delv

Comments can be addressed to bryce.schroeder@gmail.com
On the web at: http://www.bryce.pw

The following license applies to module delv, and not necessarily 
to the content of this archive file:
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

If this archive represents a modified version of "Cythera Data," you should
be aware that it was not distributed by Bryce Schroeder or other members of
the Technical Documentation Project, and is being circulated against their
express wishes and without their consent.
"""

import delv
import delv.archive
import sys

if len(sys.argv) < 2:
    print 'Usage: ./archive_example.py "Cythera Data" ["Modded Cythera Data"]'
    sys.exit(-1)

# open a Delver Archive - specifically as a Scenario (greatly speeds this
# program, because the Scenario class knows which resources are supposed to
# be encrypted, sparing delv the difficulty of guessing for each one.)
archive = delv.archive.Scenario(sys.argv[1])

print "Loaded archive '%s'"%archive.scenario_title

# Go through all the possible subindex pages and print out the ones that
# actually have stuff in them
for idx in archive.subindices():
    resids = archive.resource_ids(idx)
    if not resids: continue
    print idx, "has", len(archive.resource_ids(idx)), "resources"

# Modify a resource, as an array: 
# (This changes the text of the Sapphire Book of Wisdom)
archive[0x021B][0xDA7:0xDAA] = 'zap'

# Create a resource one way
archive[0xBC00] = "This file written by delv %s"%delv.version

# Another way to create a resource, which we'll make encrypted this time
about_resource = archive.get(0xBC35, True)
about_resource.hint_encryption(True)

# A way to read/edit resource - as file-like objects (They have many 
# helpful methods for reading/writing binary, see delv.util.BinaryHandler)
rfile = about_resource.as_file()
rfile.write(ABOUT)

if len(sys.argv)>2:
    print "Writing modified scenario to %s"%sys.argv[2]
    archive.to_path(sys.argv[2])

# Functionality remaining to be added for Archive objects -
# loading and storing from files in a directory.
