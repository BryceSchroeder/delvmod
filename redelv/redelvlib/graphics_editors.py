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
import gtk,gobject
import delv
import delv.graphics

class GraphicsEditor(editors.Editor):
    name = "Graphics Editor (Unimplemented)"
    has_flags = True
    force_type = None
    default_size=320,320
    def gui_setup(self):
        self.set_default_size(*self.default_size)
        pbox = gtk.VBox(False,0)
        menu_items = (
            ("/File/Import", "<control>I", self.file_import, 0, None),
            ("/File/Export RGB", None, self.file_export, 0, None),
            ("/File/Export Indexed","<control>E",self.file_indexed,0,None),
            ("/File/Save Resource", "<control>S", self.file_save, 0, None),
            ("/File/Revert", None, self.revert, 0, None),
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
        self.toggle_palette.connect("toggled", self.palette_toggled)
        self.flags = gtk.Entry()
        self.flags.set_editable(False)
        if self.has_flags:
            hbox = gtk.HBox(False,0)
            hbox.pack_start(gtk.Label("Flags:"),True,True,0)
            hbox.pack_start(self.flags,False,True,0)
            pbox.pack_start(hbox,False,True,0)

        self.add(pbox)
        self.animation_sid = None
    def cleanup(self):
        if self.animation_sid is not None:
            gobject.source_remove(self.animation_sid)
    def palette_toggled(self, *argv):
        newstate = self.toggle_palette.get_active()
        print "Palette animation:",newstate
        if newstate:
            if self.is_unsaved():
                self.error_message("Save your changes, or revert them, first.")
                self.toggle_palette.set_active(False)
                return
            self.pal_n = 0
            self.animation_sid = gobject.timeout_add(
                100, self.animation_timer)
        else:
            gobject.source_remove(self.animation_sid)
            self.animation_sid = None
    def animation_timer(self):
        gc = self.pixmap.new_gc()
        self.pixmap.draw_indexed_image(gc, 
            0, 0, self.image.logical_width,self.image.logical_height,
            gtk.gdk.RGB_DITHER_NORMAL, 
            str(self.image.get_logical_image()), 
            self.image.logical_width, 
            delv.colormap.animated_rgb24[self.pal_n%8])
        self.display.set_from_pixmap(self.pixmap,None)
        self.pal_n += 1
        return True
    def editor_setup(self):
        self.load_image()
    def revert(self, *args): self.load_image()
    def load_image(self, *args):
        if self.force_type:
            self.image = self.force_type(self.res)
        else:
            self.image = delv.graphics.DelvImageFactory(self.res)
        self.set_title(self.name + " - %04X"%self.res.resid)
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
        # Iterating over pixels! This is barbaric!
        pixels = bytearray()
        for y in xrange(self.image.logical_height):
            for x in xrange(self.image.logical_width):
                pixels+=chr(delv.colormap.colormatch_rgb24(img.get_pixel(x,y)))
        self.image.set_image(pixels)
        self.res.set_data(self.image.get_data())
        self.set_saved()
        self.load_image()
    def get_pixbuf_from_pixmap(self):
        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 
            self.image.logical_width,self.image.logical_height)
        pbuf.get_from_drawable(self.pixmap, gtk.gdk.colormap_get_system(),
            0,0,0,0,self.image.logical_width,self.image.logical_height)
        return pbuf
    def file_import(self,*args):
        #if self.unsaved and self.warn_unsaved_changes(): return 
        path = "<undefined>"
        try:
            path = self.ask_open_path()
            if not path: return
            pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        except Exception,e:
            self.error_message("Couldn't open '%s': %s"%(path,
                repr(e)))
            return
        gc = self.pixmap.new_gc()
        self.pixmap.draw_pixbuf(gc, pixbuf, 0,0,0,0,
            pixbuf.get_width(), pixbuf.get_height())
        self.set_unsaved()
        self.display.set_from_pixmap(self.pixmap,None)
        self.redelv.set_unsaved()
    def file_export(self,*args):
        path = self.ask_save_path(default = "RGB%04X.png"%self.res.resid)
        if not path: return
        if not path.endswith(".png"): path += ".png"
        pbuf = self.get_pixbuf_from_pixmap()
        # The text chunk mechanism could be used to preserve non-visual data...
        pbuf.save(path, "png", {})
    def file_indexed(self,*args):
        path = self.ask_save_path(default = "%04X.png"%self.res.resid)
        if not path: return
        try:
            import Image
            pil_img = Image.frombuffer("P", 
                (self.image.logical_width, self.image.logical_height), 
                self.image.get_logical_image(), "raw",
                ("P",0,1))
            pil_img.putpalette(delv.colormap.pil)
            pil_img.save(path)
        except ImportError:
            self.error_message("Couldn't import python imaging library (PIL)")

    def edit_copy(self, *args):
        self.redelv.clipboard.set_image(self.get_pixbuf_from_pixmap())
    def edit_paste(self, *args):
        self.redelv.clipboard.request_image(self.paste,None)
    def paste(self, clipboard, pixbuf, data):
        if not pixbuf: return
        self.edited = pixbuf
        gc = self.pixmap.new_gc()
        self.pixmap.draw_pixbuf(gc, pixbuf, 0,0,0,0,
            pixbuf.get_width(), pixbuf.get_height())
        self.set_unsaved()
        self.display.set_from_pixmap(self.pixmap,None)
        
    def edit_cut(self, *args):
        self.edit_copy()
        self.edit_clear()
    def edit_clear(self, *args):
        gc = self.pixmap.new_gc()
        gc.set_foreground(gtk.gdk.Color(pixel=0x00))
        self.pixmap.draw_rectangle(gc, True,0,0,
            self.image.height,self.image.width)
        self.set_unsaved()
        self.display.set_from_pixmap(self.pixmap,None)
 
class TileSheetEditor(GraphicsEditor):
    force_type = delv.graphics.TileSheet
    has_flags = False
    default_size=320,600
    name = "Tile Sheet Editor"
class PortraitEditor(GraphicsEditor):
    force_type = delv.graphics.Portrait
    has_flags = False
    name = "Portrait Editor"
class SizedEditor(GraphicsEditor):
    force_type = delv.graphics.General
    has_flags = True 
    default_size=480,480
    name = "Sized Image Editor"
class IconEditor(GraphicsEditor):
    force_type = delv.graphics.SkillIcon
    has_flags = False
    name = "Icon Editor"
class LandscapeEditor(GraphicsEditor):
    force_type = delv.graphics.Landscape
    has_flags = False
    name = "Landscape Editor"
