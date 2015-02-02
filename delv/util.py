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
