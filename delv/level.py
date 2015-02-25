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
# Maps and prop lists. Convenience utilities for map visualization.
import delv.util
import store
import array

class PropListEntry(object):
    def __init__(self, flags, loc, aspect, proptype, d3, propref, storeref, u):
        self.flags = flags;self.loc=loc;self.aspect=aspect&0x1F
        self.rotated = aspect&0xE0
        self.proptype=proptype;self.d3=d3;self.propref=propref
        self.storeref=storeref;self.u=u
    def show_in_map(self):
        # This is probably wrong - many details yet to be determined. FIXME
        return not (self.flags & 0x4C)
    def get_loc(self): # FIXME
        return self.loc[0],self.loc[1]
    # Persistence data fields
    def get_d1(self):
        return self.d3>>8
    def set_d1(self,v):
        if v > 255: raise ValueError, "d1 is an 8-bit quantity"
        self.d3 = (self.d3&0x00FF)|(v<<8)
    def get_d2(self):
        return self.d3&0xFF
    def set_d2(self,v):
        if v > 255: raise ValueError, "d2 is an 8-bit quantity"
        self.d3 = (self.d3&0xFF00)|v
    def set_d3(self,v):
        self.d3 = v
    def get_d3(self):
        return self.d3
    def debug(self, library): 
        # Man I need to refactor, look at that nomenclature
        if self.show_in_map():
            t = library.get_tile(library.get_prop(
                self.proptype).get_tile(self.aspect))
            return "%03X:%X:%X-%08X[%08X]-%s(%04X)"%(
                self.proptype, self.aspect, 
                self.rotated, t.attributes, t.draw_priority(),
                t.get_name(), self.get_d3())
        else:
            return "{%04X:%02X(%04X)}"%(
                self.proptype | (self.aspect<<10) | (self.rotated<<5), 
                self.flags, self.get_d3())

class PropList(store.Store):
    def __init__(self, src):
        store.Store.__init__(self, src)
        self.empty()
        if self.src: self.load_from_bfile()
    def empty(self):
        self.props = []
        self.propsat = {}
    def load_from_bfile(self):
        while not self.src.eof():
            flags=self.src.read_uint8()
            loc= self.src.read_xy24()
            aspect,proptype = self.src.read_uint6_uint10()
            d3 = self.src.read_uint16()
            propref = self.src.read_uint32()
            storeref = self.src.read_uint16()
            u= self.src.read_uint16()
            nprop = PropListEntry(flags, loc,
                aspect, proptype,d3, propref, storeref,u)
            self.props.append(nprop)
            if not self.propsat.has_key(loc): self.propsat[loc] = []
            self.propsat[loc].append(nprop)
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
        for _ in xrange(roof_length/2): 
            self.roof_data.append(self.src.read_uint16())
        self.map_data = array.array('H')
        for _ in xrange(self.width*self.height):
            self.map_data.append(self.src.read_uint16())
    

class Level(object):
    pass
