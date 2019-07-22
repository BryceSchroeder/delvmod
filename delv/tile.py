#!/usr/bin/env python
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
from . import store


class Tile(object):
    def __init__(self, index, namecode, attributes, fauxprop, image):
        self.index=index
        self.namecode = namecode
        self.attributes = attributes
        self.fauxprop,self.fauxprop_aspect,self.fauxprop_rotate = fauxprop
        self.mask = None
        self.rotated_mask = None
        self.image = str(image)
        self.rotated_cache = None
        self.requires_mask =(attributes & 0xFF000000) and '\x00' in self.image
    def draw_priority(self):
        if not self.attributes: return 0xFFFFFFFF
        return (self.attributes&0xBFCDFD1C)
    def get_name(self,plural=False):
        return store.namecode(self.namecode, plural)
    def get_image(self, rotated=False): 
        if rotated:
            if not self.rotated_cache: 
                self.rotated_cache = self.rotate()
            return self.rotated_cache
        else:
            return self.image
    def rotate(self):
        rotated = bytearray(32*32)
        for y in range(32):
            rotated[y*32:y*32+32] = self.image[y::32]
        return str(rotated)
    def get_pixmap_mask(self,gtk,rotated=False):
        """This is really just to save redelv the bother of having 
           a separate cache of tile masks..."""
        if self.mask and not rotated: return self.mask
        if self.rotated_mask and rotated: return self.rotated_mask
        image = self.get_image(rotated)
        mask = gtk.gdk.Pixmap(None, 32, 32, 1)
        on = mask.new_gc(foreground=gtk.gdk.Color(pixel=1),
             function=gtk.gdk.COPY)
        off = mask.new_gc(foreground=gtk.gdk.Color(pixel=0),
             function=gtk.gdk.COPY) 
        mask.draw_rectangle(off, True, 0,0,32,32)
        for n,pixel in enumerate(image):
            if pixel != '\x00': 
                mask.draw_point(on, n%32, n//32)
        #    else:
        #        self.mask.draw_point(off, n%32, n//32)
        if rotated:
            self.rotated_mask = mask
        else:
            self.mask = mask
        return self.rotated_mask if rotated else self.mask

class CompoundTile(Tile):
    def __init__(self, index, namecode, attributes, fauxprop, library, 
        composition):
        image = bytearray(32*32)
        for n,(resid, tile, segment) in enumerate(composition):
            chunk = library.get_object(resid).get_subtile(tile,segment)
            i = (n%4)*8 + (n//4)*8*32
            for r in range(8):
                 image[i+32*r:i+32*r+8] = chunk[8*r:8*r+8]
        Tile.__init__(self, index, namecode, attributes, fauxprop, image)
