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
import delv.colormap, delv.level
import editors
import cStringIO as StringIO
import gtk

class PropListEditor(editors.Editor):
    name = "Prop List Editor [nothing opened]"
    default_size = 800,600
    def gui_setup(self):
        pbox = gtk.VBox(False,0)
        self.set_default_size(*self.default_size)

        menu_items = (
            ("/File/Save Resource", "<control>S", None, 0, None),
            ("/File/Revert",        None,    self.load, 0, None),
            ("/File/Export CSV",  None,    None, 0, None),
            ("/File/Import CSV",  None,    None, 0, None),
            ("/Edit/Cut",           "<control>X", None, 0, None),
            ("/Edit/Copy",          "<control>C", None, 0, None),
            ("/Edit/Paste",         "<control>V", None, 0, None),
            ("/Edit/Delete",          None,        None, 0, None),
            ("/Map/Open Map",        "<control>M",    self.open_map, 0, None),
            ("/Map/Send Selection to Map",  "S", self.send_selection, 0, None),
            ("/Select/Container Contents", "<control>N",None,0,None),
            ("/Select/Others in Cell","<control>T",None,0,None),
            ("/Select/Parent","<control>P",None,0,None),
            ("/Select/Scroll to Selected","<control>F",None,0,None),
            )

        accel = gtk.AccelGroup()
        ifc = gtk.ItemFactory(gtk.MenuBar, "<main>", accel)
        self.add_accel_group(accel)
        ifc.create_items(menu_items)
        self.menu_bar = ifc.get_widget("<main>")
        pbox.pack_start(self.menu_bar, False, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        self.data_view = gtk.TreeView()
        self.data_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        dc = gtk.TreeViewColumn()
        dc.set_title("Index")
        c = gtk.CellRendererText()
        c.set_property('editable',False)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",0)
        self.data_view.append_column(dc)
        
        dc = gtk.TreeViewColumn()
        dc.set_title("Flags")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",1)
        self.data_view.append_column(dc)
        
        dc = gtk.TreeViewColumn()
        dc.set_title("Free")
        c = gtk.CellRendererToggle() 
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"active",12)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Prop Type")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",2)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Location")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",3)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Rotate?")
        c = gtk.CellRendererToggle() 
        #c.connect('toggled', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"active",4)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Aspect")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",5)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("D1")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",6)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("D2")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",7)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("D3")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",8)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Prop Reference")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",9)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Storage")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        #c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",10)
        self.data_view.append_column(dc)


        sw.add(self.data_view)
        pbox.pack_start(sw, True, True, 5)
        self.add(pbox)
    def load(self):
        self.lmap = self.library.get_object(self.res.resid - 0x0100)
        self.props = delv.level.PropList(self.res)
        self.tree_data = gtk.ListStore(str,str,str,str,bool,str,
            str,str,str,str,str,int,bool)
        self.data_view.set_model(self.tree_data)
        for idx,prop in enumerate(self.props):
            self.tree_data.append(["%d"%idx, "0x%02X"%prop.flags,
                "0x%03X (%s)"%(prop.proptype,prop.get_name(self.library)),
                prop.textual_location(),
                prop.rotated, "%d"%prop.aspect, "%d"%prop.get_d1(),
                "%d"%prop.get_d2(), "0x%04X"%prop.get_d3(),
                "0x%08X"%prop.propref, "0x%04X"%prop.storeref, idx,
                prop.okay_to_take()
                ])

    def editor_setup(self):
        self.set_title("Prop List Editor [%04X]"%self.res.resid)
        self.map_editor = None
        self.library = self.redelv.get_library()
        self.load()
    def cleanup(self):
        if self.map_editor: self.map_editor.prop_editor = None

    def open_map(self, *argv):
        if self.map_editor:
            self.map_editor.show_all()
            self.map_editor.present()
        else:
            self.map_editor = self.redelv.open_editor(self.res.resid-0x0100)
            self.map_editor.marry(self)
            self.map_editor.prop_editor = self
    def send_selection(self, *argv):
        if not self.map_editor: self.open_map()
        tm,paths = self.data_view.get_selection().get_selected_rows()
        selected = [
            tm.get_value(tm.get_iter(path),11) for path in paths]
        self.map_editor.change_selection(selected)
    def select_props_by_index(self, selection):
        tsel = self.data_view.get_selection()
        tsel.unselect_all()
        if not selection: return
        for prop in selection:
            tsel.select_path(prop)

     

# Note to self, make this support general tile layers
# Also, abstract the tile drawing so the code can be reused in something
# other than pygtk
# Idea: change palette to show selection
class MapEditor(editors.Editor):
    name = "Map Editor [nothing opened]"
    default_size = 800,600
    def gui_setup(self): 
        self.mouse_position = 0,0

        pbox = gtk.VBox(False,0)
        self.set_default_size(*self.default_size)
        menu_items = (
            ("/File/Save Resource", "<control>S", None, 0, None),
            ("/File/Revert",        None,    self.load, 0, None),
            ("/File/Export Image",  None,    self.export_img, 0, None),
            ("/Edit/Cut",           "<control>X", None, 0, None),
            ("/Edit/Copy",          "<control>C", None, 0, None),
            ("/Edit/Paste",         "<control>V", None, 0, None),
            ("/Edit/Clear",          None,        None, 0, None),
            ("/Tool/Cursor",        "C",          None, 0, None),
            ("/Tool/Pencil",        "N",          None, 0, None),
            ("/Tool/Brush",         "B",          None, 0, None),
            ("/Tool/Rectangle Select", "R",       None, 0, None),
            ("/Tool/Tile Select", "T",       self.tile_select, 0, None),
            ("/Tool/Stamp",         "M",          None, 0, None),
            ("/Tool/Eyedropper",   "E",           None, 0, None),
            ("/Tool/Prop Select",  "P",           self.prop_select, 0, None),
            ("/Tool/Select None",  "X",           self.select_none, 0, None),
            ("/View/Preview Palette Animation",None,None, 0, None),
            ("/View/Display Roof Layer",None,     None, 0, None),
            ("/View/Display Props",  None,        None, 0, None),
            ("/View/Send Selection to Prop List","S",self.send_selection,
                    0,None),
            ("/Windows/Tile Selector", "<control>T", None, 0, None),
            ("/Windows/Props List", "<control>P", self.open_props, 0, None),
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
        self.display = gtk.Image()
        self.eventbox = gtk.EventBox()
        self.eventbox.add_events(
            gtk.gdk.POINTER_MOTION_MASK|gtk.gdk.BUTTON_PRESS)
        self.eventbox.connect("motion-notify-event", self.mouse_movement)
        self.eventbox.connect("button-press-event", self.mouse_click)
        self.eventbox.add(self.display)
        self.sbox = gtk.Fixed()
        self.sbox.put(self.eventbox, 0,0)
        sw.add_with_viewport(self.sbox)
        pbox.pack_start(sw, True, True, 0)
        self.sw = sw
 
        hbox = gtk.HBox(False,0)

        hbox.pack_start(gtk.Label("Cursor:"),False,True,0)
        self.w_xpos = gtk.Entry()
        self.w_xpos.set_width_chars(4)
        self.w_xpos.set_editable(False)
        hbox.pack_start(self.w_xpos,False,True,0)
        self.w_ypos = gtk.Entry()
        self.w_ypos.set_width_chars(4)
        self.w_ypos.set_editable(False)
        hbox.pack_start(self.w_ypos,False,True,0)

        hbox.pack_start(gtk.Label("Map Data:"),False,True,0)
        self.w_mapdata = gtk.Entry()
        self.w_mapdata.set_width_chars(6)
        self.w_mapdata.set_editable(False)
        hbox.pack_start(self.w_mapdata,False,True,0)

        hbox.pack_start(gtk.Label("Name:"),False,True,0)
        self.w_name = gtk.Entry()
        self.w_name.set_editable(False)
        hbox.pack_start(self.w_name,False,True,0)

        hbox.pack_start(gtk.Label("Attr:"),False,True,0)
        self.w_attr = gtk.Entry()
        self.w_attr.set_width_chars(10)
        self.w_attr.set_editable(False)
        hbox.pack_start(self.w_attr,True, True, 0)

        hbox.pack_start(gtk.Label("Faux Prop:"),False,True,0)
        self.w_faux = gtk.Entry()
        self.w_faux.set_width_chars(9)
        self.w_faux.set_editable(False)
        hbox.pack_start(self.w_faux,True, True, 0)

        hbox.pack_start(gtk.Label("FP Tile:"),False,True,0)
        self.w_fauxtile = gtk.Entry()
        self.w_fauxtile.set_width_chars(6)

        self.w_fauxtile.set_editable(False)
        hbox.pack_start(self.w_fauxtile,True, True, 0)

        hbox.pack_start(gtk.Label("FP Attr:"),False,True,0)
        self.w_fauxattr = gtk.Entry()
        self.w_fauxattr.set_width_chars(10)
        self.w_fauxattr.set_editable(False)
        hbox.pack_start(self.w_fauxattr,True, True, 0)

        hbox.pack_start(gtk.Label("FP Offs:"),False,True,0)
        self.w_fauxoffs = gtk.Entry()
        self.w_fauxoffs.set_width_chars(5)
        self.w_fauxoffs.set_editable(False)
        hbox.pack_start(self.w_fauxoffs,True, True, 0)
        pbox.pack_start(hbox, False, True, 0)

        self.w_props = gtk.Entry()
        self.w_props.set_width_chars(80)
        self.w_props.set_editable(False)
        pbox.pack_start(self.w_props, False, True, 0)


        self.add(pbox)
    #def set_view(self,x=None,y=None):
    #    if x is not None: self.view_x = x
    #    if y is not None: self.view_y = y
    #def get_view_rect(self):
    #    return (self.view_x,self.view_y,
    #        self.sw.allocation.width,self.sw.allocation.height)

    def editor_setup(self):
        self.set_title("Map Editor [%04X]"%self.res.resid)
        self.prop_editor = None
        self.click_tool = None
        self.selection = None
        self.library = self.redelv.get_library()
        self.load()
        self.pixmap = gtk.gdk.Pixmap(None, 
            self.lmap.width*32, self.lmap.height*32,
                gtk.gdk.visual_get_system().depth)
        print 0,0,self.lmap.width*32, self.lmap.height*32
        self.gc = self.pixmap.new_gc(function=gtk.gdk.COPY)
        self.gc.set_foreground(gtk.gdk.Color(pixel=0x00000000))
        #self.gc.set_background(gtk.gdk.Color(255,0,0))
        self.pixmap.draw_rectangle(self.gc, True, 
            0,0,self.lmap.width*32,self.lmap.height*32)
        #self.view_rect=0,0,self.sw.allocation.width,self.sw.allocation.height
        self.draw_map()     

    def draw_tile(self, x, y, tid, pal=delv.colormap.rgb24, as_prop=False,
                  offset=(0,0),rotated=False,inhibit=False):
        if not tid: return
        tile =  self.library.get_tile(tid)
        xo,yo = offset[::-1] if rotated else offset
        attr = tile.attributes
        if not inhibit:
            if rotated: #refactor this now that we understand howit works FIXME
                if as_prop and attr & 0x00000C0 ==   0x40:
                    self.draw_tile(x-1,y, tile.index-1, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
                elif as_prop and attr & 0x00000C0 == 0x80:
                    self.draw_tile(x,y-1, tile.index-1, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
                elif as_prop and attr & 0x00000C0 == 0xC0:
                    self.draw_tile(x-1,y-1, tile.index-3, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
                    self.draw_tile(x-1,y, tile.index-2, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
                    self.draw_tile(x,y-1, tile.index-1, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
            else: 
                if as_prop and attr & 0x00000C0 ==   0x40:
                    self.draw_tile(x,y-1, tile.index-1, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
                elif as_prop and attr & 0x00000C0 == 0x80:
                    self.draw_tile(x-1,y, tile.index-1, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
                elif as_prop and attr & 0x00000C0 == 0xC0:
                    self.draw_tile(x-1,y-1, tile.index-3, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
                    self.draw_tile(x,y-1, tile.index-2, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)
                    self.draw_tile(x-1,y, tile.index-1, pal=pal,as_prop=True,
                                   offset=offset,rotated=rotated,inhibit=True)


        if tile.requires_mask or as_prop:
            self.gc.set_clip_origin(x*32-xo, y*32-yo)
            self.gc.set_clip_mask(tile.get_pixmap_mask(gtk,rotated))
        else: 
            self.gc.set_clip_mask(None)
        self.pixmap.draw_indexed_image(self.gc, x*32-xo, y*32-yo, 32, 32,
            gtk.gdk.RGB_DITHER_NORMAL, tile.get_image(rotated),
            32, pal)
        if tile.fauxprop:
            fauxprop = self.library.get_prop(tile.fauxprop)
            fptile = fauxprop.get_tile(tile.fauxprop_aspect)
            self.draw_tile(x, y, fptile, pal=pal,as_prop=True,
                           offset=fauxprop.get_offset(tile.fauxprop_aspect),
                           rotated=tile.fauxprop_rotate)
        
    # FIXME needs to incorporate faux props into the prop list and draw
    # them under the same priority system as listed props
    def draw_map(self,stop=None):
        for y in xrange(stop[1] if stop else self.lmap.height):
            for x in xrange(stop[0] if stop else self.lmap.width):
                self.draw_tile(x,y,self.lmap.map_data[x+y*self.lmap.width])
        for y in xrange(self.lmap.height):
            for x in xrange(self.lmap.width):
                if not self.props: continue
                prpat = self.props.props_at((x,y))
                visible = filter(lambda r:r.show_in_map(), prpat)[::-1]
                visible.sort(key=(lambda p: self.library.get_tile(
                    self.library.get_prop(p.proptype).get_tile(
                        p.aspect)).draw_priority()))
                for p in visible:
                    x,y = p.get_loc()
                    proptype = self.library.get_prop(p.proptype)
                    proptile = proptype.get_tile(p.aspect)
                    self.draw_tile(x,y,proptile, 
                        offset=proptype.get_offset(p.aspect), as_prop=True,
                        rotated=p.rotated)
                # draw invisible props
                invisible = filter(lambda r: not r.show_in_map(), prpat)
                for p in invisible: 
                    x,y = p.get_loc()
                    proptype = self.library.get_prop(p.proptype)
                    proptile = proptype.get_debug_tile(p.aspect)
                    self.draw_tile(x,y,proptile, 
                        offset=proptype.get_offset(p.aspect), as_prop=True,
                        rotated=p.rotated)
        if isinstance(self.selection, tuple):
            x,y = self.selection
            self.draw_tile(x,y,
                self.lmap.map_data[x+y*self.lmap.width],
                pal=delv.colormap.selected_rgb24)
        elif self.selection is None:
            pass
        elif self.props:
            for pidx in self.selection:
                p = self.props[pidx]
                proptype = self.library.get_prop(p.proptype)
                if p.show_in_map():
                    proptile = proptype.get_tile(p.aspect)
                else:
                    proptile = proptype.get_debug_tile(p.aspect)
                x,y = p.loc
                self.draw_tile(x,y,proptile, 
                    offset=proptype.get_offset(p.aspect), as_prop=True,
                    rotated=p.rotated, pal=delv.colormap.selected_rgb24)


        self.display.set_from_pixmap(self.pixmap,None)

    def load(self):
        self.lmap = delv.level.Map(self.res)
        self.props = self.library.get_object(self.res.resid + 0x0100)
    def change_selection(self, ns):
        if self.selection == ns: return 
        self.selection = ns
        self.draw_map()
    def select_none(self, *argv):
        self.change_selection(None)
    def tile_select(self, *argv):
        self.click_tool = self.tile_select_tool
    def tile_select_tool(self, x, y):
        self.change_selection((x,y))
    def prop_select(self, *argv):
        self.click_tool = self.prop_select_tool
    def prop_select_tool(self, x, y):
        self.change_selection([p.index for p in self.props.props_at((x,y))])
    def update_cursor_info(self):
        x,y = self.mouse_position
        self.w_xpos.set_text(str(x))
        self.w_ypos.set_text(str(y))
        self.w_mapdata.set_text("0x%04X"%(
            self.lmap.map_data[x+y*self.lmap.width]))
        tile = self.library.get_tile(self.lmap.get_tile(x,y))
        self.w_name.set_text(
            tile.get_name())
        self.w_attr.set_text(
            "0x%08X"%tile.attributes)
        self.w_faux.set_text(
            "0x%03X:%X:%d"%(tile.fauxprop,tile.fauxprop_aspect,
                 tile.fauxprop_rotate))
        if tile.fauxprop:
             fp = self.library.get_prop(tile.fauxprop)
             self.w_fauxtile.set_text(
                "0x%04X"%(fp.tile))
             self.w_fauxattr.set_text(
                "0x%08X"%self.library.get_tile(fp.get_tile(
                     tile.fauxprop_aspect)).attributes)
             self.w_fauxoffs.set_text(
                "%d,%d"%fp.get_offset(tile.fauxprop_aspect))
        else:
             self.w_fauxtile.set_text("(NA)")
             self.w_fauxattr.set_text("(NA)")
             self.w_fauxoffs.set_text("(NA)")
        if self.props: p = self.props.props_at((x,y))
        else: return
        if not p:
             self.w_props.set_text("(No props)")
        else:
             self.w_props.set_text(', '.join(map(
                 lambda p:p.debug(self.library),p)))
    def mouse_movement(self, widget, event):
        if event.x is None or event.y is None: return
        x,y= widget.translate_coordinates(self.display, 
             int(event.x),int(event.y))
        newp = x//32,y//32
        if newp != self.mouse_position:
            self.mouse_position = newp
            self.update_cursor_info()
    def mouse_click(self, widget, event):
        if event.x is None or event.y is None: return
        x,y= widget.translate_coordinates(self.display, 
             int(event.x),int(event.y))
        newp = x//32,y//32
        if self.click_tool: self.click_tool(*newp)
    def export_img(self, *argv):
        path = self.ask_save_path(default = "Map%04X.png"%self.res.resid)
        if not path: return
        if not path.endswith(".png"): path += ".png"
        pbuf = self.get_pixbuf_from_pixmap()
        pbuf.save(path, "png", {})
    def get_pixbuf_from_pixmap(self):
        pbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 
            self.lmap.width*32,self.lmap.height*32)
        pbuf.get_from_drawable(self.pixmap, gtk.gdk.colormap_get_system(),
            0,0,0,0,self.lmap.width*32,self.lmap.height*32)
        return pbuf
    def open_props(self, *argv):
        if self.prop_editor:
            self.prop_editor.show_all()
            self.prop_editor.present()
        else:
            self.prop_editor = self.redelv.open_editor(self.res.resid+0x0100)
            self.prop_editor.marry(self)
            self.prop_editor.map_editor = self
    def cleanup(self):
        if self.prop_editor: self.prop_editor.map_editor = None
    def send_selection(self, *argv):
        if not isinstance(self.selection, list): pass
        if not self.prop_editor: self.open_props()
        self.prop_editor.select_props_by_index(self.selection)
