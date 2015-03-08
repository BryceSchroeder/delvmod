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
import sys
INDENT='   '
class _PrintOuter(object):
    indent=INDENT
    stream = sys.stdout
    nl = True
    def set_stream(self, stream): self.stream = stream
    def pn(self, il, *v):
        if self.nl: self.stream.write(self.indent*il)
        self.stream.write(' '.join(v)+'\n')
        self.nl = True
    def p(self, il, *v):
        if self.nl: self.stream.write(self.indent*il)
        outstr = ' '.join(v)
        self.stream.write(outstr)
        self.nl = '\n' in outstr
    def disassemble_atom(self, il, atom):
        if atom is None:
            self.p(il, "nil")
        elif isinstance(atom, int):
            self.p(il, "%d"%atom)
        elif isinstance(atom, dref):
            self.p(il, "ref %s"%self.script.get_dref_label(atom))
        elif isinstance(atom, str):
            self.p(il, repr(atom))
        else:
            assert False, "Bad atom"
    def str_disassemble_atom(self, il, atom):
        if atom is None:
            return "nil"
        elif isinstance(atom, int):
            return "%d"%atom
        elif isinstance(atom, dref):
            return "ref %s"%self.script.get_dref_label(atom)
        elif isinstance(atom, str):
            return repr(atom)
        else:
            assert False, "Bad atom"

def TypeFactory(script, src, library=None): 
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
        obj.demarshal(script, src, len(src))
        if library: obj.load_from_library(library)
        return obj



class Array(list, _PrintOuter): 
    def empty(self):
        self[:] = []
        self.references = {}
    def demarshal(self, script, src, end=None):
        self.empty()
        self.script = script
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
                self.references[n] = self[n]
                self[n] = TypeFactory(self.script,
                    library.get_dref(self[n]), library)
    def disassemble(self, out, indent):
        if len(self) < 2:
            self.pn(indent, "array [%s]"%(' '.join(map(
                 lambda (n,a):('%d: '%n)+self.str_disassemble_atom(indent+1,a),
                     enumerate(self)))))
            return
        self.pn(indent, "array [")
        for n,item in enumerate(self):
            if False: #self.references.has_key(n): 
                self.p(indent, "%4d: "%n)
                self.disassemble_atom(indent+1,self.references[n])
                self.pn(indent+1,'')
            else:
                self.p(indent, "%4d: "%n)
                print "$$$$$$$$$$$$$", repr(item)
                self.disassemble_atom(indent+1,item)
                self.pn(indent+1,'')
        self.pn(indent, "]")
    def printout(self, out, level):
        print >> out, '\t'*level, "Array"
        for n,item in enumerate(self):
            print >> out, '\t'*(level+1), "%3d:"%n, item


class DCOperation(_PrintOuter):
    def __init__(self, data):
        self.data = data
        self.decode()
    def decode(self):
        pass
    def disassemble(self, out, indent):
        self.set_stream(out)
        self.pn("UNKNOWN OPERATION")

class DCBytes(DCOperation):
    def disassemble(self, out, indent):
        self.set_stream(out)
        self.pn(indent, "bytes [")
        howmany = (80 - indent*len(self.indent) - 2)/5
        for n,b in enumerate(self.data):
            self.p(indent+1, "0x%02X "%b)
            if not (n+1)%howmany: self.p(indent,'\n')
        self.pn(indent, "]")
class Code(list, _PrintOuter):
    def empty(self):
        self[:] = []
    def demarshal(self, script, src, end=None):
        self.script = script
        typecode = src.read_uint8()
        assert typecode == 0x81
        self.argc = src.read_uint8()
        self.localc = src.read_uint8()
        self.local_names = ["var_%d"%x for x in xrange(self.localc)]
        self.arg_names = ["arg_%d"%x for x in xrange(self.argc)]
        print "reading from src Code", src
        self[:] = [DCBytes(src.readb())]
    def disassemble(self, out, indent):
        self.set_stream(out)
        self.pn(indent, "function (%s)"%(' '.join(self.arg_names)))
        if self.localc: self.pn(indent+1, 
                'with (%s)'%(' '.join(self.local_names)))
        for op in self:
            op.disassemble(out, indent+1)
    def __str__(self):
        return "<Code argc=%d localc=%d length=%d>"%(
            self.argc,self.localc,len(self))
    def load_from_library(self, library):
        pass
    def printout(self, out, level=0):
        print >> out, '\t'*level, str(self)
        self.disassemble(out, level+1)
       
class DispatchTable(dict, _PrintOuter):
    def empty(self):
        self.references = {}
        self.item_labels = {}
        self.clear()
    def demarshal(self, script, src, end):
        self.empty()
        typecode,count = src.read_fo16()
        self.script = script
        assert typecode == 0xA
        assert not count & 0xFF00
        offsets = []
        for n in xrange(count):
            atom = src.read_atom()
            signal = src.read_uint16()
            self[signal] = atom
            if isinstance(atom, util.dref):
                offsets.append((atom.offset,atom))
        self.suggest_table_names()
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
                self.references[n] = self[n]
                self[n] = TypeFactory(self.script,
                    library.get_dref(self[n]), library)
                if self.references[n].resid == self.script.res.resid:
                    self.item_labels[self.script.get_dref_label(
                        self.references[n])]=self[n]
    def suggest_table_names(self):
        for key,value in self.items():
            if key in self.references: value = self.references[key]
            if isinstance(value, dref):
                self.script.get_dref_label(
                        value, "signal_%04X"%key)
    def disassemble(self, out, indent):
        self.set_stream(out)
        self.pn(indent, "index [")
        for key,value in self.items():
            if key in self.references: value = self.references[key]
            if value is None: 
                self.pn(indent+1, '0x%04X: nil'%key)
            elif isinstance(value, int):
                self.pn(indent+1, '0x%04X: %d'%(key,value))
            elif isinstance(value, dref):
                self.pn(indent+1, '0x%04X: ref %s'%(key,
                    self.script.get_dref_label(
                        value, "signal_%04X"%key)))
            else:
                self.pn(indent+1,
                    '0x%04X:'%(key))
                value.disassemble(out, indent+2)
        self.pn(indent, "]")
    def printout(self, out, level):
        print >> out, '\t'*level, "Dispatch Table"
        for signal,item in self.items():
            print >> out, '\t'*(level+1), "0x%04X:"%signal 
            if hasattr(item, 'printout'): item.printout(out, level+2)
            else: print >> out, '\t'*(level+2), repr(item)[:40]

class Class(_PrintOuter):
    def __init__(self, script, src=None, end=None):
        self.dispatch = None 
        self.script = script
        if src: self.demarshal(self.script, src, end)
    def demarshal(self, script, src, end=None):
        self.script = script
        src.seek(0)
        dtoffset = src.read_uint16()
        src.seek(dtoffset)
        self.dtindex = DispatchTable()
        self.dtindex.demarshal(self.script, src, dtoffset)
    def load_from_library(self, library):
        self.dtindex.load_from_library(library)
        self.dispatch = self.dtindex
    def disassemble(self, out, level):
        print >> out, '\t'*level, "Class with Dispatch Table"
        self.dtindex.disassemble(out, level+1)
    def disassemble(self, out, indent):
        self.pn(indent, "class (")
        for label, item in self.dtindex.item_labels.items():
            self.pn(indent+1, "%s:"%label)
            item.disassemble(out, indent+2)
        self.dtindex.disassemble(out, indent+1)
        self.pn(indent, ")")
 
class Script(store.Store):
    class_container = False
    def __init__(self, src):
        store.Store.__init__(self, src)
        self.symbol_table = {}
        self.unique_symbol = 0
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.obj = None
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.write(self.cobj.get_data())
    def get_dref_label(self, ref, suggestion=None):
        if ref in self.symbol_table:
            return self.symbol_table[ref]
        if ref.resid == self.res.resid and ref.offset in self.symbol_table:
            return self.symbol_table[ref.offset]
        if suggestion is None: 
            suggestion = "label_%d"%self.unique_symbol
            self.unique_symbol += 1
        self.symbol_table[ref] = suggestion
        self.symbol_table[ref.offset] = suggestion
        return suggestion
    def get_offset_label(self, offset, suggestion=None):
        return self.get_dref_label(dref(self.res.resid, offset))
        
    def load_from_bfile(self):
        #print repr(self.src.resource)
        self.src.seek(0)
        if self.class_container: 
            self.obj = Class(self, self.src, len(self.src))
        else:
            cntype = self.src.read_uint8()
            self.src.seek(0)
            if cntype == 0x81:
                self.obj = Code()
                self.obj.demarshal(self, self.src)
            elif cntype&0xF0 == 0x90:
                self.obj = Array()
                self.obj.demarshal(self, self.src)
            elif cntype&0xF0 == 0xA0:
                self.obj = DispatchTable()
                self.obj.demarshal(self, self.src,len(self.src))
            else:
                self.obj = self.src.read_atom()
    def load_from_library(self, library):
        if hasattr(self.obj, 'load_from_library'):
            self.obj.load_from_library(library)
    def printout(self, out, level=0):
        if not hasattr(self.obj, 'disassemble'):
            print >> out, "Atom:", self.obj
            return
        print >> out, "-- Script Object from %s --"%repr(self.src)
        self.obj.disassemble(out, 1)
        
        
        
class ClassContainer(Script):
    class_container = True


