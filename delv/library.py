#!/usr/bin/env python
# Copyright 2015 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
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
import archive,hints,tile,prop
import array
class Library(object):
    """This class is a wrapper around one or more Delver archives, and 
       facilitates retrieving various kinds of objects by their resource
       ID. I.e, whereas the delv.archive.Scenario object will return a 
       delv.archive.Resource object when asked for resource ID 0x8E91,
       the library will return a delv.graphics.TileSheet object. 

       The Library also provides facilities that integrate multiple
       resources into logical parts, e.g. it unifies graphical tiles
       with their names and properties, and allows them to be retrieved
       under a simple API.
 
       The library is a read-only facility and it assumes that its underlying
       archive does not change from under it. If that assumption is not true,
       i.e. if you are using it as part of an editor, you will need to tell
       the library the underlying archive has changed with .update(). This 
       will purge all caches."""
    def __init__(self, *archives):
        """Create a new library, using the archives provided. The search path
           will be from last to first, i.e. if you say Library(A, B, C) and 
           archives B and C both contain a resource 0xFFFF, and you ask for
           0xFFFF, you will get the one from archive C."""
        self.cache = {}
        self.archives = archives[::-1]
        self.load_tiles()
        self.load_props()

    def load_props(self):
        self.props = []
        proptiles = self.get_object(0xF000)
        xoffsets = self.get_object(0xF011)
        yoffsets = self.get_object(0xF012)
        for pid,tile in enumerate(proptiles):
            self.props.append(prop.Prop(pid, tile, zip(
                       xoffsets[pid<<5:(pid<<5)+32],
                       yoffsets[pid<<5:(pid<<5)+32]), scripts=None))

    def load_tiles(self):
        tilenames = self.get_object(0xF004)
        tileattrs = self.get_object(0xF002)
        tilecompositions = self.get_object(0xF013)
        tilefauxprops = self.get_object(0xF010)
        tilesheets = self.objects(hints.GRAPHICS_TILESHEET, True)
        self.tiles = []
        tile_Nothing = tile.Tile(0,tilenames[0], tileattrs[0],
            tilefauxprops[0],
            tilesheets[0].get_tile(0))

        
        for n,attr in enumerate(tileattrs):
            tileres_n = (n >> 4)&0xFF
            if not (tileattrs[n] or tilesheets[tileres_n]): 
                self.tiles.append(tile_Nothing)
                continue
            if n < 0x1000:
                self.tiles.append(tile.Tile(n,tilenames[n], tileattrs[n],
                    tilefauxprops[n],
                    tilesheets[tileres_n].get_tile(n&0x00F)))
            elif n < 0x2000:
                self.tiles.append(tile.CompoundTile(n,tilenames[n],
                    tileattrs[n],tilefauxprops[n],
                    self,tilecompositions[n-0x1000]))
            else: 
                assert 0, "Turns out there are more tiles than I thought."
                
    def get_tile(self, tid):
        """Returns the specified Tile, or "Nothing" if there is none such."""
        return self.tiles[tid]
    def get_prop(self, ptype):
        return self.props[ptype]

    def objects(self,si=None,dense=False):
        if dense:
            return [self.get_object((si,n)) for n in xrange(256)]
        else:
            return [self.get_object(resid) for resid in self.resource_ids(si)]
    def resources(self,si=None):
        return [self.get_resource(resid) for resid in self.resource_ids(si)]
    def resource_ids(self, si=None):
        ids = set()
        for archive in self.archives:
            ids.update(archive.resource_ids(si))
        return list(ids)
    def get_resource(self, resid):
        """Get a resource by its resource ID or subindex,n pair."""
        for archive in self.archives:
            r = archive.get(resid)
            if r: return r
        return None
    def get_object(self, resid):
        """Get the appropriate kind of object for a specified resource."""
        r = self.get_resource(resid)
        if not r: return None
        if r in self.cache: return self.cache[r]
        C = hints.class_by_resid(r.resid)
        if not C: return None
        ob = C(r)
        self.cache[r] = ob
        return ob
    
