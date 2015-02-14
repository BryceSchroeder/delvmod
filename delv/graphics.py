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
from util import bits_pack, ncbits_pack, ncbits_of, bits_of, bitstruct_pack

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
        else:
            self.src = None
        
        
        if self.has_header and self.src:
            header = self.src[0:4]
            self.src = self.src[4:]
            data_cursor = 0
            self.width = self.logical_width = bits_of(header, 8+6, 0) << 2
            self.flags = bits_of(header, 2,  14)
            self.height = bits_of(header, 15, 16) << 1
            self.flags2 = bits_of(header, 1, 31)
            self.logical_height = self.height + self.flags2
            # TODO - figure out what the deal is with this.
            # DelvTechWiki conjectures that it has something to do with 
            # objects that have some sort of response to dragging/clicking
            # only in certain areas. But it has colors similar to the main
            # object...
            if self.flags: 
                self.logical_width += 4
                self.width += self.flags
            if self.flags2:
                self.height += self.flags2
                # interpreting 8F0C correctly seems to be mutually exclusive
                # with 8F1A. They have the same identified or suspected flag
                # bits. One possibility is that 8F0C is an earlier version
                # of the graphics format (I at least do not recognize the pot
                # as appearing in the current game); another is that the size
                # information is encoded somewhere else e.g. in a script.
                # Neither of the two resources mentioned above contain any
                # unknown opcodes (and that would be a really obtuse way
                # to encode size information anyhow.)
        elif self.has_header and not self.src:
            self.width,self.height = width,height
            self.flags = 0
            data_cursor = 0
            self.logical_width = logical_width
            self.logical_height = self.height
        else:
            self.width,self.height = self.canonical_size
            self.flags = 0
            data_cursor = 0
            self.logical_width = self.width
            self.logical_height = self.height
        self.cursor = 0
        self.image = bytearray(self.logical_width * self.logical_height)
        if src: self.decompress(self.src, data_cursor)
        self.cached_visual = None
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
                # Short data
                # They do not seem to have any visual effect.
                # It is quite possible that this represents a short run of 
                # literal data (< C0); it only appears as the penultimate
                # opcode in the corpus. On this basis we assume 4 bits of
                # literals, but only D2 is seen.
                operation = data[cursor:cursor+1]; cursor += 1
                literals =  bits_of(operation,  4,4)
                self.data(data[cursor:cursor+literals]); cursor += literals
                #print "Unknwn opcode %02X lit=%d c=%X"%(operation[0],literals,
                #    cursor)
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
                #print "Orderly termination. dc:%x pc:%X"%(cursor,self.cursor)
            else:
                # unknown opcode
                raise UnknownOpcode("0x%02X at 0x%06X"%(opcode,cursor))

    def compress(self, image):
        """Create the compressed version of the graphic. You shouldn't
           normally need to call it explicitly."""
        # The basic idea here is that we have each opcode make a "bid" on
        # the image data at the current cursor position, then we use a greedy
        # approach to pick the bidder who gives the best (local) compression
        # ratio.
        # Each cursor position needs to be bid on by the following operations:
        # Short Data (Dx)               Long Data (Cx)
        # Short Copy with 0 literals    Long Copy with 0 literals
        # Short Copy with 1 literal     Long Copy with 1 literal
        # Short Copy with 2 literals    Long Copy with 2 literals
        # Short Run (Ex)                Long Run (F0)
        operations = [
                      lambda i,d: self.en_short_data(i,d),
                      lambda i,d: self.en_long_data(i,d),
                      lambda i,d: self.en_short_copy(i,d,0),
                      lambda i,d: self.en_short_copy(i,d,1),
                      lambda i,d: self.en_short_copy(i,d,2),
                      lambda i,d: self.en_long_copy(i,d,0),
                      lambda i,d: self.en_long_copy(i,d,1),
                      lambda i,d: self.en_long_copy(i,d,2),
                      lambda i,d: self.en_short_run(i,d),
                      lambda i,d: self.en_long_run(i,d)
        ]
        codes = []
        icursor = 0
        while icursor < len(self.image):
            # each of the en_* codes returns a compression_ratio, end_cursor,
            # code tuple. We pick the best one until we're done.
            _,icursor,code = max([op(icursor,image) for op in operations])
            codes.append(code)
            #if not code[0]&0x80: break
        # The scheme above will tend to produce lots of sequences like
        # C0 aa bb cc dd, C0 ee ff gg hh, C0 ii jj kk ll
        # and we need to condense them into
        # C2 aa bb cc dd ee ff gg hh ii jj kk ll
        # which is what condense does. The whole reason for this nonsense is
        # that we don't want greedy behavior in the literal data opcodes.

        if self.has_header:
            data = bytearray(4)
            bits_pack(data, self.width>>2, 14, 0 )
            bits_pack(data, self.flags,     2, 15) 
            bits_pack(data, self.height,   16, 16)
        else: 
            data = bytearray()
        data += self.condense_opcodes(codes)
        data += '\xFF' # Termination opcode
        return data

    def get_data(self):
        """Return the compressed image data, as a bytearray."""
        if not self.src: self.src = self.compress(self.image)
        return self.src

    def get_logical_image(self):
        """Get the whole image. Returns a one-dimensional
           bytearray. This will include data not part of the image
           displayed to the user, if it exists (the purpose of that data
           is unknown at this time.)"""
        return self.image
    def get_from(self, x,y,w,h):
        """Get a section of the image, bounded by the rectangle (x,y,w,h).
           It is returned as a flat bytearray, size w*h."""
        gf = bytearray()
        for yr in xrange(y,y+h):
            gf += self.image[yr*self.logical_width+x:yr*self.logical_width+x+w]
        return gf
    def get_image(self):
        """Get only the part of the image normally displayed by 
           the engine to the user. This is usually all of the image;
           except for certain Sized image resources ID 8Fxx."""
        if self.width == self.logical_width: 
            self.cached_visual = self.image
        if self.cached_visual: return self.cached_visual
        self.cached_visual = bytearray(self.width*self.height)
        v_cursor = 0
        for x in xrange(self.height):
            self.cached_visual[v_cursor:v_cursor+self.width] = (
                self.image[x*self.logical_width:x*self.logical_width+self.width
                ])
            v_cursor += self.width
        return self.cached_visual
    def set_image(self, data):
        """Set the uncompressed data of the logical image. data must be a 
           linear indexable item of size logical_width*logical_height, of
           integer values that represent indexed color pixels. Left to right,
           top to bottom, densely packed."""
        self.image = bytearray(data)
        self.cached_visual = None
        self.src = None
    def draw_into(self,src,x=0,y=0,w=0,h=0):
        """Draw an image src into this object, optionally specifying
           destination coordinates and a width and height if you wish
           to copy less than the entirety of the source image.
           src must be a flat indexable of size w*h.
           The source must already be 8-bit indexed color using the colormap
           for your target game (e.g the Cythera CLUT); dithering
           and color-matching are beyond the scope of this project."""
        self.src = None
        if not self.image: 
             self.image = bytearray(self.logical_width*self.logical_height)
        for yr in xrange(y,y+h): 
             self.image[yr*self.logical_width+x:yr*self.logical_width+x+w] = src[(yr-y)*w:(yr-y)*w + w]
    def draw_into_tile(self,src,n):
        """Conveninence method to draw to a particular tile. n has the
           same semantics as for get_tile below, including for situations
           in which non-canonical tileset shapes are addressed."""
        self.draw_into(*(src,)+self.tile_rect(n))

    def get_tile(self,n):
        """Get the nth 32x32 tile of this image. Clasically meaningful only
           for tile sheets, where it returns the nth from the top (counting
           from zero.) For the sake of completeness, though, it will work
           on other images, in which case the tiles are numbered top to 
           bottom, left to right. The format is the same as get_from."""
        return self.get_from(*self.tile_rect(n))

    def tile_rect(self,n):
        """Return the bounding rectangle of the nth tile."""
        y = (n*32)%512
        x = (n//16)*32
        return (x,y,32,32)
  
    def get_size(self):
        """Return (width,height)."""
        return self.width,self.height
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
    # encoder methods
    # All of them return compression_ratio, end_cursor_position, encoded_data
    # tuples.
    # compression_ratio = lenth of image data / length of encoded data
    def en_short_data(self,i,d):
        end = min(i+3,len(d))
        datalen = end-i
        code = bytearray(1+datalen)
        bits_pack(code, 0xD,          4, 0)
        bits_pack(code, datalen,      2, 6)
        for n,m in zip(xrange(i,i+datalen),xrange(1,datalen+1)):
            code[m]=d[n]
        return datalen/(datalen+1.0),end,code
    def en_long_data(self,i,d):
        if len(d)-i < 4:
            return -1,i,''
        return 4/5.0,i+4,'\xC0'+d[i:i+4]
    def searchback(self, d, i, lits, start, stop, mlen,llen=3):
        found = -1
        match_found = -1
        lowest_clen = llen
        highest_clen = min(mlen,len(d)-i)
        found_clen = 0
        while (highest_clen >= lowest_clen):
            mid_clen = (highest_clen-lowest_clen)/2 + lowest_clen
            found = d.rfind(d[i+lits:i+lits+mid_clen],start,stop)
            if found >= 0:
                lowest_clen = mid_clen+1
                found_clen = mid_clen
                match_found = found
            else:
                highest_clen = mid_clen-1
        return match_found,found_clen if match_found >= 0 else llen
    def en_short_copy(self,i,d,lits):
        #if lits: return -1,i,''
        found,clen = self.searchback(d,i,lits,max(0,i-(1024-lits)),i+lits,10)
        if found < 0:
            return -1,i,''

        index = -(found-i+1)+lits

        code = bytearray(2)
        bitstruct_pack(code, [
            (0,      [(1,0)       ]),
            (index,  [(3,8), (7,1)]),
            (clen-3, [(3,13)      ]),
            (lits,   [(2,11)      ])])
          
        #check = ncbits_of(code, (3,8), (7,1))
        #if check != index:
        #    print "ERROR %08X %08X"%(index,check), clen-3, lits
        code += d[i:i+lits]
        return (lits+clen)/(2.0+lits),i+lits+clen,code
    def en_long_copy(self,i,d,lits):
        found,clen = self.searchback(d,i,lits, max(0,i-(32768-lits)),i+lits,34)
        if found < 0:
            return -1,i,''
        index = -(found-i+1)+lits

        code = bytearray(3)
        bitstruct_pack(code, [
            (2,      [(2,0)             ]),
            (index,  [(6,16),(3,8),(6,2)]),
            (clen-3, [(5,11)            ]),
            (lits,   [(2,22)            ])])

        #check = ncbits_of(code, (6, 16),(3,8),(6,2))
        #if check != index:
        #    print "ERROR", index,check, clen-3, lits
        code += d[i:i+lits]
        return (lits+clen)/(3.0+lits),i+lits+clen,code
    def en_short_run(self,i,d):
        initial_color = d[i]
        end = i
        while end < len(d) and d[end] == initial_color:
            end += 1
        if end-i < 3:
            return -1,i,''
        runlength = min(18,end-i)
        code = bytearray(2)
        bits_pack(code, 0xE,           4, 0)
        bits_pack(code, runlength-3,   4, 4)
        bits_pack(code, initial_color, 8, 8)
        return (runlength/2.0, i+runlength, code)
    def en_long_run(self,i,d):
        initial_color = d[i]
        end = i
        while end < len(d) and d[end] == initial_color:
            end += 1
        if end-i < 3:
            return -1,i,''
        runlength = min(258,end-i)
        code = bytearray(3)
        bits_pack(code, 0xF0,          8, 0)
        bits_pack(code, runlength-3,   8, 8)
        bits_pack(code, initial_color, 8, 16)
        return (runlength/3.0, i+runlength, code)
    def condense_opcodes(self, codes):
        condensed = []
        data=bytearray()
        data_opcode = bytearray()
        for c in codes:
            if c[0]&0xF0 == 0xC0:
                data_opcode.extend(c[1:])
            else:
                if data_opcode: data += self.merge_C0(data_opcode)
                data += c
                data_opcode = bytearray()
        data += self.merge_C0(data_opcode)
        return data
    def merge_C0(self, ops):
        data = bytearray()
        assert not len(ops)%4
        while ops:
            chunk = min(64,len(ops))
            data += chr(0xC0 + chunk/4 - 1)
            data += ops[:chunk]
            ops = ops[chunk:]
        return data

class General(DelvImage):
    has_header = True

class TileSheet(DelvImage):
    canonical_size = 32,512

class Portrait(DelvImage):
    canonical_size = 64,64

class Landscape(DelvImage):
    canonical_size = 288,32


class SkillIcon(DelvImage):
    """Class for handling the small skill icons that are stored
       uncompressed as indexed color data.
       Methods with the same name generally work as in DelvImage."""
    canonical_size = 32,16
    width = 32
    height = 16
    logical_width = 32
    logical_height = 16
    #def __init__(self, data=None):
    #    self.image = data
    #    self.data = data
    #    if not self.image: self.image = bytearray(32*16)
    def decompress(self, src, *argv):
        self.image = src
        self.data = None
    def compress(self, *argv):
        self.data = self.image

_CLASS_HINTS = {142:General, 141:TileSheet, 135:Portrait, 131:Landscape,
                137:SkillIcon}
_NAME_HINTS = {'general':General,'tiles':TileSheet,'portrait':Portrait,
               'landscape':Landscape,'sprite':TileSheet,'sized':General,
               'icon':SkillIcon
               }
