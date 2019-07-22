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

import delv
import delv.ddasm
import sys
from sys import argv

if len (argv) < 2:
    print("Usage: ddasm.py binfile.out resid [output.rdasm]", file=sys.stderr)
    sys.exit(0)


machinecode = open(argv[1],'rb')

context_resid = int(argv[2].replace('0x',''),16)
disassembler = delv.ddasm.Disassembler(context_resid)

source = str(disassembler.disassemble(machinecode))

output = open(argv[3] if len(argv) > 3 else 'dda.rdasm','wb')

output.write(source)

