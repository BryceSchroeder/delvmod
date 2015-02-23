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
        self.padding = self.src.read(12)
        for b in self.padding: assert not b


        roof_length = 0x40*self.roof_layer_size+0x40*self.roof_underlayer_size
        self.roof_data = array.array('H')
        for _ in xrange(roof_length/2): 
            self.roof_data.append(self.src.read_uint16())
        self.map_data = array.array('H')
        for _ in xrange(self.width*self.height):
            self.map_data.append(self.src.read_uint16())
    

class PropList(store.Store):
    pass

class Level(object):
    pass
