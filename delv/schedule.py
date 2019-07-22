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

import array
from . import store

class ScheduleList(store.Store):
    def __init__(self, src):
        store.Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty (self):
        self.schedules = []
        self.lengths = []
    def __iter__(self): return self.schedules.__iter__()
    def load_from_bfile(self):
        self.src.seek(0)
        self.lengths = [self.src.read_uint16() for _ in range(0x100)]
        
        for length in self.lengths:
            self.schedules.append([
                self.read_entry(self.src) for _ in range(length)])
    def read_entry(self, src):
        hour = src.read_uint8()
        mode = src.read_uint8()
        scripting = src.read_uint16()
        level = src.read_uint8()
        x,y = src.read_xy24()
        return (hour, mode, scripting, level, x, y)
    def write_to_bfile(self, dest=None):
        dest = dest or self.src
        dest.seek(0)
        for schedule in self.schedules:
            dest.write_uint16(len(schedule))
        for schedule in self.schedules:
            for hour,mode,scripting,level,x,y in schedule:
                dest.write_uint8(hour)
                dest.write_uint8(mode)
                dest.write_uint16(scripting)
                dest.write_uint8(level)
                dest.write_xy24(x,y)
        #print dest.tell(), "bytes written"


