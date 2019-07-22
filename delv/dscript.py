#!/usr/bin/env python
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

from __future__ import absolute_import, division, print_function, unicode_literals

from . import store
from . import ddasm
from . import rdasm

DSM_WARN = """
; Caution: this is automatically generated code that has not been manually 
; checked. It should reassemble to the original binary, but it may not make
; sense. You may wish to use TAUCS instead where available, for source files
; which have been checked and supplied with meaningful symbolic names, etc.
""".strip()

class Script(store.Store):
    force_classmode = False
    def __init__(self, src):
        store.Store.__init__(self,src)
        self.disassembler = ddasm.Disassembler(self.res.resid)
        
    
    def disassemble(self):
        self.data = self.res.get_data()
        return self.disassembler.disassemble(self.data,
                                   force_classmode = self.force_classmode,
                                   preamble = DSM_WARN)
     
    

class Class(Script):
    force_classmode = True

class Direct(Script):
    force_classmode = False
