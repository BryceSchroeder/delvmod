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
# This file addresses sundry storage types used within Delver Archives,
# and as such is mostly a helper for other parts of delv. 
import delv.util, delv.archive, delv.store, delv.library
import editors
import cStringIO as StringIO
import gtk
# Note to self, make this support general tile layers
# Also, abstract the tile drawing so the code can be reused in something
# other than pygtk
# Idea: change palette to show selection
class MapEditor(editors.Editor):
    name = "Map Editor [nothing opened]"
    default_size = 800,600
    def gui_setup(self): 
        pbox = gtk.VBox(False,0)
        self.set_default_size(*self.default_size)
        menu_items = (
            ("/File/Save Resource", "<control>S", None, 0, None),
            ("/File/Revert",        None,    self.load, 0, None),
            ("/Edit/Cut",           "<control>X", None, 0, None),
            ("/Edit/Copy",          "<control>C", None, 0, None),
            ("/Edit/Paste",         "<control>V", None, 0, None),
            ("/Edit/Clear",          None,        None, 0, None),
            ("/Tool/Cursor",        "C",          None, 0, None),
            ("/Tool/Pencil",        "N",          None, 0, None),
            ("/Tool/Brush",         "B",          None, 0, None),
            ("/Tool/Rectangle Select", "R",       None, 0, None),
            ("/Tool/Stamp",         "M",          None, 0, None),
            ("/Tool/Eyedropper",   "E",           None, 0, None),
            ("/Tool/Prop Select",  "P",           None, 0, None),
            ("/View/Preview Palette Animation",None,None, 0, None),
            ("/View/Display Roof Layer",None,     None, 0, None),
            ("/View/Display Props",  None,        None, 0, None),
            ("/Windows/Tile Selector", "<control>T", None, 0, None),
            ("/Windows/Props List", "<control>P", None, 0, None),
            ("/Windows/Brushes",    "<control>B", None, 0, None),
            ("/Windows/Stamps",     "<control>M", None, 0, None),
            ("/Windows/Map Boundaries", None,     None, 0, None),
            )
        accel = gtk.AccelGroup()
        ifc = gtk.ItemFactory(gtk.MenuBar, "<main>", accel)
        self.add_accel_group(accel)
        ifc.create_items(menu_items)
        self.menu_bar = ifc.get_widget("<main>")
        pbox.pack_start(self.menu_bar, False, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        pbox.pack_start(sw, True, True, 5)
        self.add(pbox)
    def editor_setup(self):
        self.set_title("Map Editor [%04X]"%self.res.resid)
        self.library = self.redelv.get_library()
        
        self.load()
    def load(self):
        pass
