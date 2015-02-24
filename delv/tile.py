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
import store


class Tile(object):
    def __init__(self, index, namecode, attributes, fauxprop, image):
        self.index=index
        self.namecode = namecode
        self.attributes = attributes
        self.fauxprop,self.fauxprop_aspect = fauxprop
        self.mask = None
        self.image = str(image)
        self.requires_mask =(attributes & 0xFF000000) and '\x00' in self.image
    def get_name(self,plural=False):
        return store.namecode(self.namecode, plural)
    def get_image(self): return self.image
    def get_pixmap_mask(self,gtk):
        """This is really just to save redelv the bother of having 
           a separate cache of tile masks..."""
        if self.mask: return self.mask
        self.mask = gtk.gdk.Pixmap(None, 32, 32, 1)
        on = self.mask.new_gc(foreground=gtk.gdk.Color(pixel=1),
             function=gtk.gdk.COPY)
        off = self.mask.new_gc(foreground=gtk.gdk.Color(pixel=0),
             function=gtk.gdk.COPY) 
        self.mask.draw_rectangle(off, True, 0,0,32,32)
        for n,pixel in enumerate(self.image):
            if pixel != '\x00': 
                self.mask.draw_point(on, n%32, n//32)
        #    else:
        #        self.mask.draw_point(off, n%32, n//32)
        return self.mask

class CompoundTile(Tile):
    def __init__(self, index, namecode, attributes, fauxprop, library, 
        composition):
        self.index=index
        self.namecode = namecode
        self.mask = None
        self.fauxprop,self.fauxprop_aspect = fauxprop
        self.attributes = attributes
        self.image = bytearray(32*32)
        for n,(resid, tile, segment) in enumerate(composition):
            chunk = library.get_object(resid).get_subtile(tile,segment)
            i = (n%4)*8 + (n//4)*8*32
            for r in xrange(8):
                 self.image[i+32*r:i+32*r+8] = chunk[8*r:8*r+8]
        self.image = str(self.image)
        self.requires_mask =(attributes & 0xFF000000) and '\x00' in self.image
