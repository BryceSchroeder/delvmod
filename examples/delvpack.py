#!/usr/bin/env python
# Copyright 2015 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
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

from __future__ import absolute_import, division, print_function, unicode_literals

import delv
import delv.archive
import sys

USAGE = '''Usage: ./delvpack.py src dest

Packs or unpacks Delver archives. If dest is an existing directory, 
it will unpack src into it. Otherwise, it writes a new Delver Archive
at dest. src itself can be either an archive or a directory containing
an unpacked Delver Archive.

Note that when copying archives, it produces an archive containing the
same data, not a copy like you'd get with cp; in particular, delv does
not leave cruft in the archive like DelvEd does, and so if you copy
"Cythera Data" the resulting copy will be smaller (but still fully
functional.)
'''

if len(sys.argv)<3:
    print(USAGE, file=sys.stderr)
    sys.exit(-1)

delv.archive.Scenario(sys.argv[1]).to_path(sys.argv[2])

