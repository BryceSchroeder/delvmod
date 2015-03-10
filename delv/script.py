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
import sys, StringIO
def rstr(x):
    return '"%s"'%repr(str(x))[1:-1].replace('"','\\"')
class FauxLibrary(object):
    def __init__(self, resource):
        self.resource = resource
    def get_dref(self, mdref):
        assert mdref.resid == self.resource.resid
        return self.resource.get_dref(mdref)
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
    def str_disassemble(self, indent):
        p = StringIO.StringIO()
        self.disassemble(p, indent)
        return p.getvalue()
    def disassemble_atom(self, il, atom):
        if atom is None:
            self.p(il, "nil")
        elif isinstance(atom, int):
            self.p(il, "%d"%atom)
        elif isinstance(atom, dref):
            self.p(il, "ref %s"%self.script.get_dref_label(atom))
        elif isinstance(atom, str):
            self.p(il, rstr(atom))
        else:
            atom.disassemble(self.stream, il+1)
    def str_disassemble_atom(self, il, atom):
        if atom is None:
            return "nil"
        elif isinstance(atom, int):
            return "%d"%atom
        elif isinstance(atom, dref):
            return "ref %s"%self.script.get_dref_label(atom)
        elif isinstance(atom, str):
            return rstr(atom)
        else:
            return atom.str_disassemble(il+1)

def TypeFactory(script, src, library=None, organic_offset=None): 
        rewind = src.tell()
        cntype = src.read_uint8()
        src.seek(rewind)

        if cntype == 0x81:
            obj = Code()
        elif cntype&0xF0 == 0x90:
            obj = Array()
        else:
            return src.read_cstring()
        obj.demarshal(script, src, len(src), organic_offset=organic_offset)
        if library: obj.load_from_library(library)
        return obj



class Array(list, _PrintOuter): 
    override_dref = None
    def empty(self):
        self[:] = []
        self.references = {}
    def demarshal(self, script, src, end=None, organic_offset=0):
        self.empty()
        self.script = script
        typecode,count = src.read_fo16()
        assert typecode == 9
        for n in xrange(count):
            v = src.read_atom()
            if self.override_dref is not None and isinstance(v,dref):
                v.resid = self.override_dref
            self.append(v)
    def marshal(self, dst):
        dst.write_do16(9, len(self))
        for a in self:
            dst.write_atom(a)
    def load_from_library(self, library, only_local=False):
        if only_local: library = FauxLibrary(self.script.res)
        for n in xrange(len(self)):
            if isinstance(self[n], dref):
                if only_local and self.script.res.resid != self[n].resid:
                    continue
                self.references[n] = self[n]
                self[n] = TypeFactory(self.script,
                    library.get_dref(self[n]), library, 
                         organic_offset=self[n].offset)
    def disassemble(self, out, indent):
        self.set_stream(out)
        if len(self) < 2:
            self.pn(indent, "array [%s]"%(' '.join(map(
                 lambda (n,a):self.str_disassemble_atom(0,a),
                     enumerate(self)))))
            return
        self.pn(indent, "array [")
        for n,item in enumerate(self):
            if False: #self.references.has_key(n): 
                self.p(indent, "#{ %4d: }# "%n)
                self.disassemble_atom(indent+1,self.references[n])
                self.pn(indent+1,'')
            else:
                self.p(indent+1, "%3d: "%n)
                self.disassemble_atom(indent+1,item)
                self.pn(indent+1,'')
        self.pn(indent, "]")
    def printout(self, out, level):
        print >> out, '\t'*level, "Array"
        for n,item in enumerate(self):
            print >> out, '\t'*(level+1), "%3d:"%n, item
class CharacterNameArray(Array):
    override_dref = 0x0201

class DCOperation(_PrintOuter):
    def __init__(self, data, i=0, toff=0):
        self.data = data[i:]
        self.true_offset = toff
        self.decode()
    def decode(self):
        pass
    def disassemble(self, out, indent):
        self.set_stream(out)
        #self.dlabel(indent)
        self.pn("UNKNOWN OPERATION")
    def __len__(self): return len(self.data)
    def dlabel(self, out, indent):
        self.set_stream(out)
        lab = self.script_context.get_offset_label(self.true_offset,
            check_only=True)
        #print "**", lab, '%04X'%self.true_offset, self.get_mnemonic()
        if lab is not None:
            self.pn(indent, '%s: '%lab)
        else:
            self.pn(indent, '/* 0x%04X */'%self.true_offset)

class DCBytes(DCOperation):
    def disassemble(self, out, indent):
        self.set_stream(out)
        #self.dlabel(indent)
        self.pn(indent, "bytes [")
        howmany = (80 - indent*len(self.indent) - 5)/5
        for n,b in enumerate(self.data):
            self.p(indent+1, "0x%02X "%b)
            if not (n+1)%howmany: self.p(indent,'\n')
        self.pn(indent, "]")

class DCFixedFieldOperation(DCOperation):
    length = 1
    mnemonic = 'ERR'
    def __init__(self, data, i, toff=0):
        self.true_offset = toff
        self.data = data[i:i+self.length]
        self.decode()
    def decode(self):
        pass
    def get_mnemonic(self):
        return self.mnemonic
    def get_fields(self):
        return ''
    def disassemble(self, out, indent):
        self.set_stream(out)
        #self.dlabel(indent)
        self.pn(indent, self.get_mnemonic(), self.get_fields())

class DCVariableFieldOperation(DCFixedFieldOperation):
    terminator = '\0'
    def __init__(self, data, i,toff):
        self.true_offset = toff
        end = self.decode_length(data[i:])
        self.data = data[i:i+end]
        self.decode()
    def decode_length(self, data):
        i = data.find(self.terminator)+1
        return i if i >= 0 else len(data)

class DCConversationPrompt(DCVariableFieldOperation):
    mnemonic = 'prompt'
    def decode_length(self, data):
        i = data.find(self.terminator)
        return i + 3
    def decode(self):
        self.promptstr = self.data[
             1:self.data.find(self.terminator)].split(',')
        self.nextfield = (self.data[-2]<<8)|self.data[-1]
        self.nextlabel = self.script_context.get_offset_label(self.nextfield,
            suggestion='conv_%03X'%self.nextfield)
    def get_fields(self):
        return ', '.join(map(rstr, self.promptstr))
         
class DCAsk(DCVariableFieldOperation):
    mnemonic = 'ask'
    def decode_length(self, data):
        i = data.find(self.terminator)
        return i+1
    def get_fields(self):
        return rstr(self.data[1:self.data.find(self.terminator)])


class DOPushArg(DCFixedFieldOperation):
    mnemonic = 'push'
    def decode(self):
        self.which = self.data[0]&0x0F
        self.arg_name = self.code_context.get_arg_name(self.which)
    def get_fields(self):
        return self.arg_name

class DOPushLocal(DCFixedFieldOperation):
    mnemonic = 'push'
    length = 1
    def decode(self):
        self.which = self.data[0]
        self.label = self.code_context.get_local_name(self.which)
    def get_fields(self):
        return self.label

class DCConverse(DCFixedFieldOperation):
    mnemonic = 'converse'

class DCGoto(DCFixedFieldOperation):
    length = 3
    branch_count = 0
    mnemonic = 'goto'
    def decode(self):
        self.offset = (self.data[1]<<8)|self.data[2]
        self.label = self.script_context.get_offset_label(self.offset,
            suggestion='skip_%d'%DCGoto.branch_count)
        DCGoto.branch_count += 1
    def get_fields(self):
        return self.label

class DOPushByte(DCFixedFieldOperation):
    mnemonic = 'push'
    length = 2
    def get_fields(self):
        return '0x%02X'%self.data[1]
class DOGlobal(DCFixedFieldOperation):
    mnemonic = 'global'
    length = 2
    def decode(self):
        self.name = 'g_%02X'%self.data[1]
    def get_fields(self):
        return self.name
class DOPushShort(DCFixedFieldOperation):
    mnemonic = 'push'
    length = 3
    def get_fields(self):
        return '0x%02X%02X'%tuple(self.data[1:])
class DOPushWord(DCVariableFieldOperation):
    mnemonic = 'push'
    length = 1
    afterlength = 0
    def decode_length(self, data):
        if data[1] == 0x30: 
             self.mnemonic = 'push.3?'
             return 4
        elif data[1] == 0x01:
             self.mnemonic = 'push.2?'
             return 3
        else: return 5
    def get_fields(self):
        return '0x' + ''.join(['%02X'%x for x in self.data[1:]])
class DOPushAtom(DOPushWord):
    mnemonic = 'pushatom?'
    def decode_length(self,data):
        return 5

class DOPushString(DCVariableFieldOperation):
    mnemonic = 'push'
    def get_fields(self):
        return rstr(str(self.data[1:-1]))

class DOPushData(DCVariableFieldOperation):
    mnemonic = 'push'
    def decode_length(self, data):
        return (data[1]<<8)|data[2]+3
    def decode(self):
        s = util.BinaryHandler(StringIO.StringIO(self.data[3:]))
        self.contents = TypeFactory(self.script_context, s, 
             organic_offset=self.true_offset+3)
        if hasattr(self.contents,'load_from_library'):
            self.contents.load_from_library(
                self.script_context.library,only_local=True)
    def disassemble(self,out,indent):
        self.set_stream(out)
        #self.dlabel(indent)
        self.pn(indent, '%s ['%self.mnemonic)
        if hasattr(self.contents,'disassemble'):
            self.contents.disassemble(out, indent+1)
        else:
            self.pn(indent+1, self.str_disassemble_atom(indent+1,
                self.contents))
        self.pn(indent, ']')

class DCExpressionContainer(DCVariableFieldOperation):
    groups = 1
    length = 1
    afterlength = 0
    mnemonic = 'ERR_EXPR'
    def __init__(self, data, i, toff):
        self.true_offset = toff
        self.items = [[] for g in xrange(self.groups)]
        self.flat_items = []
        inside = self.groups
        group = 0
        original_i = i
        i += self.length
        while inside:
            op,i = DCOperationFactory(data, i, self.code_context,
                        self.script_context, mode = 'expression',
                        organic_offset = 0)
            if op:
                self.items[group].append(op)
                self.flat_items.append(op)
            else:
                inside -= 1
                group += 1
        self.data = data[original_i:i+self.get_afterlength(data[i:])]
        self.decode()
    def get_afterlength(self, data):
        return self.afterlength
    def decode(self): pass
    def disassemble(self, out, indent): 
        self.set_stream(out)
        #self.dlabel(indent)
        self.p(indent, self.get_mnemonic())
        for group in self.items:
            self.pn(indent, '(')
            for item in group:
                 item.disassemble(out, indent+1)
            self.pn(indent, ')')
        
class DC9D(DCExpressionContainer):
    mnemonic = 'op9D_%02X'
    length = 2
    def decode(self):
        self.which = self.data[1]
    def get_mnemonic(self):
        return self.mnemonic%self.which
class DC9B(DC9D):
    mnemonic='op9B_%02X'

class DCStringConstant(DCVariableFieldOperation):
    mnemonic = ''
    def decode_length(self,data):
        i = 0
        while i < len(data):
            if data[i] >= 0x80: break
            i += 1
        return i
    def disassemble(self,out,indent):
        self.set_stream(out)
        #self.dlabel(indent)
        self.pn(indent,rstr(str(self.data)))

class DOSeriesA(DCExpressionContainer):
    mnemonic = 'sysa_%1X'
    groups = 1
    def decode(self):
        self.which = self.data[0]&0x0F
    def get_mnemonic(self):
        return self.mnemonic%self.which
    
class DOOperator(DCFixedFieldOperation):
    mnemonics = {
        0x46: 'index',
        0x4A: 'add',   0x4C: 'mul',   0x4B: 'sub',  0x4D: 'div', 
        0x4E: 'arithmetic?', 0x4F: 'mod_candidate?', 0x50: 'op_50?',
        0x51: 'gt', 0x52: 'le?', 0x54: 'neq', #0x57: 'op57',
        0x53: 'lt?',
        0x5A: 'shl', 0x5B: 'bitwise?', 0x5E: 'not?', 0x5D: 'bitwise_not?',
        0x5C: 'shr?', 0x5F: 'bitand?'
    }
    def decode(self):
        self.mnemonic = self.mnemonics.get(self.data[0],
            "op%02X"%self.data[0])

class DOField(DCFixedFieldOperation):
    length = 2
    mnemonic = 'field'
    def get_fields(self):
        return '.attr_%02X'%self.data[1]
class DOCast(DCFixedFieldOperation):
    length = 2
    mnemonic = 'cast'
    def get_fields(self):
        return '_%02X'%self.data[1]
class DONField(DOCast):
    menmonic = 'field64?'
class DON60(DOCast):
    menmonic = 'field60?'
class DON61(DOCast):
    mnemonic = 'unknown61?'
    length = 3
    def get_fields(self):
        return '_%02X%02X'%tuple(self.data[1:])

class DO92(DCExpressionContainer):
    mnemonic = 'unkn92'
    length=2
    groups=1
    def get_mnemonic(self):
        return '%s_%02X'%(self.mnemonic,self.data[1])

class DCLocalAssignment(DCExpressionContainer):
    groups = 1
    mnemonic = 'set'
    length = 2
    def decode(self):
        self.which = self.data[1]
        #print 'XXXXXX %02X/%02X/%02X/%02X'%tuple(self.data[0:4])
        self.local_name = self.code_context.get_local_name(self.which)
    def get_mnemonic(self):
        return '%s %s'%(self.mnemonic,self.local_name)
class DCAttrAssignment(DCExpressionContainer):
    groups = 2
    mnemonic = 'set'
    length = 2
    def decode(self):
        self.which = self.data[1]
        self.field_name = '.attr_%02X'%self.which
    def get_mnemonic(self):
        return '%s%s '%(self.mnemonic,self.field_name)

class DCReturn(DCExpressionContainer):
    groups = 1
    mnemonic = 'return'
    length = 1
class DCPrint(DCExpressionContainer):
    mnemonic = 'print'

class DCUnknown7(DC9D):
    mnemonic = 'unkn7_%02X'
    length = 2
    groups = 1
class DCUnknown5(DC9D):
    mnemonic = 'unkn5_%08X'
    length = 5
    groups = 1
    def decode(self):
        self.value = (self.data[1]<<24)|(self.data[2]<<16)|(
            self.data[3]<<8)|self.data[4]
    def get_mnemonic(self):
        return self.mnemonic%self.value

class DCIfStatement(DCExpressionContainer):
    mnemonic = 'if'
    branch_count = 0
    groups = 1
    afterlength = 2
    def decode(self):
        self.offset = (self.data[-2]<<8)|self.data[-1] 
        self.label = self.script_context.get_offset_label(self.offset,
            suggestion='branch_%d'%DCIfStatement.branch_count)
        DCIfStatement.branch_count += 1
    def get_mnemonic(self):
        return 'goto %s %s '%(self.label,self.mnemonic)
class DCEEStatement(DCFixedFieldOperation):
    mnemonic = 'unknEE'
    length = 1

class DCF5(DCFixedFieldOperation):
    mnemonic = 'unknF5'
    length = 1

class DCCE(DCFixedFieldOperation):
    mnemonic = 'unknCE'
    length = 1

class DCWhileStatement(DCIfStatement):
    mnemonic = 'ifnot?'


class DCCallRes(DCExpressionContainer):
    mnemonic = 'call'
    length = 3
    def decode(self):
        self.resid = (self.data[1]<<8)|self.data[2] 
    def get_mnemonic(self):
        return '%s res 0x%04X'%(self.mnemonic,self.resid)
class DCCallArray(DCExpressionContainer):
    mnemonic = 'dispatch'
    length = 3
    groups = 2
    def decode(self):
        self.base_resid = (self.data[1]<<8)|self.data[2] 
    def get_mnemonic(self):
        return '%s res 0x%04X'%(self.mnemonic,self.base_resid)

class DC9E(DCCallArray):
    mnemonic = 'endgame?'
    length = 3
    groups = 1
    def get_mnemonic(self):
        return '%s 0x%02X%02X'%((self.mnemonic,)+tuple(self.data[1:3]))
 

class DCSignal(DCExpressionContainer):
    mnemonic = 'signal'
    def decode(self):
        self.argc = self.data[0]&0x0F
    def get_mnemonic(self):
        return self.mnemonic+'_%01X'%self.argc
class DCSeriesE(DCSignal):
    mnemonic = 'syse'
class DCSeriesA(DCExpressionContainer):
    mnemonic = 'sysa'
class DCSeriesB(DCExpressionContainer):
    mnemonic = 'sysb'
class DCSeriesD(DCSignal):
    mnemonic = 'sysd'
class DCSeriesF(DCSignal):
    mnemonic = 'sysf'

def DCOperationFactory(data, i, code, script, mode = 'toplevel',
    organic_offset=0):
    if i == len(data): return None,i
    DCOperation.code_context = code
    DCOperation.script_context = script
    opc = data[i]
    if mode is 'toplevel':
        if opc < 0x80:
            op = DCStringConstant
        elif opc == 0x82:
            op = DCLocalAssignment
        elif opc == 0x85:
            op = DCUnknown5
        elif opc == 0x86:
            op = DCAttrAssignment
        elif opc == 0x87:
            op = DCUnknown7
        elif opc == 0x88:
            op = DCGoto
        elif opc == 0x8A:
            op = DCPrint
        elif opc == 0x8B:
            op = DCReturn
        elif opc == 0x8C:
            op = DCWhileStatement
        elif opc == 0x8D:
            op = DCIfStatement
        elif opc == 0x8E:
            op = DCConverse
        elif opc == 0x8F:
            op = DCAsk
        elif opc == 0x90:
            op = DCConversationPrompt  
        elif opc == 0x92:
            op = DO92  
        elif opc == 0x9C:
            op = DCCallArray
        elif opc == 0x9D:
            op = DC9D
        elif opc == 0x9B:
            op = DC9B
        elif opc == 0x9E:
            op = DC9E
        elif opc == 0x9F:
            op = DCCallRes
        elif opc&0xF0 == 0xA0:
            op = DCSeriesA
        elif opc&0xF0 == 0xB0:
            op = DCSeriesB

        elif opc == 0xCE:
            op = DCCE
        elif opc&0xF0 == 0xC0:
            op = DCSignal        

        elif opc&0xF0 == 0xD0:
            op = DCSeriesD
        elif opc&0xF0 == 0xE0:
            op = DCSeriesE
        
        elif opc == 0xF5:
            op = DCF5
        elif opc&0xF0 == 0xF0:
            op = DCSeriesF
        else:
            op = DCBytes
        op = op(data,i,organic_offset+i)
        i += len(op)
        return op, i
    elif mode is 'expression':
        if opc &0xF0 == 0x30:
            op = DOPushArg
        elif opc < 0x30:
            op = DOPushLocal
        elif opc == 0x41:
            op = DOPushByte
        elif opc == 0x42:
            op = DOPushShort
        elif opc == 0x43:
            op = DOPushWord
        elif opc == 0x44:
            op = DOPushString
        elif opc == 0x45:
            op = DOPushData
        elif opc == 0x46:
            op = DOOperator
        elif opc == 0x48:
            op = DOGlobal
        elif opc == 0x49:
            op = DOPushAtom
        elif opc&0xF0 == 0xA0:
            op = DOSeriesA
        elif opc >= 0x4A and opc <= 0x4F:
            op = DOOperator
        elif opc in [0x50,
                0x51,0x52,0x53,0x54,0x56,0x57,0x5E,0x5D,0x5B,0x5C,0x5F]:
            op = DOOperator
        elif opc == 0x5A:
            op = DOOperator
        elif opc == 0x60:
            op = DON60
        elif opc == 0x61:
            op = DON61
        elif opc == 0x62:
            op = DOField
        elif opc == 0x64:
            op = DONField
        elif opc == 0x63:
            op = DOCast    
        elif opc == 0x9B:
            op = DC9B
        elif opc == 0x9D:
            op = DC9D
        elif opc == 0x9F:
            op = DCCallRes
        elif opc&0xF0 == 0xB0:
            op = DCSeriesB
        elif opc&0xF0 == 0xC0:
            op = DCSignal
        elif opc == 0xEE:
            op = DCEEStatement
        elif opc&0xF0 == 0xD0:
            op = DCSeriesD
        elif opc&0xF0 == 0xF0:
            op = DCSeriesF
        elif opc == 0x40:
            op = None
            i += 1
        else:
            op = DCBytes
        
        if op:
            op = op(data,i,organic_offset+i) 
            i += len(op)
        return op,i
class Code(list, _PrintOuter):
    def empty(self):
        self[:] = []
    def get_local_name(self, n):
        if len(self.local_names) <= n:
            return '<LOCAL NAME 0x%02X>'%n
        return self.local_names[n]
    def get_arg_name(self,n):
        return self.arg_names[n]
    def demarshal(self, script, src, end=None,organic_offset=0):
        self.empty()
        self.script = script
        typecode = src.read_uint8()
        assert typecode == 0x81
        self.argc = src.read_uint8()
        self.localc = src.read_uint8()
        self.local_names = ["var_%d"%x for x in xrange(self.localc)]
        self.arg_names = ["arg_%d"%x for x in xrange(self.argc)]
        data = src.readb()
        i = 0
        while i < len(data):
            op,i = DCOperationFactory(data,i,self,script,
                 organic_offset=organic_offset+3)
            self.append(op)
        #self[:] = [DCBytes(src.readb())]
    def disassemble(self, out, indent):
        self.set_stream(out)
        self.p(indent, "function (%s) "%(' '.join(self.arg_names)))
        if self.localc: self.pn(indent+1, 
                'with (%s) {'%(' '.join(self.local_names)))
        else: self.pn(indent, "{")
        for op in self:
            op.dlabel(out,indent+1)
            op.disassemble(out, indent+1)
        self.pn(indent, "}")
    def __str__(self):
        return "<Code argc=%d localc=%d length=%d>"%(
            self.argc,self.localc,len(self))
    def load_from_library(self, library, only_local=False):
        pass
    def printout(self, out, level=0):
        print >> out, '\t'*level, str(self)
        self.disassemble(out, level+1)
       
class DispatchTable(dict, _PrintOuter):
    def empty(self):
        self.references = {}
        self.item_labels = {}
        self.clear()
    def demarshal(self, script, src, end,organic_offset=0):
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
    def load_from_library(self, library,only_local=False):
        for n in self:
            if isinstance(self[n], dref):
                if only_local and self.script.res.resid != dref.resid:
                    continue
                self.references[n] = self[n]
                self[n] = TypeFactory(self.script,
                    library.get_dref(self[n]), library, 
                         organic_offset=self[n].offset)
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
    def __init__(self, script, src=None, end=None, organic_offset=0):
        self.dispatch = None 
        self.script = script
        if src: self.demarshal(self.script, src, end,
             organic_offset=organic_offset)
    def demarshal(self, script, src, end=None, organic_offset = 0):
        self.script = script
        src.seek(0)
        dtoffset = src.read_uint16()
        src.seek(dtoffset)
        self.dtindex = DispatchTable()
        self.dtindex.demarshal(self.script, src, dtoffset,
             organic_offset=dtoffset)
    def load_from_library(self, library,only_local=False):
        self.dtindex.load_from_library(library)
        self.dispatch = self.dtindex
    def disassemble(self, out, indent):
        self.set_stream(out)
        self.pn(indent, "class {")
        for label, item in self.dtindex.item_labels.items():
            self.pn(indent+1, "%s:"%label)
            item.disassemble(out, indent+2)
        self.dtindex.disassemble(out, indent+1)
        self.pn(indent, "}")
 
class Script(store.Store):
    class_container = False
    library = None
    character_names = False
    def __init__(self, src):
        store.Store.__init__(self, src)
        self.symbol_table = {}
        self.unique_symbol = 0
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.obj = None
    def set_library(self, library):
        self.library = library
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.write(self.cobj.get_data())
    def get_dref_label(self, ref, suggestion=None, check_only=False):
        if ref in self.symbol_table:
            return self.symbol_table[ref]
        if ref.resid == self.res.resid and ref.offset in self.symbol_table:
            return self.symbol_table[ref.offset]
        if check_only: return None
        if suggestion is None: 
            suggestion = "label_%d"%self.unique_symbol
            self.unique_symbol += 1
        self.symbol_table[ref] = suggestion
        self.symbol_table[ref.offset] = suggestion
        return suggestion
    def get_offset_label(self, offset, suggestion=None,check_only=False):
        return self.get_dref_label(dref(self.res.resid, offset),
            suggestion,check_only=check_only)
        
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
                self.obj.demarshal(self, self.src, organic_offset = 0)
            elif cntype&0xF0 == 0x90:
                self.obj = (
                    CharacterNameArray if self.character_names else Array)()
                self.obj.demarshal(self, self.src, organic_offset = 0)
            elif cntype&0xF0 == 0xA0:
                self.obj = DispatchTable()
                self.obj.demarshal(self, self.src,len(self.src),
                    organic_offset = 0)
            else:
                self.obj = self.src.read_atom()
    def load_from_library(self, library,only_local=False):
        self.set_library(library)
        if hasattr(self.obj, 'load_from_library'):
            self.obj.load_from_library(library,only_local)
    def printout(self, out, level=0):
        if not hasattr(self.obj, 'disassemble'):
            print >> out, "Atom:", self.obj
            return
        print >> out, "-- Script Object from %s --"%repr(self.src)
        self.obj.disassemble(out, 1)
    def disassemble(self, target=None):
        if target is None: 
             out = StringIO.StringIO()
        else:
             out = target
        if not hasattr(self.obj, 'disassemble'):
            print >> out, self.str_disassemble_atom(self.obj)
        else:
            self.obj.disassemble(out, 0)

        if target is None: return out.getvalue()
        return "<ERROR>"
    def str_disassemble_atom(self, atom):
        if atom is None:
            return "nil"
        elif isinstance(atom, int):
            return "%d"%atom
        elif isinstance(atom, dref):
            return "ref %s"%self.get_dref_label(atom)
        elif isinstance(atom, str):
            return rstr(atom)
        else:
            return "<BAD ATOM>"

        
        
        
        
class ClassContainer(Script):
    class_container = True

class CharacterNames(Script):
    character_names = True
