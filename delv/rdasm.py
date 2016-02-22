#!/usr/bin/env python
# Copyright 2014-2016 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
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

# Documentation of the assembly language can be found at:
# http://www.ferazelhosting.net/wiki/RDASM
All_Operations = {}
Statement_Operations = {}
RDASM_opcode_names = []
# TODO 1. distinguish between statement-opcodes and expression-opcodes
# 2. Add data-defining toplevel for classes. array Foo(1,2)?
# 3. function code generation
#    including local variables and labels...
# 4. classes
# 5. disassembler
# 6. provisions for regression testing
# 7. enter all this stuff into github and pip
# 8. redelv to use it, and upload that

OpClasses = {}
StatementClasses = {}
MnemonicDecoder = {}
def opcode(mnemonic, statement=False):
    def real_decorator(f):
        MnemonicDecoder[mnemonic] = f.__
        OpClasses[f.__name__.replace('Op_','')] = f.__doc__
        OpClasses[mnemonic] = f.__doc__
        if statement:
            StatementClasses[f.__name__.replace('Op_','')] = f.__doc__
            StatementClasses[f.mnemonic] = f.__doc__
        return f
    return real_decorator
STR_SYM = '(terminated_string|symbol):%s'
INT_SYM = '(integer|symbol):%s'
ATO_SYM = '(atom|symbol):%s'
EXPR_CODE = "'(' ws expression_item*:%s ws ')'"
STAT_CODE = "'(' ws function_item*:%s ws ')'"
import inspect # forgive me, I just need to get this done
class Opcode(object):
    def __init__(self, ctx, **kwargs):
        self.ctx = ctx
        self.kwargs = kwargs
    def generate(self, of, ctx):
        of.write_uint8(self.encoding)
    def rule(self, name, rhs=''):
        base = "operation_%s = '%s'"%(name,name)
        if rhs:
            base += ' space '+rhs
        else:
            base += self.match()
        return base + ' -> %s(asm, %s)'%(self.true_name, self.parameterization())
    def match(self):
        argname, _, _, argclass = inspect.getargspec(self.generate)
        if not argclass: return ''
        p = ' space '.join([rule%binding for binding,rule in zip(argname[-len(argclass):],argclass)])
        return (' space ' if argclass[0].strip()[0] == "'" else ' required_space ')+p if p else p

    def parameterization(self):
        argname, _, _, argclass = inspect.getargspec(self.generate)
        if not argclass: return ''
        p = ', '.join(['%s=%s'%(binding,binding) for binding,rule in zip(
                             argname[-len(argclass):],argclass)])
        return p
    def finish(self, of, ctx, value):
        of.write_uint16(value)

############################ OPCODE DEFINITIONS ###########################
class Op_local(Opcode):
    mnemonic = 'loc'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(ctx.getfval(which))

class Op_argument(Opcode):
    mnemonic = 'arg'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(ctx.getfval(which)|0x30)

class Op_end_expression(Opcode):
    mnemonic = 'end'
    encoding = 0x40

class Op_then_go_to(Opcode):
    mnemonic = 'then'
    def generate(self, of, ctx, label=INT_SYM):
        of.write_uint8(0x40)
        of.write_uint16(ctx.getlval(label, self, of.tell()))

class Op_load_byte(Opcode):
    mnemonic = 'byte'
    def generate(self, of, ctx, immediate=INT_SYM):
        of.write_uint8(0x41)
        of.write_uint8(ctx.getlval(immediate, self, of.tell()))
    def finish(self, of, ctx, value):
        of.write_uint8(value)

class Op_load_short(Opcode):
    mnemonic = 'short'
    def generate(self, of, ctx, immediate=INT_SYM):
        of.write_uint8(0x42)
        of.write_uint16(ctx.getlval(immediate, self, of.tell()))

class Op_load_word(Opcode):
    mnemonic = 'word'
    def generate(self, of, ctx, immediate='(atom|symbol):%s'):
        of.write_uint8(0x43)
        of.write_uint32(ctx.getlval(immediate, self, of.tell()))
    def finish(self, of, ctx, value):
        of.write_uint32(value)

class Op_load_cstring(Opcode):
    mnemonic = 'string'
    def generate(self, of, ctx, immediate=STR_SYM):
        of.write_uint8(0x44)
        of.write(ctx.getval(immediate))

class Op_load_data(Opcode):
    mnemonic = 'data'
    def generate(self, of, ctx, dval='(table|array):%s'):
        of.write_uint8(0x45)
        lenadr = of.tell()
        of.write_uint16(0xDEAD)
        startaddr = of.tell()
        v = ctx.getval(dval)
        if isinstance(v, dict):
            dict_write_code(v, of, ctx)
        else:
            v.write_code(of, ctx)
        endaddr = of.tell()
        of.seek(lenadr)
        of.write_uint16(endaddr-startaddr)
        of.seek(endaddr)

class Op_index(Opcode):
    mnemonic = 'idx'
    encoding = 0x46

class Op_load_near_word(Opcode):
    mnemonic = 'near'
    def generate(self, of, ctx, lbl=INT_SYM):
        of.write_uint8(0x47)
        of.write_uint16(ctx.getlval(lbl, self, of.tell()))
    
class Op_global(Opcode):
    mnemonic = 'glo'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(0x48)
        of.write_uint8(ctx.getval(which))

class Op_load_far_word(Opcode):
    mnemonic = 'far'
    def generate(self, of, ctx, resid=INT_SYM, offset=INT_SYM):
        of.write_uint8(0x49)
        of.write_uint16(ctx.getval(resid))
        of.write_uint16(ctx.getval(offset))

class Op_add(Opcode):
    mnemonic = 'add'
    encoding = 0x4A

class Op_subtract(Opcode):
    mnemonic = 'sub'
    encoding = 0x4B

class Op_multiply(Opcode):
    mnemonic = 'mul'
    encoding = 0x4C

class Op_divide(Opcode):
    mnemonic = 'div'
    encoding = 0x4D

class Op_modulus(Opcode):
    mnemonic = 'mod'
    encoding = 0x4E

class Op_less_than(Opcode):
    mnemonic = 'lt'
    encoding = 0x4F

class Op_less_than_or_equal(Opcode):
    mnemonic = 'le'
    encoding = 0x50

class Op_greater_than(Opcode):
    mnemonic = 'gt'
    encoding = 0x51 

class Op_greater_than_or_equal(Opcode):
    mnemonic = 'ge'
    encoding = 0x52

class Op_not_equal(Opcode):
    mnemonic = 'ne'
    encoding = 0x53

class Op_equal(Opcode):
    mnemonic = 'eq'
    encoding = 0x54

class Op_negative(Opcode):
    mnemonic = 'not'
    encoding = 0x55

class Op_bitwise_and(Opcode):
    mnemonic = 'andb'
    encoding = 0x56

class Op_bitwise_or(Opcode):
    mnemonic = 'orb'
    encoding = 0x57

class Op_bitwise_xor(Opcode):
    mnemonic = 'xor'
    encoding = 0x58

class Op_bitwise_not(Opcode):
    mnemonic = 'notb'
    encoding = 0x59

class Op_left_shift(Opcode):
    mnemonic = 'lsh'
    encoding = 0x5A

class Op_right_shift(Opcode):
    mnemonic = 'rsh'
    encoding = 0x5B  

class Op_logical_and(Opcode):
    mnemonic = 'and'
    encoding = 0x5C

class Op_logical_or(Opcode):
    mnemonic = 'or'
    encoding = 0x5D

class Op_logical_not(Opcode):
    mnemonic = 'not'
    encoding = 0x5E

class Op_get_length(Opcode):
    mnemonic = 'len'
    encoding = 0x5F

class Op_has_field(Opcode):
    mnemonic = 'has'
    def generate(self, of, ctx, field=INT_SYM):
        of.write_uint8(0x60)
        of.write_uint8(ctx.getval(field))

class Op_class_variable(Opcode):
    mnemonic = 'cvar'
    def generate(self, of, ctx, classfield=INT_SYM, tidx=INT_SYM):
        of.write_uint8(0x61)
        of.write_uint8(ctx.getval(classfield))
        of.write_uint8(ctx.getval(tidx))

class Op_get_field(Opcode):
    mnemonic = 'field'
    def generate(self, of, ctx, field=INT_SYM):
        of.write_uint8(0x62)
        of.write_uint8(ctx.getval(field))


class Op_cast_to(Opcode):
    mnemonic = 'cast'
    def generate(self, of, ctx, field=INT_SYM):
        of.write_uint8(0x63)
        of.write_uint8(ctx.getval(field))

class Op_is_type(Opcode):
    mnemonic = 'type'
    def generate(self, of, ctx, field=INT_SYM):
        of.write_uint8(0x64)
        of.write_uint8(ctx.getval(field))

class Op_set_local(Opcode):
    mnemonic = 'setl'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(0x82)
        of.write_uint8(ctx.getfval(which, warn_new=False))

class Op_write_near_word(Opcode):
    mnemonic = 'wnw'
    def generate(self,of,ctx, addr=INT_SYM):
        of.write_uint8(0x83)
        of.write_uint16(ctx.getlval(addr, self, of.tell()))

class Op_set_index(Opcode):
    mnemonic = 'seti'
    encoding = 0x84

class Op_write_far_word(Opcode):
    mnemonic = 'wfw'
    def generate(self,of,ctx, resid=INT_SYM, offset=INT_SYM):
        of.write_uint8(0x85)
        of.write_uint16(ctx.getval(resid))
        of.write_uint16(ctx.getlval(addr, self, of.tell()))

class Op_set_field(Opcode):
    mnemonic = 'setf'
    def generate(self,of,ctx, whichfield=INT_SYM):
        of.write_uint8(0x86)
        of.write_uint8(ctx.getval(whichfield))

class Op_set_global(Opcode):
    mnemonic = 'setg'
    def generate(self,of,ctx, whichglobal=INT_SYM):
        of.write_uint8(0x87)
        of.write_uint8(ctx.getval(whichglobal))

class Op_unconditional_branch(Opcode):
    mnemonic = 'branch'
    def generate(self,of,ctx, lbl=INT_SYM):
        of.write_uint8(0x88)
        of.write_uint16(ctx.getlval(lbl, self, of.tell()))

class Op_switch(Opcode):
    mnemonic = 'switch'
    encoding = 0x89

class Op_cases(Opcode):
    mnemonic = 'cases'
    def generate(self,of,ctx, lbls="'(' ws symlistitem*:%s ws ')' "):
         of.write_uint8(0x40)
         of.write_uint16(len(lbls))
         for lbl in lbls:
              of.write_uint16(ctx.getlval(lbl,self,of.tell()))
        

class Op_print(Opcode):
    mnemonic = 'print'
    encoding = 0x8A

class Op_return(Opcode):
    mnemonic = 'ret'
    encoding = 0x8B

class Op_branch_if(Opcode):
    mnemonic = 'if'
    encoding = 0x8C

class Op_branch_if_not(Opcode):
    mnemonic = 'if_not'
    encoding = 0x8D

class Op_exit_conversation(Opcode):
    mnemonic = 'exit'
    encoding = 0x8E

class Op_conversation_prompt(Opcode):
    mnemonic = 'prompt'
    encoding = 0x8F
    def generate(self, of,ctx,prompt=STR_SYM):
        of.write_uint8(0x8F)
        of.write(ctx.getval(prompt))

class Op_conversation_response(Opcode):
    mnemonic = 'response'
    def generate(self,of,ctx, prompt=STR_SYM):
        of.write_uint8(0x90)
        of.write(ctx.getval(prompt))
        ctx.register_conversation_prompt(of.tell())
        of.write_uint16(0xDEAD)

class Op_end_response(Opcode):
    mnemonic = 'endr'
    def generate(self, of,ctx):
        p=ctx.finish_conversation_prompt(of.tell(x))
        endpoint = of.tell()
        of.seek(p)
        of.write_uint16(endpoint)
        of.seek(endpoint)

class Op_gui_close(Opcode):
    mnemonic = 'gclose'
    encoding = 0x93

class Op_gui_call(Opcode):
    mnemonic = 'gui'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(0x9B)
        of.write_uint8(ctx.getval(which))

class Op_call_method(Opcode):
    mnemonic = 'method'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(0x9D)
        of.write_uint8(ctx.getval(which))

class Op_call_subroutine(Opcode):
    mnemonic = 'csub'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(0x9E)
        of.write_uint16(ctx.getlval(which, self, of.tell()))

class Op_call_resource(Opcode):
    mnemonic = 'cres'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(0x9F)
        of.write_uint16(ctx.getval(which))

#class Op_delete(Opcode):
#    mnemonic = 'del'
#    encoding = 0xA7

class Op_system_call(Opcode):
    mnemonic = 'sys'
    def generate(self, of, ctx, which=INT_SYM):
        of.write_uint8(ctx.getval(which))


      
###################### END OPCODES #####################################

# I hope python purgatory isn't too bad
item = None
for item in globals():
    if item.startswith("Op_"):
        OpClasses[globals()[item].mnemonic] = globals()[item]
        OpClasses[item.replace('Op_','')] = globals()[item]
        globals()[item].true_name = item

#def opcode(mnemonic, funclevel=True):
#    def real_decorator(f):
#        RDASM_opcode_names.append('opcode_'+f.__name__)
#        RDASM_opcode_names.append('opcode_'+mnemonic)
#        All_Operations[f.__name__] = f
#        All_Operations[mnemonic] = f
#        return f
#    return real_decorator

def dict_write_code(table, ofile, context):
    ofile.write_uint16(0xA000|len(table))
    callbacks = []
    for k,v in table.items():
        k = context.getval(k)
        write_array_item(ofile, v, context,callbacks)
        ofile.write_uint16(k)
    addrs = []
    for address, item in callbacks:
        addrs.append((address,ofile.tell()))
        if isinstance(item,str) or isinstance(item,bytearray):
            ofile.write(item)
        else:
            item.write_code(ofile,context)
    t = ofile.tell()
    for address,ptr in addrs:
        ofile.seek(address)
        ofile.write_uint16(ptr)
    ofile.seek(t)  


def write_array_item(ofile, item, context, callbacks):
    item = context.getval(item)
    if item is None:
         ofile.write_uint32(0x5000FFFF)
    elif item is Empty:
         ofile.write_uint32(0x5000FFFE)
    elif item is True:
         ofile.write_uint32(0x50000001)
    elif item is False:
         ofile.write_uint32(0x50000000)
    elif isinstance(item,int):
         ofile.write_uint32(item)
    elif isinstance(item,str) or isinstance(item,bytearray) or isinstance(item,Array):
         ofile.write_uint16(context.context_resource|0x8000)
         callbacks.append((ofile.tell(), item))
         ofile.write_uint16(0xDEAD)
    elif isinstance(item,dict):
         ofile.write_uint16(context.context_resource|0x8000)
         callbacks.append((ofile.tell(), item))
         ofile.write_uint16(0xDEAD)
    else:
         #print "***", item
         item.write_code(ofile,context)


def direct_hex_to_bytearray(text):
    f = []
    for i in xrange(0,len(text),2):
        f.append(int(text[i:i+1],16))
    #print f
    return bytearray(f)

class SymbolList(list): 
    def __hash__(self):
        return hash('.'.join(self))

class TLL(object):
    def __init__(self, sym):
        self.sym = sym
    def write_code(self, ofile, context):
        context.define_symbol(self.sym, ofile.tell())

class Array(list):
    def with_label(self, label=None):
        if label is not None:
            self.label= label
        return self
    def write_code(self,ofile,context):
        if hasattr(self, 'label'):
            context.define_symbol(self.label, ofile.tell())
        ofile.write_uint16(0x9000|len(self))
        callbacks = []
        for item in self:
            write_array_item(ofile,item,context,callbacks)

        addrs = []
        for address, item in callbacks:
            addrs.append((address,ofile.tell()))
            if isinstance(item,str) or isinstance(item,bytearray):
                ofile.write(item)
            else:
                item.write_code(ofile,context)
        t = ofile.tell()
        for address,ptr in addrs:
            ofile.seek(address)
            ofile.write_uint16(ptr)
        ofile.seek(t)  

class Label(SymbolList): pass
class ResRef(tuple):
    def write_code(self,ofile,context):
        ofile.write_uint16(0x8000|context.getval(self[0]))
        ofile.write_uint16(context.getval(self[1]))
class ArrayRef(tuple):
    def write_code(self,ofile,context):
        ofile.write_uint16(0x3000|context.getval(self[1]))
        ofile.write_uint16(context.getval(self[0]))
class ObjRef(tuple): 
    def write_code(self,ofile,context):
        ofile.write_uint8(0x40)
        ofile.write_uint8(context.getval(self[0]))
        ofile.write_uint16(context.getval(self[1]))
class Empty(object):
    def write_code(self,ofile,context=None):
        ofile.write_uint32(0x5000FFFE)

class Function(object): 
    def __init__(self,label=None, args=None, body=None):
        self.label = label
        self.args = args
        self.body = body
        self.local_vars = 0
    def write_code(self,ofile,context):
        if self.label: context.define_symbol(self.label, ofile.tell())

        ofile.write_uint8(0x81)
        ofile.write_uint8(len(self.args))

        locals_addr = ofile.tell()
        ofile.write_uint8(0xDE)

        callbacks = context.begin_function_context(self)
        for item in self.body:
            item.write_code(ofile,context)


        new_callbacks = []
        for obj, label, position in callbacks:
            t = ofile.tell()
            ofile.seek(position)
            labval = context.getfval(label,None)
            if not labval is None:
                obj.finish(ofile, context, labval)
            ofile.seek(t)
            if labval is None:
                #print "Long-callback", obj,label,position
                new_callbacks.append((obj,label,position))

        context.end_function_context()

        t = ofile.tell()
        ofile.seek(locals_addr)
        ofile.write_uint8(self.local_vars)
        ofile.seek(t)

        return new_callbacks


class FItem(object):
    def __init__(self, lb, op):
        #print "FBODYITEM", lb, op
        self.label = lb
        self.op = op
    def write_code(self, of, ctx):
        if self.label: ctx.define_local_label(self.label, of.tell())
        if isinstance(self.op, bytearray):
            of.write(self.op)
        elif self.op:
            self.op.generate(of, ctx, **self.op.kwargs)
def get_op(sym):
    return "OP%s"%sym

RDASM_opcode_names = []
RDASM_opcode_rules = []
for k,v in OpClasses.items():
    RDASM_opcode_names.append('operation_'+k)
    RDASM_opcode_rules.append(v(None).rule(k))
RDASM_opcode_rules.sort(reverse=True)
RDASM_opcode_names.sort(reverse=True)
RDASM_Opcodes = ""
RDASM_Opcodes += '\n'.join(RDASM_opcode_rules)
RDASM_Opcodes += "\noperation = " + ' | '.join(RDASM_opcode_names) + '\n'

#RDAll = []
#for name, op in All_Operations.items():
#    RDAll.append("opcode_%s = '%s' %s"%(name, name, ' ws '+op.__doc__ if op.__doc__ else ''))
#RDASM_Opcodes += '\n'.join(RDAll)
#print RDASM_Opcodes

RDASM_Grammar_Preamble = r"""
comment =  (('/*' (~'*/' anything)* '*/')|((';'|'//') (~'\n' anything)* '\n')) -> None
ws = (comment|'\t'|' '|'\n'|'\r')* -> None
space = (comment|'\t'|' ')* -> None
integer = bin_int|hex_int|dec_int
required_space = (comment|'\t'|' ')+ -> None
bin_int = '0b' <bin_digit+>:x -> int(x,2)
hex_int = '0x' <hex_digit+>:x -> int(x,16)
dec_int = <sign? dec_digit+>:x -> int(x)

bin_digit = anything:x ?(x in "01") -> x
dec_digit = anything:x ?(x in "0123456789") -> x
hex_digit = anything:x ?(x in "0123456789abdefABCDEF") -> x
sign = anything:x ?(x in "-+") -> x



escaped  = '\\' (
                ('n' -> '\n')
                |('t' -> '\t')
                |('r' -> '\r')
                |('f' -> '\f')
                |('b' -> '\b')
                |('\\' -> '\\')
                |('"' -> '"')
                |('\'' -> '\'')
                |escaped_hex
                )
escaped_hex = 'x' <hex_digit{2}>:hs -> chr(int(hs,16))

#
terminated_string = '"' (escaped| ~'"' anything)*:x '"' -> bytearray(''.join(x)+'\0')
direct_string = '\'' (escaped| ~'\'' anything)*:x  '\'' -> bytearray(''.join(x))
hex_pair = <hex_digit hex_digit>:x (ws|'.')? -> int(x,16)
direct_hex = '{' ws hex_pair*:x ws '}' -> bytearray(x)
#
symbol_ch0 = anything:x ?(x in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_') -> x
symbol_chn = anything:x ?(x in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-0123456789') -> x
chain_symbol_item = ws simple_symbol:x ws '.' ws ->x
chain_symbol = chain_symbol_item+:x simple_symbol:y -> SymbolList([z[0] for z in x]+y)
simple_symbol = <symbol_ch0 symbol_chn*>:x -> SymbolList([x])
symbol = chain_symbol | simple_symbol
#
word_literal = '<' ws <(hex_digit){8}>:x ws '>' -> int(x,16)
res_arrayref = (integer|symbol):r ws '[' ws (integer|symbol):i ws ']' -> ArrayRef((r,i))
resref = (integer|symbol):r ws ':' ws (integer|symbol):o ->ResRef((r,o))
objref = (integer|symbol):o ws '@' ws (integer|symbol):c -> ObjRef((c,o))
#
true = ('True'|'true') -> 0x50000001
false = ('False'|'false') -> 0x50000000
none = ('None'|'none') -> 0x5000FFFF
empty = ('empty'|'Empty') -> 0x5000FFFE
boolean = true | false
atom = resref|res_arrayref|objref|boolean|none|empty|integer|word_literal

parameter = atom | symbol | terminated_string

table_item = (integer|symbol):key ws ':' ws (array|table|terminated_string|none|empty|symbol):value ws ','? ws -> (key,value)
table_content = table_item*:t -> t
table = ('table'|'tbl') ws '(' ws table_content:t ws ')' -> dict(t)

array_item = (array|table|atom|terminated_string|symbol):value ws ','? ws -> value
array_content = array_item*:a -> Array(a)
array = ('array'|'ary') ws symbol?:lb ws '(' ws array_content:a ws ')' -> a.with_label(lb)

class = 'class' required_space symbol:c -> asm.set_fieldnames(c)
direct = direct_string | direct_hex

arg = ws simple_symbol:a ws ','? ws -> a
expression_item = function_item # FIXME distinguish between appropriate opcodes for each.
function_item = ws (symbol:lb ws ':')? ws (operation|direct)?:op space '\n' -> FItem(lb=locals().get('lb',None),op=locals().get('op',None))
function = 'function' ws symbol?:lb ws '(' arg*:args ')' ws '(' ws function_item*:body ws ')' -> Function(lb, args, body)

av = atom|(symbol:s -> asm.lookup_symbol(s))
or_expression = av:a ws '|' ws av:b -> a|b
add_expression = av:a ws '+' ws av:b -> a+b
sub_expression = av:a ws '-' ws av:b -> a-b
and_expression = av:a ws '&' ws av:b -> a&b
define_expression =  sub_expression | and_expression | or_expression | add_expression | atom |  symbol:s -> asm.lookup_symbol(s) 

simple_define = 'define' ws symbol:k ws '(' ws define_expression:e ws ')' -> asm.define_symbol(k, e) 
sdef_block = ws symbol:k ws '(' ws define_expression:e ws ')' ws ','? ws -> (k,e)
defines = 'defines' ws symbol:k ws '(' ws sdef_block*:d ws ')' -> asm.define_symbols(k, d)

define = simple_define | defines


symlistitem = symbol:s ws ','? ws -> s
include = 'include' ws '(' ws symlistitem*:s ws ')' ws -> [asm.include(v) for v in s]
short_include = 'include' ws symbol:s -> asm.include(s)
use = 'use' ws '(' ws symlistitem*:s ws ')' ws -> [asm.use(v) for v in s]
short_use = 'use' ws symbol:s -> asm.use(s)
resource = 'resource' ws av:v -> asm.set_context_resource(v)
label = simple_symbol:s ws ':' -> asm.toplevel_label(s)
toplevel = define | function | array | table | class | direct | comment | include | use |short_use|short_include|resource | direct_hex | direct_string |label
toplevelitem = (ws? toplevel:a ws?) -> a
program = toplevelitem*:a -> a

"""




import parsley
import cStringIO
import delv.util
import sys,os.path
class Assembler(object):
    def __init__(self,message_stream=sys.stderr,filename="<stream>",path=None):
        if path is None: path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rdasm_include')
        self.path = path
        p = globals()
        self.toplabels = []
        self.symtab = {}
        p['asm'] = self
        self.Parser = parsley.makeGrammar(RDASM_Opcodes+ '\n' +RDASM_Grammar_Preamble , p)
        self.linenumber=0
        self.filename="<unknown>"
        self.mstream = message_stream
        self.fieldnames = {}
        self.function_contexts = []
        self.output_file = None
    def begin_function_context(self, func):
        context = {sym:n for n,sym in enumerate(func.args)}
        callbacks = []
        self.function_contexts.append((func, context, callbacks))
        return callbacks
    def get_function_context(self):
        return self.function_contexts[-1]
    def end_function_context(self):
        return self.function_contexts.pop()
    def toplevel_label(self, s):
        return TLL(s)
    def set_context_resource(self,v):
        self.context_resource = v
    def include(self, ifil):
        pth = os.path.join(self.path, os.path.join(*ifil)+'.rdasm')
        f = self.assemble(open(pth).read())
    def use(self, usesym):
        for sym,val in self.symtab.items():
            #print "*",sym, usesym
            if sym[0] == usesym[0]:
                self.define_symbol(SymbolList(sym[1:]), self.lookup_symbol(sym))
    def set_fieldnames(self, fn):
        if self.output_file.tell(): self.error("Code generation began before `class` was seen.")
        #self.output_file.write_uint16(0xFFFF)
        #print "SET FIELDNAMES", self.output_file.tell()
        self.fieldnames = {}
        for sym in self.symtab:
            if sym[0] == fn[0]:
                self.fieldnames[SymbolList(sym[1:])] = self.lookup_symbol(sym)
        #print self.fieldnames
        return bytearray('\xFF\xFF')
        
    def define_symbols(self, base, syms):
        for k,v in syms:
            #print "dss",base,k,v
            self.define_symbol(SymbolList(base+k), v)
    def define_symbol(self, sym, e):
        #print >> self.mstream, "DEFINE", sym, e
        self.symtab[sym] = e
    def getval(self,thing,create=None):
        if isinstance(thing, SymbolList):
            return self.lookup_symbol(thing)
        else:
            return thing
    def register_conversation_prompt(self, loc):
        fn,fc,cb = self.get_function_context()
        fn.conversation_prompts.append(loc)
    def finish_conversation_prompt(self):
        fn,fc,cb = self.get_function_context()
        p = fn.conversation_prompts.pop()
        return p
        
    def getlval(self,thing, caller, loc, output=0xDEAD):
        if not isinstance(thing, SymbolList): return thing
        fn,fc,cb = self.get_function_context()
        if thing in fc: return fc[thing]
        if thing in self.symtab: return self.symtab[thing]
        cb.append((caller, thing, loc))
        return output
    def define_local_label(self, label, position):
        fn,fc,cb = self.get_function_context()
        if fn.label: self.define_symbol( SymbolList(fn.label + label), position)
        fc[label] = position
            
    def getfval(self,thing,warn_new=True):
        if not isinstance(thing,SymbolList): return thing
        fn,fc,cb = self.get_function_context()
        if thing in fc: return fc[thing]
        if thing in self.symtab: return lookup_symbol(thing)
        if warn_new is None:
            return None
        if warn_new:
            self.error("Local variable %s used before assignment"%thing[0], warn=True)
        rv = fn.local_vars
        fc[thing] = rv
        fn.local_vars += 1
        return rv
    def lookup_symbol(self, sym):
        try:
            return self.symtab[sym]
        except KeyError:
            self.error("undefined symbol %s"%'.'.join(sym))
            return 0x5000FFFF
    def error(self,msg,warn=False):
        print >> self.mstream, "%s %s:%d:"%("Warning:" if warn else "Error:",
            self.filename, self.linenumber), msg
    
    def write_code(self, item, ofile):
        if item is None:
            return None
        rv = None
        if isinstance(item,bytearray):
            ofile.write(item)
        elif isinstance(item,dict):
            rv = dict_write_code(item,ofile,self)
        else:
            rv = item.write_code(ofile, self)
        return rv
 
    def write_class_table(self,of):
        fieldnames = self.fieldnames
        table = {}
        for sym,field in self.fieldnames.items():
            if self.symtab.has_key(sym): table[field] = (
                0x80000000|(self.context_resource<<16)|self.getval(sym))

        dict_write_code(table, of, self)
         
    def assemble(self,source):
        source = source.strip()

        binfile = delv.util.BinaryHandler(cStringIO.StringIO())
        self.output_file = binfile
        callbacks = []
        parsed = self.Parser(source).program()
        for item in parsed:
            rv = self.write_code(item, binfile)
            #print binfile.tell()
            if rv: callbacks.extend(rv)

        for obj, label, position in callbacks:
             #print "Resolving long callback", obj, label, position
             t = binfile.tell()
             binfile.seek(position)
             labval = self.getval(label,None)
             if not labval:
                  self.error("Symbol remains unresolvable: %s"%label)
                  labval = 0xDEAD
             obj.finish(binfile, self, labval)
             binfile.seek(t)

        #print "CLASS", self.field_names 
        if self.fieldnames:
             cstart = binfile.tell()
             self.write_class_table(binfile)
             binfile.seek(0)
             binfile.write_uint16(cstart)

        return binfile.file.getvalue()

