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
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 

import delv
import delv.archive
import sys
import delv.library

USAGE = '''
Usage: ./class_fields.py archive baseID

Prints out a table of the fields of the objects in the same
subindex as baseID. (E.g. baseID=1A00 prints out the tables from
all resources 1Axx.)

Using delv Version: %s
'''%delv.version


if len(sys.argv)<2:
    print >> sys.stderr, USAGE
    sys.exit(-1)

seen_fields = {}
source = open(sys.argv[1],'rb')
arch = delv.archive.Scenario(source)
series = ((int(sys.argv[2],16) & 0x0000FF00)>>8)-1
fieldcounts = {}
field_occurances = {}
singletons = {}
lib = delv.library.Library(arch)
for res in arch.resource_ids(series):
    name = lib.get_prop(res&0x03FF).get_name() if res>= 0x1000 and res <= 0x13ff else ''
    rfile = arch.get(res).as_file()
    rfile.seek(rfile.read_uint16())
    items = rfile.read_uint16()&0x0FFF
    print (" 0x%04X%s: %5d bytes, %d fields "%(res,' ("%s")'%name if name else '', len(rfile),items)
        ).center(60,"-")
    
    for n in xrange(items):
        value = rfile.read_uint32()
        key = rfile.read_uint16()
        occurances = field_occurances.get(key,{})
        counts = seen_fields.get(key,{})
        fieldcounts[key] = fieldcounts.get(key, 0)+1
        if value > 0x80000000:
            resid = (value &0x7FFF0000)>>16
            offset = value & 0x0000FFFF
            if resid != res:
                preview = "ALIEN DREF: [%04X:%04x]"%(resid,offset)
                counts['alien'] = counts.get('alien',0)+1
                occurances['alien']=occurances.get('alien',[])+[res]
            else:
                t = rfile.tell()
                rfile.seek(offset)
                prevbytes = rfile.readb(18)
                rfile.seek(t)
                preview = ' '.join(['%02X'%x for x in prevbytes])
                counts[preview[0:5]] = counts.get(preview[0:5],0)+1
                occurances[preview[0:5]] = occurances.get(preview[0:5],[])+[res]
        else:
            preview = ''
            counts['%08X'%value] = counts.get('%08X'%value,0)+1
            occurances['%08X'%value] = occurances.get('%08X'%value,[])+[res]
        seen_fields[key] = counts
        singletons[key] = res
        field_occurances[key] = occurances
        print " 0x%04X: 0x%08X  |  %s"%(key,value,preview)
print " STATISTICS ".center(70,'=')
fieldorder = [(v,k) for k,v in fieldcounts.items()]
fieldorder.sort()
for count, key in fieldorder:
    value = seen_fields[key]
    print (" FIELD 0x%04X - %d occurance%s"%(
       key,fieldcounts[key], 
       's' if fieldcounts[key] > 1 else ' in 0x%04X'%singletons[key]
       )).center(70,'-')
    for val,count in value.items():
        print "\t%3d:  %s"%(count,val)
        if res >= 0x1000 and res <= 0x13ff:
            print '\t', ', '.join(['%s'%lib.get_prop(rid&0x03FF).get_name() for rid in field_occurances[key][val]])
