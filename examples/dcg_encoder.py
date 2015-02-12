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
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 

import delv
import delv.archive
import delv.graphics
import delv.colormap
from PIL import Image
import sys

USAGE = '''
Usage: ./dcg_encoder.py src.png DEST.data [flags]
e.g:   ./dcg_encoder.py landking.png 8E71.data

Converts indexed color images to Delver Compressed Graphics. If the flags
parameter is given, a sized image will be produced, otherwise there will
not be a header written. This program will allow the creation of images 
of non-canonical sizes; it is up to you to not try to stick e.g. a 
128x128 image in the resource for a portrait (ID 0x88xx).

Requires Python Imaging Library.
Using delv Version: %s
'''%delv.version

if len(sys.argv)<3:
    print >> sys.stderr, USAGE
    sys.exit(-1)

source = open(sys.argv[1],'rb')
destination = open(sys.argv[2],'wb')
flags = int(sys.argv[3]) if len(sys.argv)>3 else None

print >> sys.stderr, "This program isn't finished yet."
