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
import store, util
from util import dref

def TypeFactory(src, library=None): 
        rewind = src.tell()
        cntype = src.read_uint8()
        print "TYPEFACTORY %02X %04X"%(cntype,src.read_uint32())
        src.seek(rewind)
        print repr(src)

        if cntype == 0x81:
            obj = Code()
        elif cntype&0xF0 == 0x90:
            obj = Array()
        else:
            return src.read_cstring()
        obj.demarshal(src, len(src))
        if library: obj.load_from_library(library)
        return obj



class Array(list): 
    def empty(self):
        self[:] = []
    def demarshal(self, src, end=None):
        typecode,count = src.read_fo16()
        assert typecode == 9
        for n in xrange(count):
            self.append(src.read_atom())
    def marshal(self, dst):
        dst.write_do16(9, len(self))
        for a in self:
            dst.write_atom(a)
    def load_from_library(self, library):
        for n in xrange(len(self)):
            if isinstance(self[n], dref):
                self[n] = TypeFactory(library.get_dref(self[n]), library)
    def printout(self, out, level):
        print >> out, '\t'*level, "Array"
        for n,item in enumerate(self):
            print >> out, '\t'*(level+1), "%3d:"%n, item


class Code(list):
    def empty(self):
        self[:] = []
    def demarshal(self, src, end=None):
        typecode = src.read_uint8()
        assert typecode == 0x81
        self.argc = src.read_uint8()
        self.localc = src.read_uint8()
        print "reading from src Code", src
        self[:] = src.readb()
    def __str__(self):
        return "<Code argc=%d localc=%d length=%d>"%(
            self.argc,self.localc,len(self))
    def load_from_library(self, library):
        pass
    def printout(self, out, level=0):
        print >> out, '\t'*level, str(self)
       
class DispatchTable(dict):
    def empty(self):
        self.clear()
    def demarshal(self, src, end):
        typecode,count = src.read_fo16()
        assert typecode == 0xA
        assert not count & 0xFF00
        offsets = []
        for n in xrange(count):
            atom = src.read_atom()
            signal = src.read_uint16()
            self[signal] = atom
            if isinstance(atom, util.dref):
                offsets.append((atom.offset,atom))
        if not offsets: return
        offsets.sort()
        for (a,da),(b,db) in zip(offsets[:-1],offsets[1:]):
            da.length = b-a
        offsets[-1][1].length = end - offsets[-1][1].offset
    def marshal(self, dst):
        dst.write_uint8(0xA0)
        dst.write_uint8(len(self))
        for k,v in self.items():
             dst.write_atom(v)
             dst.write_uint16(k)
    def load_from_library(self, library):
        for n in self:
            if isinstance(self[n], dref):
                self[n] = TypeFactory(library.get_dref(self[n]), library)
    def printout(self, out, level):
        print >> out, '\t'*level, "Dispatch Table"
        for signal,item in self.items():
            print >> out, '\t'*(level+1), "0x%04X:"%signal 
            if hasattr(item, 'printout'): item.printout(out, level+2)
            else: print >> out, '\t'*(level+2), repr(item)[:40]

class Class(object):
    def __init__(self, src=None, end=None):
        self.dispatch = None
        if src: self.demarshal(src, end)
    def demarshal(self, src, end=None):
        src.seek(0)
        dtoffset = src.read_uint16()
        src.seek(dtoffset)
        self.dtindex = DispatchTable()
        self.dtindex.demarshal(src, dtoffset)
    def load_from_library(self, library):
        self.dtindex.load_from_library(library)
        self.dispatch = self.dtindex
    def printout(self, out, level):
        print >> out, '\t'*level, "Class with Dispatch Table"
        self.dtindex.printout(out, level+1)
 
class Script(store.Store):
    class_container = False
    def __init__(self, src):
        store.Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.obj = None
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.write(self.cobj.get_data())
        
    def load_from_bfile(self):
        #print repr(self.src.resource)
        self.src.seek(0)
        if self.class_container: 
            self.obj = Class(self.src, len(self.src))
        else:
            cntype = self.src.read_uint8()
            self.src.seek(0)
            if cntype == 0x81:
                self.obj = Code()
                self.obj.demarshal(self.src)
            elif cntype&0xF0 == 0x90:
                self.obj = Array()
                self.obj.demarshal(self.src)
            elif cntype&0xF0 == 0xA0:
                self.obj = DispatchTable()
                self.obj.demarshal(self.src,len(self.src))
            else:
                self.obj = self.src.read_atom()
    def load_from_library(self, library):
        if hasattr(self.obj, 'load_from_library'):
            self.obj.load_from_library(library)
    def printout(self, out, level=0):
        if not hasattr(self.obj, 'printout'):
            print >> out, "Atom:", self.obj
            return
        print >> out, "-- Script Object from %s --"%repr(self.src)
        self.obj.printout(out, level+1)
        
        
        
class ClassContainer(Script):
    class_container = True


