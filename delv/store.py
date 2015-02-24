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
# This file addresses sundry storage types used within Delver Archives,
# and as such is mostly a helper for other parts of delv. 
import util, archive
import cStringIO as StringIO
import array, bisect
import tile

class Store(object):
    def __init__(self, src):
        self.data = None
        self.set_source(src)
    def set_source(self, src):
        self.src = None
        if src and issubclass(src.__class__, util.BinaryHandler):
            self.src = src
            self.res = None
        elif src and issubclass(src.__class__, archive.Resource):
            self.src = src.as_file()
            self.res = src
        elif src:
            self.src = util.BinaryHandler(src)
            self.res = None
    def get_data(self):
        if not self.data:
            buf = StringIO.StringIO()
            bh = util.BinaryHandler(buf)
            self.write_to_bfile(bh)
            # I wonder why StringIO doesn't have a method that does this:
            self.data = bytearray(buf.getvalue())
        return self.data 

class SymbolList(Store):
    pass

class TileAttributesList(Store):
    def __init__(self, src):
        Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.contents = array.array("L")
    def load_from_bfile(self):
        while not self.src.eof():
            self.contents.append(self.src.read_uint32())
    def __iter__(self): return self.contents.__iter__()
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.seek(0)
        for attr in self.contents: dest.write_uint32(attr)
    def __getitem__(self, n):
        return self.contents[n]
    def __setitem__(self, n, value):
        self.contents[n] = value
    def __len__(self): return len(self.contents)

class PropTileList(Store):
    def __init__(self, src):
        Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.contents = array.array("H")
    def load_from_bfile(self):
        while not self.src.eof():
            self.contents.append(self.src.read_uint16())
    def __iter__(self): return self.contents.__iter__()
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.seek(0)
        for attr in self.contents: dest.write_uint16(attr)
    def __getitem__(self, n):
        return self.contents[n]
    def __setitem__(self, n, value):
        self.contents[n] = value
    def __len__(self): return len(self.contents)

class TileFauxPropsList(Store):
    def __init__(self, src):
        Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.contents = []
    def load_from_bfile(self):
        while not self.src.eof():
            word = self.src.read_uint16()
            self.contents.append((word&0x3FF, word>>10))
    def __iter__(self): return self.contents.__iter__()
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.seek(0)
        for ptype,aspect in self.contents: dest.write_uint16(ptype|(aspect<<10))
    def __getitem__(self, n):
        return self.contents[n]
    def __setitem__(self, n, value):
        self.contents[n] = value
    def __len__(self): return len(self.contents)

# maybe store should subclass list?
class TileCompositionList(Store):
    def __init__(self, src):
        Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.contents = []
    def load_from_bfile(self):
        while not self.src.eof():
            self.contents.append(self.parse([
                self.src.read_uint16() for _ in xrange(0x10)]))
    def parse(self, tw):
        return ((0x8E00|((t>>4)&0x00FF),t&0x000F,(t&0xF000)>>12) for t in tw)

    def __iter__(self): return self.contents.__iter__()
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.seek(0)
        for attr in self.contents: dest.write_uint32(attr)
    def __getitem__(self, n):
        return self.contents[n]
    def __setitem__(self, n, value):
        self.contents[n] = value
    def __len__(self): return len(self.contents)


def namecode(name, plural):
    if '\\' in name:
        stem = name[:name.find('\\')]
        ending = name[name.find('\\')+1:]
        if '/' in ending:
            return stem+ending.split('/')[1 if plural else 0]
        else:
            return stem+ending if plural else stem
    else:
        return name


class TileNameList(Store):
    def __init__(self, src):
        Store.__init__(self, src)
       
        self.empty()
        if self.src: self.load_from_bfile()
    def items(self):
        """Return a list of cutoff,name pairs."""
        return zip(self.cutoffs,self.names)
    def __iter__(self): return self.cutoffs.__iter__()
    def empty(self):
        """Purge the contents of the TileNameList."""
        self.names = []
        self.cutoffs = array.array('H')
    def write_to_bfile(self, dest):
        if dest is None: dest = self.src
        dest.seek(0)
        for cutoff, name in zip(self.cutoffs,self.names):
            dest.write_uint16(cutoff)
            dest.write_cstring(name)
    def load_from_bfile(self):
        while not self.src.eof():
            value = self.src.read_uint16()
            name = self.src.read_cstring()
            if not name and not value: break
            self.cutoffs.append(value)
            self.names.append(name)
    def namecode(self, name, plural):
        return namecode(name,plural)
    def get_name(self, idx, plural=False):
        return self.namecode(self[idx], plural)
    def __getitem__(self, idx):
        return self.names[bisect.bisect_left(self.cutoffs,idx)]
    def __setitem__(self, idx, val):
        "Note that setitem will not create new pairs, it just sets names."
        self.names[bisect.bisect_left(self.cutoffs,idx)] = val
    def __delitem__(self, cutoff):
        rmidx = bisect.bisect_left(self.cutoffs,cutoff)
        del self.cutoffs[rmidx]
        del self.names[rmidx]
    def append(self, cutoff, name):
        "Insert the name and cutoff into this object."
        insertidx = bisect.bisect_left(self.cutoffs,cutoff)
        self.cutoffs.insert(insertidx, cutoff)
        self.names.insert(insertidx, name)
    def extend(self, data):
        "Data - a list of (cutoff,name) pairs, or a dict of {cutoff:name}."
        if isinstance(data,dict):
             data = data.items()
        for pair in data: self.append(*pair)
    def __len__(self):
        return len(self.names)
