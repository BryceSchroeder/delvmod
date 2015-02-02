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
class Library(object):
    """Class for providing tile graphics and properties."""
    def __init__(self, scenario=None):
        """Create a new tile library, optionally from the Scenario object
           provided."""
        pass
    def load_from_scenario(self, scenario):
        """Add the tiles (graphics, properties, and so forth) from a Delver
           scenario to this tile library. It will overwrite any already
           existing tiles with the same IDs."""
        pass
    def save_to_scenario(self, scenario):
        """Save the tile definitions and graphics to the scenario provided.
           The resources F004 (tile names), F002 (tile properties), and 
           various 8Exx tile graphics resources may be overwritten or added."""
    def get(self, idx, default=None):
        """Return the Tile object at the index provided, returning None if
         there is no such tile defined."""
        pass
    def set(self, idx, graphic): 
        """Saves a single tile into the tile library at the index provided."""
    def set_page(self, idx, graphic):
        """Replaces (or creates) a whole tile page (i.e. a 32x512 graphic with
           16 potential tiles. The index idx is the index of the first tile on
           the page to be replaced."""
        pass
    def get_page(self, idx, form='numpy'):
        """Returns a whole page of graphics, same index semantics as .set_page.
        """
        pass
    def tiles(self, idx=None, hidx=None): 
        """Returns a list of Tile objects that are found on the page of idx if 
           no parameter hidx is provided, otherwise all tiles found between 
           IDs [idx, hidx), and if both parameters are omitted, a list of all
           tile objects in this library."""
        pass
    def __getitem__(self, idx):
        """Returns the image of the tile idx directly."""
        pass
    def __setitem__(self, idx): 
        """Sets the content of an individual tile directly."""
        pass
