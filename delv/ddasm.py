# Copyright 2016 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
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
from cStringIO import StringIO
import delv
import delv.util
import delv.rdasm_symbolics as symbolics
INDENT = '    '
INCLUDES = """
include Delver.Model
include Delver.Main
include Cythera
use System
""".strip()
class Disassembler(object):
    def __init__(self,context_resource=None):
        self.labels = {}
        self.inhibit_subs = []
        self.class_data_labels = {}
        self.pseudo_ops = {}
        self.context_resource=context_resource
    def disassemble(self, code, force_classmode=False, preamble=None):
        self.infile = delv.util.BinaryHandler(code, coverage_map=True)
        if force_classmode:
            self.content = [DClass(self.infile)]
        else:
            self.content = [read_DVMObj(self.infile)]
        for content in self.content: content.load(self)
            #another = self.content[0].load(self)
            #while another: 
            #    self.infile.seek(another)
            #    self.content.append(read_DVMObj(self.infile))
            #    another = self.content[-1].load(self)
        postscript = []
        of = StringIO()
        print >> of, preamble if preamble else "// DDASM %s"%delv.version
        print >> of, INCLUDES
        us = self.infile.cm_unseen()
        content = self.content[0]
        if len(us)==1 and not isinstance(self.content[0], DClass) and us[0][0]+us[0][1] == len(self.infile):
            usof,usln = us[0]
            self.infile.seek(usof)
            c = self.infile.readb(usln)
            postscript.append((usof, "{"+' '.join(['%02X'%x for x in c])+"}"))
        if us and not isinstance(self.content[0], DClass):
            print >> of, "// WARNING: Disassembly skipped %d area(s):"%len(us)
            print >> of, "//      Offset       Length"
            for usof,usln in us:
                print >> of, "//      0x%04X       %d"%(usof,usln)
        else:
            p = self.infile.tell()
            for usof, usln in us:
                self.infile.seek(usof)
                obj = read_DVMObj(self.infile, usln)
                if isinstance(obj, DFunction):
                    obj.load(self, namehint='Sub')
                    content.register_sub(obj)
                elif hasattr(obj, 'load'):
                    obj.load(self) 
            self.infile.seek(p)
        if self.context_resource:
            print >> of, 'resource 0x%04X\n'%self.context_resource
        #print >> of, '// Class Data:'
        #for k,v in self.class_data_labels.items():
        #    print >> of, '// Class Data: ', k, v
        postscript.sort(reverse=True)
        skipped = None
        for content in self.content:
            print >> of, '\n// 0x%04X:'%content.offset
            skipped = postscript.pop() if (postscript and not skipped) else None
            if skipped and content.offset > skipped[0]:
                print >> of, '\n// Skipped region at 0x%04X'%skipped[0]
                print >> of, skipped[1]
                skipped = None
            content.show(0, of)
        if skipped:
            print >> of, '\n// Skipped ending at 0x%04X:'%skipped[0]
            print >> of, skipped[1]
        return of.getvalue()
    def register_class_data(self, label, field):
        self.class_data_labels[label] = (field.offset, field)
    def get_label(self, position, hint=None, pseudo_op=None, unique=True):
        if not self.labels.has_key(position):
            if hint is False: return False
            self.labels[position]=(hint if hint else 'Label')+(
                "%04X"%position if unique else '')
        if pseudo_op:
            self.pseudo_ops[position] = pseudo_op
        return self.labels[position]


class DVMObj(object):
    """This is the common base class for Delver VM script objects,
       excepting those that can be exactly mapped to Python
       equivalents (strings, integers, True, False, and None.)
       DVMObjs thus include arrays, tables, classes & functions."""
    pass
class DData(DVMObj):
    def __init__(self, ifile):
        self.near = ifile
        self.dd=None
        self.offset = ifile.tell()
        #size = ifile.read_uint16() & 0x0FFF
        self.value = ifile.read_uint32()
    def load(self, dd, anonymous=False):
        self.dd = dd
        if not anonymous: self.name = dd.get_label(self.offset, "ClassData")
    def show(self, i, of):
        name = None if not self.dd else self.dd.get_label(self.offset, False)
        print >> of, INDENT*i+'class_data %s ( %s )'%(name if name else '', word2str(self.value,self.dd))
        # if you prefer this style...
        # print >> of, INDENT*i+'%s: {%08X}'%(name, self.value)

class DArray(list, DVMObj):
    def __init__(self, ifile):
        self.near = ifile
        self.dd=None
        self.offset = ifile.tell()
        size = ifile.read_uint16() & 0x0FFF
        for _ in xrange(size):
            self.append(ifile.read_uint32())
    def load(self, dd, anonymous=False):
        self.dd = dd
        #print ">>> Loading the array at 0x%04X"%self.offset
        if not anonymous: self.name = dd.get_label(self.offset, "Array")
        for i in xrange(len(self)):
            if self[i] & 0x80000000:
                addr = self[i]&0xFFFF
                self.near.seek(addr)
                #print ">>> Preparing to load", i, '0x%04X'%(self[i]&0xFFFF), self[i]
                if self.dd.get_label(addr,False):
                    continue
                self[i] = read_DVMObj(self.near)
                if hasattr(self[i],'load'): self[i].load(dd, 
                                                         anonymous=True)
    def show(self, i, of):
        name = None if not self.dd else self.dd.get_label(self.offset, False)
        print >> of, INDENT*i+'array %s('%(name if name else ''),
        if len(self)> 6: print >> of, '\n'+INDENT*(i+1),
        for item in self:
            if isinstance(item, str):
                print >> of, json.dumps(item),
            elif hasattr(item, 'show'):
                item.show(i+1, of)
            else:
                print >> of, word2str(item,self.dd),
            if len(self) > 6: print >> of, '\n'+INDENT*(i+1),
        print >> of, ')',
        if len(self)> 6: print >> of, ''

    


class DTable(dict, DVMObj):
    def __init__(self, ifile):
        self.near = ifile
        self.field_ordering = []
        self.subvals = []
        self.offset = ifile.tell()
        self.dd=None
        self.ovals = []
        size = ifile.read_uint16() & 0x0FFF
        for _ in xrange(size):
            value = ifile.read_uint32()
            key = ifile.read_uint16()
            self.field_ordering.append(key)
            self.subvals.append(value)
            if not self.has_key(key) or value != 0x5000FFFF:
                self[key] = value
    def load(self, dd, anonymous=False):
         self.dd = dd
         if not anonymous: self.name = dd.get_label(self.offset, "Table")
         #for k,v in self.items():
         for k,v in zip(self.field_ordering, self.subvals):
             if v & 0x80000000:
                 self.near.seek(v&0xFFFF)
                 self[k] = read_DVMObj(self.near)
                 if hasattr(self[k],'load'): self[k].load(dd,
                                                          anonymous=True)
                 self.ovals.append(self[k])
             else: 
                 self.ovals.append(v)
    def show(self, i, of):
        name = None if not self.dd else self.dd.get_label(self.offset, False)
        print >> of, INDENT*i+'table (',#%s('%(name if name else ''),
        if len(self)> 3: print >> of, '\n'+INDENT*(i+1),
        
        for key,item in zip(self.field_ordering, self.ovals):
        #for key,item in self.items():
            print >> of, '0x%04X ='%key,
            if isinstance(item, str):
                print >> of, json.dumps(item),
            elif hasattr(item, 'show'):
                item.show(0, of)
            else:
                print >> of, word2str(item, self.dd),
            if len(self) > 3:
                print >> of, '\n'+INDENT*(i+1),
        print >> of, ')',
        if len(self)> 3: print >> of, ''

class DClass(DTable):
    def __init__(self, ifile, class_name='Object'):
        self.class_name = class_name
        self.table_offset = ifile.read_uint16()
        ifile.seek(self.table_offset)
        self.force_field = []
        self.content_order = []
        self.order_offsets = []
        self.subs = []
        DTable.__init__(self, ifile)
    def register_sub(self, sub):
        self.subs.append((sub.offset, sub))
    
    def load(self, dd, anonymous=False):
         self.dd =dd
         self.method_locs = {}
         valids = []
         for k,v in self.items():
             if v & 0x80000000: 
                 #print "CTXR", dd.context_resource, 
                 if (v&0x7FFF0000)>>16 != dd.context_resource: continue
                 valids.append((v&0xFFFF,k))
                 self.dd.inhibit_subs.append(v&0xFFFF)
         valids.sort()

         for (st,k),(en,_)in zip(valids,valids[1:]+[(self.table_offset,-1)]):
             self.content_order.append(k)
             self.order_offsets.append(st)
             self.near.seek(st)
             #print "%20s (0x%04X): 0x%04X-0x%04X"%(
             #    symbolics.DASM_OBJECT_HINTS.get(k,'????'),k,st,en)
             self.dd.get_label(st, 
                 hint=symbolics.DASM_OBJECT_HINTS.get(k,"Field%04X"%k),
                 unique=False)
             self.method_locs[k] = st
             p = self.near.tell()
             self.near.seek(st)
             self[k] = read_DVMObj(self.near, en-st)
             if hasattr(self[k],'load'): 
                 #print '%x'%st, en-st, k, self[k]
                 self[k].load(dd)
             self.near.seek(p)
    def show(self, i, of):
        #for k, v in symbolics.ASM_OBJECT_HINTS.items():
        #    print >> of,k,v
        showcd = self.dd.class_data_labels.items()
        showcd = [(v[0], k, v[1]) for k,v in showcd]
        showcd.sort()
        print >> of, '//', showcd

        print >> of, 'field_order ('+', '.join(
            ['0x%04X'%x for x in self.field_ordering])+')'
        print >> of, "// Standard Symbol  Key     Value or Offset"
        for k, v in self.items():
            print >> of, '// %-16s 0x%04X:'%(
                    symbolics.DASM_OBJECT_HINTS.get(k,'????'), k),
            if not isinstance(v,int):
                print >> of, '0x%04X'%self.method_locs[k]
            else:
                print >> of, '0x%08X'%(v)
        print >> of, (INDENT*i)+'class', self.class_name 
        if self.content_order:
            for item in self:
                if not item in self.content_order:
                    self.content_order.append(item)
                    self.order_offsets.append(0x10000)
       
        for offset, name, dobj in showcd:
            self.content_order.append(dobj)
            self.order_offsets.append(offset)

        order = []
        if self.content_order:
            tmpor = []
            for ck,oo in zip(self.content_order, self.order_offsets):
                if isinstance(ck,DVMObj):
                    tmpor.append((oo,ck,ck.name))
                else:
                    tmpor.append((oo,self[ck],ck))
            for subo, sub in self.subs:
                tmpor.append((subo,sub,None))
            tmpor.sort()
            order = [(self.dd.labels.get(ofs,fv), itm) for ofs,itm,fv in tmpor]
        else:
            for cf,cv in self.items():
                order.append((cv, cf))
            for subo, sub in self.subs:
                order.append((self.dd.labels[subo], sub))
            

        for k,item in order:
                
            #item = self[k]
            print >> of
            #if k: print >> of, (' Field 0x%04X '%k).center(78,'/')
            if hasattr(item, 'show'):
                item.show(0, of)
            else:
                print >> of, 'class_field %s %s'%(
                    symbolics.DASM_OBJECT_HINTS['_name']
                    +'.'+symbolics.DASM_OBJECT_HINTS[k] if symbolics.DASM_OBJECT_HINTS.has_key(k) else word2str(k,self.dd),
                     word2str(item,self.dd),)

import json
class Opcode(object):
    mnemonic = 'NOP'
    expect = 0
    symbols = {}
    fixed_field = None
    suppress_labels = False
    def __init__(self, opcode, bfile, func):
        #print ">>> %02X"%opcode, bfile.tell()
        self.func = func
        self.dd = func.dd
        self.offset = bfile.tell()-1
        self.content = []
        self.opcode = opcode
        self.parse(bfile)
        self.prefix = ''
        self.field = None
        if self.fixed_field == 1:
            self.field = bfile.read_uint8()
        elif self.fixed_field == -1:
            self.field = bfile.read_sint8()
        elif self.fixed_field == 2:
            self.field = bfile.read_uint16()
        elif self.fixed_field == -2:
            self.field = bfile.read_sint16()
        elif self.fixed_field == 4:
            self.field = bfile.read_uint32()
        elif isinstance(self.fixed_field, str):
            self.field = bfile.read_uint16()
            self.label = func.dd.get_label(self.field, self.fixed_field)
        elif self.fixed_field is str:
            self.field = bfile.read_cstring()
        elif isinstance(self.fixed_field, dict):
            bsize = self.fixed_field['_size']
            self.prefix = self.fixed_field['_name']+'.'
            if bsize == 1:
                 self.field = bfile.read_uint8()
            elif bsize == 2:
                 self.field = bfile.read_uint16()
        self.expectation()
    def expectation(self):
        for n in xrange(self.expect):
            self.func.expectation(self.expect_cb)
        if self.expect: self.func.iseg(self.expect)
    def expect_cb(self, op, bfile):
        assert op == 0x40
        return OpEnd(op, bfile, self.func)
    def parse(self, bfile):
        pass
    def show(self, idnt, strm):
        d = self.dd.get_label(self.offset, False)
        if d and not self.suppress_labels: print >> strm, (INDENT*idnt)+d+':'
        print >> strm, (INDENT*idnt)+self.mnemonic + ' ' + self.parameters()
    def parameters(self):
        if isinstance(self.fixed_field, str):
            return self.label
        if self.fixed_field is str:
            return json.dumps(self.field)
        if isinstance(self.fixed_field,dict):
            if self.fixed_field.has_key(self.field):
                return self.prefix+self.fixed_field[self.field]
            else:
                return "0x%X"%self.field
        if self.field is None: return ''
        if self.field < 0: return '%d'%self.fixed_field
        return ('0x%'+('0%dX'%(self.fixed_field*2)))%self.field
        
       

class OpLocal(Opcode):
    mnemonic = 'loc'
    def parse(self, bfile):
        self.symbol = self.func.get_local(self.opcode, 
                                          self.mnemonic.title())
    def parameters(self):
        return self.symbol

class OpArg(OpLocal):
    mnemonic = 'arg'

class OpEnd(Opcode):
    mnemonic = 'end'
    def show(self, idnt, strm):
        print >> strm, (INDENT*(idnt-1)
            ) + self.mnemonic + ' ' + self.parameters()
class OpSeti(Opcode):
    mnemonic = 'set_index'
    expect = 3



class OpData(Opcode):
    mnemonic = 'data'
    def parse(self, bfile):
        self.size = bfile.read_uint16()
        self.startpos = bfile.tell()
        #print "> Data opcode, offset 0x%04X"%self.offset, "size", self.size, "start 0x%04X"%self.startpos
        self.content = read_DVMObj(bfile, self.size)
        #print ">> Loaded", ','.join(['%08X'%x for x in self.content])
        if hasattr(self.content,'load'):self.content.load(self.dd,
                                                          anonymous=True)
        bfile.seek(self.size+self.startpos)
    def parameters(self):
        buf = StringIO()
        self.content.show(0,buf)
        return buf.getvalue().strip()

class OpByte(Opcode):
    mnemonic = 'byte'
    def parse(self, bfile):
        self.immediate = bfile.read_sint8()
    def parameters(self):
        return str(self.immediate)
class OpShort(Opcode):
    mnemonic = 'short'
    def parse(self, bfile):
        self.immediate = bfile.read_sint16()
    def parameters(self):
        return str(self.immediate)

def word2str(i,dd):
        #if dd is None: dd = Disassembler.current_instance # doesn
        if i <= 0x07FFFFFF:
            return str(i)
        elif i <= 0x0FFFFFFF:
            return str(i | ~(-1&0x0FFFFFFF))
        elif i < 0x30000000:
            return '<%08X>'%i
        elif i < 0x40000000: 
            resid = i&0xFFFF
            if symbolics.DASM_RESOURCE_NAME_HINTS.has_key(resid):
                respart = (symbolics.DASM_RESOURCE_NAME_HINTS['_name']
                          +'.'+symbolics.DASM_RESOURCE_NAME_HINTS[resid])
            else:
                respart = '0x%04X'%resid
            return '%s[%d]'%(respart, 0xFFF&(i>>16))
        elif i < 0x50000000:
            assert i&0xFF000000 == 0x40000000
            classpart = (i & 0xFF0000)>>16
            whichpart = i& 0xFFFF
            if classpart == 0x40 and symbolics.DASM_CYTHERA_CHARACTERS.has_key(whichpart):
                whichpart = 'Characters.'+symbolics.DASM_CYTHERA_CHARACTERS[whichpart]
            else:
                whichpart = '0x%04X'%whichpart
            if symbolics.DASM_OBJ_NAME_HINTS.has_key(classpart):
                classpart = (symbolics.DASM_OBJ_NAME_HINTS['_name']+'.'
                     +symbolics.DASM_OBJ_NAME_HINTS[classpart])
            else:
                classpart = '0x%02X'%classpart

            return whichpart+'@'+classpart #'0x%04X@0x%02X'%(i&0xFFFF, (i&0xFF0000)>>16)
        elif i == 0x50000000:
            return 'false'
        elif i == 0x50000001:
            return 'true'
        elif i == 0x5000FFFF:
            return 'none'
        elif i == 0x5000FFFE:
            return 'empty'
        elif 0x50000000 < i < 0x80000000:
            return '<%08X>'%i
        else:
            resid =(i&0x7FFF0000)>>16
            offset = i&0xFFFF 
            if resid == dd.context_resource:
                respart = 'here'
            elif symbolics.DASM_RESOURCE_NAME_HINTS.has_key(resid):
                respart = (symbolics.DASM_RESOURCE_NAME_HINTS['_name']
                          +'.'+symbolics.DASM_RESOURCE_NAME_HINTS[resid])
            else:
                respart = '0x%04X'%resid
            offspart = dd.get_label(offset,False) or '0x%04X'%offset
            
            return respart+':'+offspart


class OpWord(Opcode):
    mnemonic = 'word'
    def parse(self, bfile):
        self.immediate = bfile.read_uint32()
        if 0x08000000 < self.immediate <= 0x0FFFFFFF:
            self.immediate |= ~(-1&0x0FFFFFFF)
    def parameters(self):
        i=self.immediate
        if 0x10000000 <= i <= 0x10000030:
            return '&Local%02X'%((i&0xFF)-1)
        return word2str(i,self.dd)
class OpSetl(Opcode):
    mnemonic = 'set_local'
    expect = 1
    def parse(self, bfile):
        self.which = bfile.read_uint8()
        self.symbol = self.func.get_local(self.which, "Local")
    def parameters(self):
        return self.symbol

class OpSubr(Opcode):
    suppress_labels = True
    mnemonic = 'subroutine'
    def parse(self, bfile):
        self.label = self.dd.get_label(bfile.tell()-1, 'InternalSub')
        self.argcount = bfile.read_uint8()
        self.loccount = bfile.read_uint8()
    def parameters(self):
        return '%d %d %s'%(self.argcount, self.loccount, self.label)

class OpWriteNearWord(Opcode):
    expect = 1
    mnemonic = 'write_near_word'
    fixed_field = 2


class OpGlobal(Opcode):
    mnemonic = 'global'
    def parse(self, bfile):
        self.immediate = bfile.read_uint8()
        sym = symbolics.DASM_GLOBAL_NAME_HINTS.get(self.immediate, None)
        self.parameter = ('Globals.'+sym) if sym else '0x%02X'%self.immediate
    def parameters(self):
        return self.parameter

class OpSys(Opcode):
    mnemonic = 'sys'
    expect = 1
    def parameters(self):
        return symbolics.DASM_SYSCALL_NAMES.get(self.opcode, "0x%02X"%self.opcode)
    
class OpWriteFarWord(Opcode):
    mnemonic = 'write_far_word'
    expect = 1
    def parse(self, bfile):
        self.resid=bfile.read_uint16()
        self.offset = bfile.read_uint16()
    def parameters(self):
        return '0x%04X 0x%04X'%(self.resid, self.offset)

class OpClassVariable(Opcode):
    mnemonic = 'class_member'
    def parse(self, bfile):
        self.classfield=bfile.read_uint8()
        self.tidx = bfile.read_uint8()
    def parameters(self):
        if symbolics.DASM_OBJECT_HINTS.has_key(self.classfield):
            return 'Object.%s %d'%(symbolics.DASM_OBJECT_HINTS[self.classfield],
                           self.tidx)
        else:
            return '%s %d'%('0x%02X'%self.classfield, self.tidx)

class OpReadFarWord(OpWriteFarWord):
    mnemonic = 'load_far_word'
    expect = 0
class OpEndr(OpEnd):
    mnemonic=''#endr'
    def parameters(self):
        return ''
class OpConversationResponse(Opcode):
    mnemonic = 'conversation_response'
    def parse(self, bfile):
        self.response = bfile.read_cstring()
        self.nextblock = bfile.read_uint16()
        self.label = self.dd.get_label(self.nextblock, 'ConvNext', OpEndr)
    def parameters(self):
        return "%s else %s "%(json.dumps(self.response),self.label)

class OpSwitch(Opcode):
    mnemonic='switch'
    expect = 1
    def expect_cb(self, op, bfile):
        assert op == 0x40
        n = bfile.read_uint16()
        f = OpCases(op, bfile, self.func)
        f.labels = [
            self.dd.get_label(bfile.read_uint16(),'Case') for _ in xrange(n)
            ]
        return f
class OpCases(OpEnd):
    mnemonic = 'cases'
    def parameters(self):
        return '( ' + ', '.join(self.labels) + ' )'
class OpThen(OpEnd):
    mnemonic='then'
    def parse(self, ifile):
        self.target = ifile.read_uint16()
        self.label =  self.dd.get_label(self.target, 'Conditional')
    def parameters(self):
        return self.dd.get_label(self.target, 'Conditional')

class OpIf(Opcode):
    expect=1
    mnemonic='if'
    def expect_cb(self,op,bfile):
        assert op == 0x40
        then= OpThen(op,bfile,self.func)
        # then.target = bfile.read_uint16() # Why was it ever this way??
        return then

class OpBranch(Opcode):
    expect=0
    mnemonic='branch'
    def parse(self, bfile):
        self.target = bfile.read_uint16()
        self.dd.get_label(self.target, 'Branch')
    def parameters(self):
        return self.dd.get_label(self.target, 'Branch')
    

class OpIfNot(OpIf):
    mnemonic = 'if_not'

def Opcoder(themnemonic, theexpect=0, thefixed=None):
    class _Op(Opcode):
        mnemonic=themnemonic
        expect=theexpect
        fixed_field=thefixed
    return _Op

class OpLoadNearWord(Opcode):
    mnemonic = 'load_near_word'
    expect=0
    #fixed_field = 'ClassData'
    def parse(self, bfile):            
        self.field = bfile.read_uint16()
        self.label = self.dd.get_label(self.field, 'ClassData')
        t=bfile.tell()
        bfile.seek(self.field)
        d = DData(bfile)
        d.load(self.dd)
        self.dd.register_class_data(self.label, d)
        bfile.seek(t)
    def parameters(self):
        return self.label
        

# TODO: deal with labels.
OpTable = {
    0x41: OpByte,
    0x42: OpShort,
    0x43: OpWord,
    0x44: Opcoder('string', 0, str),
    0x45: OpData,
    0x46: Opcoder('index'),
    0x47: OpLoadNearWord,#Opcoder('load_near_word', 0, 'ClassData'),
    0x48: OpGlobal,
    0x49: OpReadFarWord,
    0x4A: Opcoder('add'),
    0x4B: Opcoder('sub'),
    0x4C: Opcoder('mul'),
    0x4D: Opcoder('div'),
    0x4E: Opcoder('mod'),
    0x4F: Opcoder('lt'),
    0x50: Opcoder('le'),
    0x51: Opcoder('gt'),
    0x52: Opcoder('ge'),
    0x53: Opcoder('ne'),
    0x54: Opcoder('eq'),
    0x55: Opcoder('neg'),
    0x56: Opcoder('bitwise_and'),
    0x57: Opcoder('bitwise_or'),
    0x58: Opcoder('bitwise_xor'),
    0x59: Opcoder('bitwise_not'),
    0x5A: Opcoder('left_shift'),
    0x5B: Opcoder('right_shift'),
    0x5C: Opcoder('and'),
    0x5D: Opcoder('or'),
    0x5E: Opcoder('not'),
    0x5F: Opcoder('len'),
    0x60: Opcoder('has_member', 0, symbolics.DASM_OBJECT_HINTS),
    0x61: OpClassVariable,
    0x62: Opcoder('get_field', 0, symbolics.DASM_STRUCT_HINTS),
    0x63: Opcoder('cast', 0, symbolics.DASM_OBJ_NAME_HINTS),
    0x64: Opcoder('is_type',0, symbolics.DASM_OBJ_NAME_HINTS),
    0x81: OpSubr,
    0x82: OpSetl,
    0x83: Opcoder('write_near_word', 1, 'ClassData'),
    0x84: OpSeti,
    0x85: OpWriteFarWord,
    0x86: Opcoder('set_field', 2, symbolics.DASM_STRUCT_HINTS),
    0x87: Opcoder('set_global', 1, symbolics.DASM_GLOBAL_NAME_HINTS),
    0x88: OpBranch,#coder('branch', 0, 'Branch'), 
    0x89: OpSwitch,
    0x8A: Opcoder('print', 1),
    0x8B: Opcoder('return', 1),
    0x8C: OpIf,
    0x8D: OpIfNot,
    0x8E: Opcoder('exit'),
    0x8F: Opcoder('conversation_prompt', 0, str),
    0x90: OpConversationResponse,
    0x92: Opcoder('ai_state', 1, 1),
    0x93: Opcoder('gui_close',1),
    
    0x9B: Opcoder('gui',1,symbolics.DASM_GUI_NAME_HINTS),
    0x9C: Opcoder('call_index', 2, 2),
    0x9D: Opcoder('method', 1, symbolics.DASM_OBJECT_HINTS),
    0x9E: Opcoder('call_subroutine', 1, 'Sub'),
    0x9F: Opcoder('call_resource', 1, symbolics.DASM_RESOURCE_NAME_HINTS)
}


SUBS_CHARS = {
  "'": "\\'",
  '\n': '\\n',
  '\t': '\\t',
  '\r': '\\r'
}
import sys
class DDirect(DVMObj):
    def __init__(self, ifile, length_hint=None):
        self.offset = ifile.tell()
        self.data = ifile.readb(length_hint) if length_hint else ifile.readb()
    def load(self, dd, *argv):
        self.dd = dd
    def show(self,i=0, ost=sys.stdout):
        print >> ost, i*INDENT+'{',
        print >> ost, ' '.join(['%02X'%x for x in self.data]),
        print >> ost, '}'

class DFunction(DVMObj):
    def get_local(self, idx, hint=None):
        if not self.local.has_key(idx):
            self.local[idx] = (hint if hint else 'Var')+"%02X"%idx
        return self.local[idx]
    def expectation(self, cb):
        self.expect_close.append(cb)
    def iseg(self, n):
        self.indent_segments.append(n)
    def __init__(self, ifile, length_hint=None, bonus_indents=0):
        self.bi = bonus_indents
        self.local = {}
        self.near = ifile
        self.offset = ifile.tell()
        assert ifile.read_uint8() == 0x81
        self.arg_count = ifile.read_uint8()
        assert self.arg_count < 0x10
        self.local_count = ifile.read_uint8()
        assert self.local_count < 0x30
        for n in xrange(self.local_count): self.get_local(n,hint="Local")
        self.body = ifile.read() if length_hint is None else ifile.read(
            length_hint-3) 
        self.size = len(self.body)
    def arglist(self):
        return ', '.join([self.get_local(x|0x30) for x in xrange(
            self.arg_count)])
    def show(self, i=0, ost=sys.stdout):
        print >> ost, i*INDENT+'function %s(%s) ('%(
             self.name, self.arglist())
        #print "***",self.bi,self.name
        i += self.bi
        for n in xrange(self.local_count):
            print >> ost, (1+i)*INDENT+'var Local%02X'%n 
            #print >> ost, (1+i)*INDENT+"// %d local vars"%self.local_count
        for il,line in zip(self.ilevel,self.code):
            il += self.bi
            if isinstance(line, tuple):
                dat, offs = line
                if offs < 0: continue
                lb = self.dd.get_label(offs, False)
                if lb: 
                    print >> ost, (il)*INDENT+lb+':'
                #else:
                #    print >> ost, (il)*INDENT+'// 0x%04X'%offs
                if not dat: continue
                ost.write((il)*INDENT+"'")
                for cn, ch in enumerate(dat):
                    lb = self.dd.get_label(offs+cn, False)
                    
                    if cn and lb:
                        ost.write("'\n"+(il)*INDENT)
                        ost.write(lb+':\n')
                        ost.write((il)*INDENT+"'")
                    if ch in SUBS_CHARS:
                        ost.write(SUBS_CHARS[ch])
                    elif 0x80 > ord(ch) >= 0x20: ost.write(ch)
                    else: ost.write('\\x%02X'%ord(ch))
                ost.write("'\n")
                    
                         
                #print >> ost, (il)*INDENT+"'"+repr(dat+'"')[1:-2]+"'"
            else:
                line.show(il, ost)
        print >> ost, i*INDENT+')'
    def load(self, dd, anonymous=False, namehint="Function"):
        self.dd = dd
        self.name = dd.get_label(self.offset, namehint)
        t = self.near.tell()
        
        self.near.seek(self.offset+3)
        self.code = []
        textbuf = [] 
        subs_found = []
        self.expect_close = []
        self.indent_segments = []
        self.ilevel = []
        ps_after = None
        mode = 'direct'
        lastoffset = self.near.tell()
        while self.near.tell() < self.offset+self.size+3:
            
            if self.near.tell() in self.dd.pseudo_ops:
                psu = self.dd.pseudo_ops[self.near.tell()]
                del self.dd.pseudo_ops[self.near.tell()]
                ps_after = psu(opcode, self.near, self)
                is_after = len(self.indent_segments)+2
                #self.indent_segments[-1] -= 1
                #if not self.indent_segments[-1]: self.indent_segments.pop()
                #if not self.expect_close:
                #    mode = 'direct'

            opcode = self.near.read_uint8()
            #print "%04X"%(self.near.tell()-1), mode, "%x"%opcode,
            #print "%02X"%opcode, len(self.expect_close)
            if opcode == 0x81:  # oh joy a function within a function.
                subroutinefound = self.near.tell()-1
                print "Subroutine discovered at 0x%04X"%(subroutinefound)
                if subroutinefound in dd.inhibit_subs:
                    print "    Ah, it's actually a method. Nevermind."
                    self.near.seek(t)
                    return
                # We're going to assume it's always preceeded by a branch
                self.near.seek(self.near.tell()-4)
                if self.near.read_uint8() == 0x88:
                    skipaddr = self.near.read_uint16()
                    print "    Goes from 0x%04X to 0x%04X (length 0x%04X)"%(
                        subroutinefound, skipaddr, skipaddr-subroutinefound)

                    sub = DFunction(self.near,  
                                    length_hint=skipaddr-subroutinefound, bonus_indents=1)
                    sub.load(self.dd, namehint = "Subroutine")
                    self.code.append(sub)
                    self.ilevel.append(len(self.indent_segments)+1)
                    print "    Right, then, moving along."
                    self.near.seek(skipaddr)
                    continue
                else:
                    print "    Couldn't identify the ending of the subroutine." 
                    self.dd.get_label(subroutinefound, "Subroutine")
                    self.near.seek(subroutinefound+1)
            if opcode < 0x80 and mode is 'direct':
                #print "staying direct"
                if not textbuf: lastoffset = self.near.tell()-1
                textbuf.append(opcode)
            elif opcode >= 0x80 and mode is 'direct':
                #print "changing to code",
                #print "ADDR", self.near.tell()-1
                mode = 'code'
                self.code.append((''.join(map(chr,textbuf)),lastoffset))
                self.ilevel.append(len(self.indent_segments)+1)
                textbuf = []; lastoffset=-1
            if mode is 'code':
                #print "code mode"
                self.ilevel.append(len(self.indent_segments)+1)
                if opcode < 0x80 and not self.expect_close: 
                    mode = 'direct'
                    #print "Abandoning code mode", self.indent_segments
                    lastoffset = self.near.tell()-1
                    textbuf =[opcode]
                    self.ilevel.pop()
                    continue
                if opcode == 0x40:
                    self.code.append(
                        self.expect_close.pop()(opcode, self.near))
                    self.indent_segments[-1] -= 1
                    if not self.indent_segments[-1]: self.indent_segments.pop()
                    if not self.expect_close:
                        mode = 'direct'
                elif 0x00 <= opcode <= 0x2F:
                    self.code.append(OpLocal(opcode, self.near, self))
                elif 0x30 <= opcode <= 0x3F:
                    self.code.append(OpArg(opcode, self.near, self))
                elif opcode >= 0xA0:
                    self.code.append(OpSys(opcode, self.near, self))
                elif OpTable.has_key(opcode):
                    self.code.append(OpTable[opcode](opcode,self.near,self))
                else:
                    print "Bad opcode '0x%02X', offset 0x%X"%(opcode, 
                                       self.near.tell())
                    assert False, "Halting."
            if ps_after:
                self.code.insert(-1,ps_after)
                self.ilevel.insert(-1,is_after)
                ps_after = None; is_after = None
        if textbuf:
            self.code.append((''.join(map(chr,textbuf)),lastoffset))
            self.ilevel.append(1)
        self.near.seek(t)
         

def read_DVMObj(binfile, length_hint=None): 
    """Read a Delver Virtual Machine object from a binary file.
       The appropriate DVMObj subclass is returned. Note that this is
       not for atoms (True, False, integers, drefs etc.) 

       It guesses based on the first byte of the input. 81 = function.
       9x = array. Ax = table. 0x at start = class. Otherwise 
       NUL-terminated string is assumed. 
 
       Note that if you know for sure what the file is, you should
       use the appropriate DVMObj constructor."""
    t = binfile.tell()
    v = binfile.read_uint8()
    v2 = binfile.read_uint8()
    binfile.seek(t)
    if v == 0x81:
        return DFunction(binfile, length_hint)
    elif v&0xF0 == 0x90:
        return DArray(binfile)
    elif v&0xF0 == 0xA0:
        return DTable(binfile)
    elif v < 0x80 and t:
        return binfile.read_cstring()
    elif not t and (v or v2):
        return DClass(binfile)
    else:
        return DDirect(binfile, length_hint)
    #else:
    #    raise TypeError("Can't figure out what 0x%02X is. <%s>"%(v,binfile))



