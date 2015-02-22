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
import delv.store
from PIL import Image
import sys

USAGE = '''
Usage: ./tileshow.py "Cythera Data" tileID [output.png]

Show the tile requested (uses the ID form seen in maps.)

Requires Python Imaging Library.
Using delv Version: %s
'''%delv.version


if len(sys.argv)<3:
    print >> sys.stderr, USAGE
    sys.exit(-1)

source = open(sys.argv[1],'rb')
tid = int(sys.argv[2],16)

resid = 0x8E00|((tid & 0xFF0)>>4)
tilen = tid & 0x00F
print "Resource: %04X"%resid, "tile:", tilen
scenario = delv.archive.Scenario(source)
resource = scenario.get(resid)
if not resource:
    print >> sys.stderr, "No resource", sys.argv[2], "found in that archive."
    sys.exit(-1)
image = delv.graphics.DelvImageFactory(resource)

tilenames = delv.store.TileNameList(scenario.get(0xF004))

pil_img = Image.frombuffer("P", 
      (32, 32), 
       image.get_tile(tilen), "raw",
       ("P",0,1))
pil_img.putpalette(delv.colormap.pil)

if len(sys.argv)>3:
    pil_img.save(sys.argv[3])
else:
    pil_img.show()

print "Size:", image.logical_width,image.width, image.height
print "Name of tile:", tilenames[tid] 
print "Singular:", tilenames.get_name(tid, plural=False)
print "Plural:", tilenames.get_name(tid, plural=True)
