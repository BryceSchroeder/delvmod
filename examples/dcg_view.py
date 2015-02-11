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
Usage: ./dcg_view.py archive resid [destination.png]
Or:    ./dcg_view.py file tiles|portrait|landscape|sized [destination.png]

Views Delver Compressed Graphics resources, either in an archive or as a
single file. In the latter case, provide the type of resource (portrait, tiles,
etc). Optionally, provide a filename to save an indexed color PNG rather than
displaying the graphic to the monitor.

Requires Python Imaging Library.
Using delv Version: %s
'''%delv.version

modes = 'tiles portrait landscape sized'.split()

if len(sys.argv)<3:
    print >> sys.stderr, USAGE
    sys.exit(-1)

source = open(sys.argv[1],'rb')

if sys.argv[2] in modes: # individual file
    data = source.read()
    image = delv.graphics.DelvImageFactoryMode(data, sys.argv[2])
else: # archive
    resource = delv.archive.Scenario(source).get(int(sys.argv[2],16))
    image = delv.graphics.DelvImageFactory(resource)


pil_img = Image.frombuffer("P", 
      (image.logical_width, image.height), 
       image.get_image(), "raw",
       ("P",0,1))
pil_img.putpalette(delv.colormap.pil)
pil_img.show()

print "Size:", image.logical_width,image.width, image.height
