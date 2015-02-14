#!/usr/bin/env python
# Copyright 2014-2015 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
# Version: 0.20
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
import cStringIO, struct

# This whole file is intended to be 'private' to delv; it isn't part of the 
# public API.

def int_to_bits(value,size):
    result = bytearray(size)
    j =0 
    for i in xrange(size-1,-1,-1):
        result[j] = (value >> i)&1
        j += 1
    return result

def bytes_to_bits(src):
    src = bytearray(src) # Note that if src is an integer, a new empty bytearray is made.
    # this is not efficient, but it does at least make sense semantically.
    result = bytearray(len(src)*8)
    ri = 0
    for byte in src:
        for bi in xrange(7,-1,-1): 
            result[ri] = (byte>>bi)&1
            ri += 1
    return result

def bits_to_bytes(src):
    result = bytearray((len(src)+7)//8)
    byi = 0
    bi = 0
    for n,bit in enumerate(src):
        byte_index = n//8
        bit_index = n % 8
        result[byte_index] |= bit << (7-bit_index)
    return result

def bitstruct_pack(target, pairs):
    b = bytes_to_bits(target)
    for value, fieldspec in pairs:
        for size, index in fieldspec[::-1]:
            fieldbits = value & (0xFFFFFFFFFFFFFFFFL >> (64-size))
            b[index:index+size] = int_to_bits(value,size)
            value >>= size
    t =  bits_to_bytes(b)
    for x in xrange(len(t)): target[x]=t[x]


def bits_pack(target, value, size, index,debug=False):
    """Alter bytearray target so that size bits of target starting
       at index are replaced by value."""
    bit_index = index % 8
    startbyte = index // 8
    endbyte = (index+size+7) // 8
    section = bytes_to_bits(target[startbyte:endbyte])
    #if debug:print "BEFORE", ''.join(["%01d"%b for b in section])
    section[bit_index:bit_index+size] = int_to_bits(value,size)
    #if debug:print "AFTER ", ''.join(["%01d"%b for b in section])
    target[startbyte:endbyte] = bits_to_bytes(section)

def ncbits_pack(target, value, *fields):
    """Alter target to contain the value given, broken up into
       nonconsecutive bitfields using the same sematics as ncbits_of.
       
       Look on this, ye coders, and repeat the sacred mantra:
          "Premature optimization is the root of all evil."
    """
    # This would be more efficient if we made it only convert to
    # bits and back once, or if we rewrote it to be like bits_of (I
    # actually wrote that first before I thought of this simpler way)
    # but why bother, it's only used compressing graphics, which is an
    # infrequent operation (whereas decompression happens a lot.)
    for size,index in fields[::-1]:
        fieldbits = value & (0xFFFFFFFFFFFFFFFFL >> (64-size))
        bits_pack(target, fieldbits, size, index)
        value >>= size
    

def ncbits_of(data, *fields):
    """Returns an integer bit field from the bytearray data, 
       the integer being made up of all the fields combined.
       Each field is a tuple in the format (size,index). 
       e.g. if  you had a bytearray foo of three bytes as follows:
       
         -----AB-, ---CDEFG, HI--JKL-   

       And you wanted to extract the bits ABCDEFGHIJKL as one
       12-bit integer, you'd say:
         ncbits_of(foo, (2,5), (7,11), (3,20))

       Note that if you ever use this function other than to be
       compatible with something already using nonconsecutive bits,
       I am pretty sure that D. E. Knuth will come to your home and
       perform an exorcism involving a shotgun and rock salt. Or at least,
       he ought to.
    """
    result = 0
    position = 0
    for size,index in fields:
        result <<= size
        result |= bits_of(data, size, index)
    return result

def bits_of(data, size, index):
    "Read a slice of the bytearray data bitwise - indices in bits"
    byte_index = index // 8
    bit_index = index % 8
    byte_end = (size+index) // 8 
    bit_size = size % 8 
    result = data[byte_index] & (0xFF >> bit_index)
    while byte_index < byte_end:
        byte_index += 1
        if len(data) == byte_index: 
            result <<= 8; break
        result = (result << 8) | data[byte_index]
    result >>= 8 - (bit_index + bit_size) % 8
    return result
        


class BinaryHandler(object):
    S_offlen = struct.Struct('>LL')
    S_uint32 = struct.Struct('>L')
    S_uint8 = struct.Struct('B')
    S_uint16 = struct.Struct('>H')

    # Wishing for a more elegant alternative
    def seek(self, *vargs, **kwargs):
        self.file.seek(*vargs, **kwargs)
    def read(self, *vargs, **kwargs):
        return self.file.read(*vargs, **kwargs)
    def write(self, *vargs, **kwargs):
        self.file.write(*vargs, **kwargs)
    def tell(self, *vargs, **kwargs):
        return self.file.tell(*vargs, **kwargs)
    def truncate(self, *vargs, **kwargs):
        return self.file.truncate(*vargs,**kwargs)

    def __init__(self, file):
        self.file = file
    def write_struct(self, s, v, offset=None):
        if offset is not None: self.seek(offset)
        if type(v) is int:
            self.write(s.pack(v)) 
        else:
            self.write(s.pack(*v))
    def write_uint8(self, v, offset=None):
        self.write_struct(self.S_uint8, v, offset)
    def write_uint16(self,v,offset=None):
        self.write_struct(self.S_uint24, v, offset)
    def write_uint32(self,v,offset=None):
        self.write_struct(self.S_uint32, v, offset)
    def write_offlen(self,offs,length,offset=None):
        self.write_struct(self.S_offlen, (offs,length), offset)

    def write_sint24(self,v,offset=None):
        if offset is not None: self.seek(offset)
        self.write_uint8((v&0xFF0000)>>16)
        return self.write_uint16((v&0x00FFFF))

    def write_xy24(self,x,y,offset=None):
        if offset is not None: self.seek(offset)
        self.write_uint8((x&0xFF0)>>4)
        self.write_uint8(((x&0x00F)<<4)&((y&0xF00)>>8))
        return self.write_uint8(y&0x0FF)

    def write_vm32(self, flags, v, offset=None):
        if offset is not None: self.seek(offset)
        self.write_uint8(flags)
        return self.write_sint24(v)

    def write_pstring(self, s, offset=None):
        if offset is not None: self.seek(offset)
        "Write a pascal string - 8 bit length followed by data."
        assert len(s) < 256
        self.write_uint8(len(s))
        return self.write(s)
    def write_cstring(self, s, offset=None):
        if offset is not None: self.seek(offset)
        "Write a null-terminated string."
        self.write(s)
        return self.write('\x00')


    def read_struct(self, s, offset=None):
        if offset is not None: self.seek(offset)
        return s.unpack(self.read(s.size))
    def read_offlen(self, offset=None):
        return self.read_struct(self.S_offlen, offset)
    def read_uint8(self, offset=None):
        "Read 8-bit unsigned integer"
        return self.read_struct(self.S_uint8, offset)[0]
    def read_uint16(self, offset=None):
        "Read 16-bit big endian unsigned integer."
        return self.read_struct(self.S_uint16, offset)[0]
    def read_sint24(self, offset=None):
        "Return a signed 24-bit integer."
        uvar = (self.read_uint8(offset)<<8) | self.read_uint16()
        if uvar & 0x800000:
            uvar = ~uvar + 1
        return uvar
    def read_xy24(self, offset=None):
        "Read packed 12-bit xy coordinates, as used in prop lists."
        if offset is not None: self.seek(offset)
        d = [ord(c) for c in self.read(3)]
        return (d[0]<<8)|(d[1]>>4), ((d[1]&0x0F)<<4)|d[2]
    def read_uint32(self, offset=None):
        "Read 32-bit unsigned integer."
        return self.read_struct(self.S_uint32, offset)[0]
    def read_vm32(self, offset=None):
        "Read 24-bit signed integer and 8-bit flags. (Flags returned first.)"
        return self.read_uint8(offset), self.read_sint24()
    def read_pstring(self, offset=None):
        size = self.read_uint8(offset)
        return self.read(size)
    def read_cstring(self, offset=None):
        if offset is not None: self.seek(offset)
        buf = []
        while True:
            b = self.read(1)
            if b == '\0' or not b: break
            buf.append(b)
        return ''.join(buf)

class UnimplementedFeature (Exception): pass
