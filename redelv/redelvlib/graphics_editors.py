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
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 
import editors
import gtk
import delv
import delv.graphics

class GraphicsEditor(editors.Editor):
    name = "Graphics Editor (Unimplemented)"
    has_flags = True
    default_size=320,320
    def gui_setup(self):
        self.set_default_size(*self.default_size)
        pbox = gtk.VBox(False,0)
        menu_items = (
            ("/File/Import", "<control>I", None, 0, None),
            ("/File/Export", "<control>E", None, 0, None),
            ("/File/Save Resource", "<control>S", self.file_save, 0, None),
            ("/File/Revert", None, self.load_image, 0, None),
            ("/Edit/Cut", "<control>X", None, 0, None),
            ("/Edit/Copy", "<control>C", None, 0, None),
            ("/Edit/Paste","<control>P", None, 0, None),
            ("/Edit/Clear", None, None, 0, None),)
        accel = gtk.AccelGroup()
        ifc = gtk.ItemFactory(gtk.MenuBar, "<main>", accel)
        self.add_accel_group(accel)
        ifc.create_items(menu_items)
        self.menu_bar = ifc.get_widget("<main>")
        pbox.pack_start(self.menu_bar, False, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.display = gtk.Image()
        sw.add_with_viewport(self.display)
        pbox.pack_start(sw, True, True, 10)

        self.toggle_palette = gtk.ToggleButton("Run Palette Animation")
        pbox.pack_start(self.toggle_palette, False,True,0)
        self.flags = gtk.Entry()
        self.flags.set_editable(False)
        if self.has_flags:
            hbox = gtk.HBox(False,0)
            hbox.pack_start(gtk.Label("Flags:"),True,True,0)
            hbox.pack_start(self.flags,False,True,0)
            pbox.pack_start(hbox,False,True,0)

        self.add(pbox)
    def editor_setup(self):
        self.image = delv.graphics.DelvImageFactory(self.res)
        self.load_image()
    def load_image(self, *args):
        data = self.image.get_logical_image()
        self.pixmap = gtk.gdk.Pixmap(None,
            self.image.logical_width,self.image.logical_height,
                gtk.gdk.visual_get_system().depth)
        # Requiring a graphics context makes it "easier!" :/
        gc = self.pixmap.new_gc()
        self.pixmap.draw_indexed_image(gc, 
            0, 0, self.image.logical_width,self.image.logical_height,
            gtk.gdk.RGB_DITHER_NORMAL, 
            str(data), self.image.logical_width, delv.colormap.rgb24)
        self.display.set_from_pixmap(self.pixmap,None)
     def file_save(self, *args):
         self.unsaved = False
         print "FIXME save not implemented yet"
class TileSheetEditor(GraphicsEditor): 
    has_flags = False
    default_size=320,600
    name = "Tile Sheet Editor"
class PortraitEditor(GraphicsEditor):
    has_flags = False
    name = "Portrait Editor"
class SizedEditor(GraphicsEditor):
    has_flags = True 
    name = "Sized Image Editor"
class IconEditor(GraphicsEditor):
    has_flags = False
    name = "Icon Editor"
class LandscapeEditor(GraphicsEditor):
    has_flags = False
    name = "Landscape Editor"
