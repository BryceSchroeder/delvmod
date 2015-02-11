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
import colormap
import archive
import util

# import the four horsemen of the bitpocalypse:
from util import bits_pack, ncbits_pack, ncbits_of, bits_of

def DelvImageFactory(src, *args, **kwargs):
    """Return the appropriate kind of DelvImage subclass for the 
       delv.archive.Resource object you provide."""
    return _CLASS_HINTS.get(src.subindex, DelvImage)(src, *args, **kwargs)
    
def DelvImageFactoryMode(src, mode, *args, **kwargs):
    """Return the appropriate kind of DelvImage subclass for the 
       specified mode, one of tiles, portrait, landscape or sized."""
    return _NAME_HINTS.get(mode, DelvImage)(src, *args, **kwargs)

class UnknownOpcode(Exception): pass

class DelvImage(object):
    """This is the base class for all forms of Delver Compressed (sprite)
       graphics, images in the proprietary format used by the Delver Engine.
       You should probably not instantiate this class directly, but instead
       one of its child classes (General, for sized images; TileSheet, for
       32x512 sets of sixteen 32x32 tiles; Portrait, for 64x64 character
       portraits; or Landscape, for 288x32 level images. You can use 
       DelvImageFactory (arguments same as DelvImage's constructor) to 
       automatically pick the right class, if you are loading from a
       delv.archive.Resource object.
       
       The file format used, is documented here in detail:
       http://www.ferazelhosting.net/wiki/Delver%20Compressed%20Graphics
    """
    canonical_size = 256,256
    has_header = False
    def __init__(self,src=None,width=256,height=256,flags=0,logical_width=256):
        """Create a new Delver Compressed Graphics Image. src can be None,
           the default, which creates an empty image of the default size
           for this type, or an random-access indexable item such as a list,
           string or array, which will be assumed to be compressed data, 
           or a delv Resource object (also assumed to be compressed data.)"""
        if isinstance(src, archive.Resource):
            self.src = bytearray(src.get_data())
        elif hasattr(src, "__getitem__"):
            self.src = bytearray(src)
        
        
        if self.has_header and src:
            header = self.src[0:4]
            data_cursor = 4
            self.width = self.logical_width = bits_of(header, 8+6, 0) << 2
            self.flags = bits_of(header, 2,  14)
            self.height = bits_of(header, 16, 16)
            # TODO - figure out what the deal is with this.
            # DelvTechWiki conjectures that it has something to do with 
            # objects that have some sort of response to dragging/clicking
            # only in certain areas.
            if self.flags: 
                self.logical_width += 4
                self.width += self.flags
            print self.flags, "x"
        elif self.has_header and not src:
            self.width,self.height = width,height
            self.flags = 0
            data_cursor = 0
            self.logical_width = logical_width
        else:
            self.width,self.height = self.canonical_size
            self.flags = 0
            data_cursor = 0
            self.logical_width = self.width
        self.cursor = 0
        self.image = bytearray(self.logical_width * self.height*2)
        if src: self.decompress(self.src, data_cursor)
    def decompress(self, data, cursor):
        """Decompress the indexable-item data provided into this image.
           You shouldn't normally need to call this explicitly."""
        while cursor < len(data):
            opcode = data[cursor]
            if opcode < 0x80:
                # short copy operation 0x00-0x7F
                operation = data[cursor:cursor+2]; cursor += 2
                index =-(ncbits_of(operation, (3,8),  (7,1)) + 1)
                length =   bits_of(operation,  3, 13) + 3
                literals = bits_of(operation,  2, 11)
                self.data(data[cursor:cursor+literals]); cursor += literals
                self.copy(length,index)
            elif opcode < 0xC0:
                # long copy operation 0x80-0xBF
                operation = data[cursor:cursor+3]; cursor += 3
                index =-(ncbits_of(operation, (6,16), (3,8), (6,2)) + 1)
                length =   bits_of(operation,  5,11) + 3
                literals = bits_of(operation,  2,22)
                self.data(data[cursor:cursor+literals]); cursor += literals
                self.copy(length,index)
            elif opcode < 0xD0:
                # pixel data 0xC0-0xCF
                operation = data[cursor:cursor+1]; cursor += 1
                size =    (bits_of(operation,  4,4) + 1) * 4
                self.data(data[cursor:cursor+size]); cursor += size
            elif opcode < 0xE0:
                # unknown opcodes 0xD0 - 0xDF
                operation = data[cursor:cursor+1]; cursor += 1
                literals =  bits_of(operation,  2,6)
                self.data(data[cursor:cursor+literals]); cursor += literals
                print "Unknown opcode %02X lit=%d"%(operation[0],literals)
                #if subcode == 2:
                #    print "%02X %02X"%(data[cursor+1],data[cursor+2])
                #    cursor += 2
                #else:
                #    print "%02X"%data[cursor+1]
                #    cursor += 1
            elif opcode < 0xF0:
                # short run 0xE0-0xEF
                operation = data[cursor:cursor+2]; cursor += 2
                length =   bits_of(operation,  4,4) + 3
                color =    operation[1]
                self.run(length,color)
            elif opcode == 0xF0:
                # long run 0xF0
                operation = data[cursor:cursor+3]; cursor += 3
                length =   operation[1] + 3
                color =    operation[2]
                self.run(length,color)
            elif opcode == 0xFF:
                # terminate 0xFF
                operation = data[cursor]; cursor += 1
                print "Orderly termination. dc:%x pc:%X"%(cursor,self.cursor)
            else:
                # unknown opcode
                raise UnknownOpcode("0x%02X at 0x%06X"%(opcode,cursor))

    def compress(self):
        """Create the compressed version of the graphic. You shouldn't
           normally need to call it explicitly."""
        pass

    def get_data(self):
        """Return the compressed image data, as a bytearray."""
        return self.src

    def get_image(self):
        """Get the whole image. Returns a one-dimensional
           bytearray."""
        return self.image

    def draw_into(self,src,x=0,y=0,w=0,h=0):
        """Draw an image src into this object, optionally specifying
           destination coordinates and a width and height if you wish
           to copy less than the entirety of the source image.
           src may be a PIL image, or anything that can be indexed 
           like src[x,y].
           The source must already be 8-bit indexed color using the colormap
           for your target game (e.g the Cythera CLUT); dithering
           and color-matching are beyond the scope of this project."""
        pass
    def draw_into_tile(self,src,n):
        """Conveninence method to draw to a particular tile. n has the
           same semantics as for get_tile below, including for situations
           in which non-canonical tileset shapes are addressed."""
        self.draw_into(*(src,)+self.tile_rect(n))

    def get_tile(self,n,form='numpy'):
        """Get the nth 32x32 tile of this image. Clasically meaningful only
           for tile sheets, where it returns the nth from the top (counting
           from zero.) For the sake of completeness, though, it will work
           on other images, in which case the tiles are numbered top to 
           bottom, left to right. formats returnable are the same as those
           for get_image."""
        pass

    def tile_rect(self,n):
        """Return the bounding rectangle of the nth tile."""
        pass
  
    def get_size(self):
        """Return (width,height)."""
        pass
    ##########################  PRIVATE METHODS  #######################
    # The methods below may change freely between delv versions, and are
    # intended for the internal use of other delv code only.
    def run(self, length, color):
        maxcursor = self.cursor + length
        while self.cursor < maxcursor:
            self.image[self.cursor] = color
            self.cursor += 1
    def copy(self, length, origin):
        abs_origin = self.cursor + origin
        copy_width = -origin
        for n in xrange(length):
            self.image[self.cursor] = self.image[abs_origin + n%copy_width]
            self.cursor += 1
    def data(self, pixels):
        self.image[self.cursor:self.cursor+len(pixels)] = pixels
        self.cursor += len(pixels)
    def put_pixel(self, color):
        self.image[self.cursor] = color
        self.cursor += 1

class General(DelvImage):
    has_header = True

class TileSheet(DelvImage):
    canonical_size = 32,512

class Portrait(DelvImage):
    canonical_size = 64,64

class Landscape(DelvImage):
    canonical_size = 288,32

_CLASS_HINTS = {142:General, 141:TileSheet, 135:Portrait, 131:Landscape}
_NAME_HINTS = {'general':General,'tiles':TileSheet,'portrait':Portrait,
               'landscape':Landscape,'sprite':TileSheet,'sized':General,
               }

class SkillIcon(object):
    """Class for handling the small skill icons that are stored
       uncompressed as indexed color data."""
    pass
