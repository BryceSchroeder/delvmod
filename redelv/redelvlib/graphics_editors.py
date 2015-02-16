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
            ("/Edit/Cut", "<control>X", self.edit_cut, 0, None),
            ("/Edit/Copy", "<control>C", self.edit_copy, 0, None),
            ("/Edit/Paste","<control>V", self.edit_paste, 0, None),
            ("/Edit/Clear", None, self.edit_clear, 0, None),)
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
        self.edited = None
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
        self.flags.set_text("0x%02X"%self.image.flags)
    def file_save(self, *args):
        # This is so needlessly slow and complicated, probably the
        # fault of X11
        img = self.pixmap.get_image(0,0,self.image.logical_width,
            self.image.logical_height)
        # YES, REALLY vvv This is barbaric...
        pixels = bytearray()
        for y in xrange(self.image.logical_height):
            for x in xrange(self.image.logical_width):
                pixels+=chr(delv.colormap.colormatch_rgb24(img.get_pixel(x,y)))
        self.image.set_image(pixels)
        self.res.set_data(self.image.get_data())
        self.unsaved = False
        self.redelv.unsaved = True
        self.load_image()
    def edit_copy(self, *args):
        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 
            self.image.logical_width,self.image.logical_height)
        pbuf.get_from_drawable(self.pixmap, gtk.gdk.colormap_get_system(),
            0,0,0,0,self.image.logical_width,self.image.logical_height)
        self.redelv.clipboard.set_image(pbuf)
    def edit_paste(self, *args):
        self.redelv.clipboard.request_image(self.paste,None)
    def paste(self, clipboard, pixbuf, data):
        if not pixbuf: return
        self.edited = pixbuf
        gc = self.pixmap.new_gc()
        self.pixmap.draw_pixbuf(gc, pixbuf, 0,0,0,0,
            pixbuf.get_width(), pixbuf.get_height())
        self.unsaved = True 
        self.display.set_from_pixmap(self.pixmap,None)
        self.redelv.unsaved = True
        
    def edit_cut(self, *args):
        self.edit_copy()
        self.edit_clear()
    def edit_clear(self, *args):
        gc = self.pixmap.new_gc()
        gc.set_foreground(gtk.gdk.Color(pixel=0x00))
        self.pixmap.draw_rectangle(gc, True,0,0,
            self.image.height,self.image.width)
        self.unsaved = True
        self.display.set_from_pixmap(self.pixmap,None)
 
class TileSheetEditor(GraphicsEditor): 
    has_flags = False
    default_size=320,600
    name = "Tile Sheet Editor"
class PortraitEditor(GraphicsEditor):
    has_flags = False
    name = "Portrait Editor"
class SizedEditor(GraphicsEditor):
    has_flags = True 
    default_size=480,480
    name = "Sized Image Editor"
class IconEditor(GraphicsEditor):
    has_flags = False
    name = "Icon Editor"
class LandscapeEditor(GraphicsEditor):
    has_flags = False
    name = "Landscape Editor"
