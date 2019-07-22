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
# Maps and prop lists. Convenience utilities for map visualization.

from __future__ import absolute_import, division, print_function, unicode_literals

import array
from . import store, util

def textual_location(flags, raw_location):
    loc = raw_location>>12,raw_location&0x000FFF
    container = (raw_location&0x00FFFF) - 0x100
    if flags == 0xFF:
        return "0x%06X Deleted"%(raw_location)
    if flags & 0x10:
        return "0x%06X (#%d)"%(raw_location,container+0x100)
    if flags & 0x08:
        return "0x%06X (@%d)"%(raw_location,container)
    else:
        return "0x%06X (%d,%d)"%((raw_location,)+loc)

def proptypename_with_flags(flags, proptype, aspect, library):
    if flags == 0x42:
        return "EGG"
    elif flags == 0x44:
        return "ROOF"
    elif flags&0xF0:
        return "%s?"%library.get_prop(proptype).get_name(aspect)
    else:
        return library.get_prop(proptype).get_name(aspect)


class PropListEntry(object):
    def __init__(self, flags, loc, aspect, proptype, d3, propref, storeref, u,
                 index=None):
        self.index=index
        self.set_location(loc)        
        self.flags = flags;self.aspect=aspect&0x1F
        self.rotated = aspect&0xE0
        self.proptype=proptype;self.d3=d3;self.propref=propref
        self.storeref=storeref;self.u=u
    def set_location(self, loc):
        if isinstance(loc, tuple):
            self.loc = loc
            self.raw_location = ((loc[0])<<12) | loc[1]
            self.container = (self.raw_location&0x00FFFF) - 0x100
        else:
            self.raw_location = loc
            self.container = (self.raw_location&0x00FFFF) - 0x100
            self.loc = self.raw_location>>12,self.raw_location&0x000FFF
    def set_flags(self, flags):
        self.flags = flags
    def textual_location(self):
        return textual_location(self.flags,self.raw_location)
    def inside_something(self):
        return self.flags & 0x18
    def show_in_map(self):
        # This is probably wrong - many details yet to be determined. FIXME
        if self.flags == 0xFF: return False
        return not (self.flags & 0x58)
    def get_loc(self): # FIXME
        return self.loc[0],self.loc[1]
    def okay_to_take(self):
        return self.flags & 0x01
    # Persistence data fields
    def get_d1(self):
        return self.d3>>8
    def set_d1(self,v):
        if v > 255: raise ValueError("d1 is an 8-bit quantity")
        self.d3 = (self.d3&0x00FF)|(v<<8)
    def get_d2(self):
        return self.d3&0xFF
    def set_d2(self,v):
        if v > 255: raise ValueError("d2 is an 8-bit quantity")
        self.d3 = (self.d3&0xFF00)|v
    def set_d3(self,v):
        self.d3 = v
    def get_d3(self):
        return self.d3
    def debug(self, library): 
        # Man I need to refactor, look at that nomenclature
        if self.show_in_map():
            tid = library.get_prop(self.proptype).get_tile(self.aspect)
            t = library.get_tile(tid)
            return "%02X:%03X:%X:%X-%03X:%08X-%s-%s(%04X)"%(
                self.flags,self.proptype, self.aspect, self.rotated,
                tid, t.attributes,
                library.get_prop(self.proptype).get_offset(self.aspect),
                self.get_name(library), self.get_d3())
        else:
            return "{%04X:%02X(%04X) %s}"%(
                self.proptype | (self.aspect<<10) | (self.rotated<<5), 
                self.flags, self.get_d3(), self.get_name(library))
    def get_name(self, library):
        if self.flags == 0x42:
            return "EGG"
        elif self.flags == 0x44:
            return "ROOF"
        elif self.flags&0xE0:
            return "(%s?)"%library.get_prop(
                self.proptype).get_name(self.aspect)
        else:
            return library.get_prop(self.proptype).get_name(self.aspect)

class PropList(store.Store):
    def __init__(self, src):
        store.Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.props = []
        self.propsat = {}
    def append(self, prop):
        self.props.append(prop)
        prop.index = len(self.props)-1
        if not self.propsat.has_key(prop.loc): 
            self.propsat[prop.loc] = []
        self.propsat[prop.loc].append(prop)
    def write_to_bfile(self, dest=None):
        if dest is None: dest = self.src
        dest.seek(0)
        for prop in self.props:
            dest.write_uint8(prop.flags)
            dest.write_uint24(prop.raw_location)
            dest.write_uint6_uint10(prop.rotated|prop.aspect,prop.proptype)
            dest.write_uint16(prop.get_d3())
            dest.write_uint16(prop.propref)
            dest.write_uint32(prop.storeref)
            dest.write_uint16(prop.u)
        dest.truncate()
    def load_from_bfile(self):
        self.empty()
        index = 0
        self.src.seek(0)
        while not self.src.eof():
            flags=self.src.read_uint8()
            loc= self.src.read_xy24()
            aspect,proptype = self.src.read_uint6_uint10()
            d3 = self.src.read_uint16()
            propref = self.src.read_uint16()
            storeref = self.src.read_uint32()
            u= self.src.read_uint16()
            nprop = PropListEntry(flags, loc,
                aspect, proptype,d3, propref, storeref,u,index)
            self.props.append(nprop)
            if not self.propsat.has_key(loc): self.propsat[loc] = []
            self.propsat[loc].append(nprop)
            index += 1
        #for prlist in self.propsat.values(): 
        #    prlist.sort(key=lambda p:p.draw_order())
    def props_at(self,loc):
        return self.propsat.get(loc,[])
    def draw_order(self):
        # NOTE should check to make sure this is always true... otherwise
        # this function needs to sort them as well.
        return self.props.__iter__()
    def __iter__(self):
        return self.props.__iter__()
    def __getitem__(self, n):
        return self.props[n]
    def __setitem__(self, k, v):
        self.props[k] = v
    def __len__(self):
        return len(self.props)

class Map(store.Store):
    def __init__(self, src):
        store.Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.rows = []
    def get_tile(self, x, y):
        """Return base tile at this location."""
        return self.map_data[x+y*self.width]
    def load_from_bfile(self):
        print("map loading")
        self.src.seek(0)
        self.width = self.src.read_uint16()
        self.height = self.src.read_uint16()
        self.unknown = self.src.read_uint16()
        assert not self.unknown

        self.roof_layer_size = self.src.read_uint16()
        self.roof_underlayer_size = self.src.read_uint16()
        assert self.roof_layer_size == self.roof_underlayer_size
        
        # if 0, show blackness instead
        self.horizontal_edge_propagation = self.src.read_uint8()
        self.vertical_edge_propagation = self.src.read_uint8()

        # which zoneport you end up at when you walk off of the map in
        # the four cardinal directions. Usually the same, but can be 
        # different - see 0x8026 for how the Cademia bridge is implemented
        self.exit_zoneport_north = self.src.read_uint16()
        self.exit_zoneport_east = self.src.read_uint16()
        self.exit_zoneport_south = self.src.read_uint16()
        self.exit_zoneport_west = self.src.read_uint16()

        # These seem to be zero. But if not, let's draw attention to it
        self.padding = self.src.readb(12)
        for b in self.padding: assert not b


        roof_length = 0x40*self.roof_layer_size+0x40*self.roof_underlayer_size
        self.roof_data = array.array('H')
        for _ in range(roof_length/2): 
            self.roof_data.append(self.src.read_uint16())
        self.map_data = array.array('H')
        for _ in range(self.width*self.height):
            self.map_data.append(self.src.read_uint16())
    

class Level(object):
    pass
