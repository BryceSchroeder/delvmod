#!/usr/bin/env python
# Copyright 2015 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
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

version = '0.1.0'

import pygtk
pygtk.require('2.0')
import gtk

import images

class ReDelv(object):

    def __init__(self):
        self.unsaved = False
        self.opened_file = None
        self.exported_directory = None

        # Make the main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_default_size(480,512)
        self.window.set_title("redelv - [No File Open]")
        self.window.set_icon(gtk.gdk.pixbuf_new_from_file(images.icon_path))
        
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.mvbox = gtk.VBox(homogeneous=False,spacing=0)
        self.window.add(self.mvbox)

        # Make the menu
        menu_items = (
            ("/_File",           None,          None,           0,  "<Branch>"),
            ("/File/_New",       "<control>N",  self.menu_new,  0,  None),
            ("/File/_Open",      "<control>O",  self.menu_open, 0,  None),
            ("/File/_Save",      "<control>S",  self.menu_save, 0,  None),
            ("/File/_Save _As",  None,          self.menu_save_as,0,None),
            ("/File/sep1",       None,          None,          0,"<Separator>"),
            ("/File/_Import",    None,          self.menu_import,0, None),
            ("/File/_Export",    "<control>E",  self.menu_export,0, None),
            ("/File/_Export _As",None,          self.menu_export_as,0,None),
            ("/File/sep2",       None,          None,          0,"<Separator>"),
            ("/File/_Quit",      "<control>Q",  self.menu_quit ,0,  None),
 
            ("/_Edit",          None,           None,           0,  "<Branch>"),
            ("/Edit/_Get _Info","<control>I",   self.menu_get_info,0,None),
            ("/Edit/_File _Metadata",None,   self.menu_file_metadata,0,None),
            ("/Edit/_Create _Index",None,       self.menu_create_index,0,None),
            ("/Edit/sep3",       None,          None,          0,"<Separator>"),
            ("/Edit/_Delete",   "<control>K",     self.menu_delete,0,None),
            ("/Edit/_Create _Resource",None,  self.menu_create_resource,0,None),
            ("/Edit/_Export _Resource",None,  self.menu_export_resource,0,None),
            ("/Edit/_Import _Resource",None,  self.menu_import_resource,0,None),
            ("/Edit/sep4",       None,          None,          0,"<Separator>"),
            ("/Edit/_Cut",   "<control>X",           self.menu_cut,0,None),
            ("/Edit/_Copy",  "<control>C",           self.menu_copy,0,None),
            ("/Edit/_Paste", "<control>P",           self.menu_paste,0,None),

            ("/_Patch",          None,          None,          0, "<Branch>"),
            ("/Patch/_Select _Base",None,       self.menu_select_base,0,None),
            ("/Patch/_Save _Patch","<control>T",  self.menu_save_patch,0,None),
            ("/Patch/_Save _Patch _As",None,    self.menu_save_patch_as,0,None),
            ("/Patch/sep5",      None,          None,          0,"<Separator>"),
            ("/Patch/_Apply",None,              self.menu_apply,0,None),
            ("/Patch/_Check _Compatibility",None,
                 self.menu_check_compatibility,0,None),

            ("/_Tools",          None,           None,         0, "<Branch>"),
            ("/Tools/_Resource _Editor", 
                 "<control>R",self.menu_resource_editor,0,None),
            ("/Tools/_Hex Editor", "<control>H",self.menu_hex_editor,0,None),
            
            ("/_Help",           None,          None,           0, "<Branch>"),
            ("/Help/About",      None,          self.menu_about, 0, None),
        )
        accel = gtk.AccelGroup()
        ifc = gtk.ItemFactory(gtk.MenuBar, "<main>", accel)
        self.window.add_accel_group(accel)
        ifc.create_items(menu_items)
        self.menu_bar = ifc.get_widget("<main>")
        self.mvbox.pack_start(self.menu_bar, False, True, 0)

        # Make the data tree
        self.data_view = gtk.TreeView()
        dc1 = gtk.TreeViewColumn()
        dc1.set_title("Subindex") # Would it be so much to ask for this to be
        # in the constructor...
        dc2 = gtk.TreeViewColumn()
        dc2.set_title("Count")
        dc3 = gtk.TreeViewColumn()
        dc3.set_title("Description")
        
        # Seriously it's like GUI programming is designed to be as clunky
        # and non-functional as possible in the quest for generality
        # Why is there no truly native python gui kit? It's the most popular
        # language in the world now...
        # Aren't we ready to move beyond the state machine model for building
        # GUI stuff???
        # and why are all the RAD tools broken?! They could at least plaster
        # over this cruft...
        c =gtk.CellRendererText();dc1.pack_start(c,True);
        dc1.add_attribute(c,"text",0)
        c =gtk.CellRendererText();dc2.pack_start(c,True);
        dc2.add_attribute(c,"text",1)
        c =gtk.CellRendererText();dc3.pack_start(c,True);
        dc3.add_attribute(c,"text",2)         
        self.data_view.append_column(dc1)
        self.data_view.append_column(dc2)
        self.data_view.append_column(dc3)

        self.temporary_data = gtk.TreeStore(str,str,str)
        self.data_view.set_model(self.temporary_data)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        sw.add(self.data_view)
        self.mvbox.pack_start(sw, True, True, 0)







        self.window.show_all()
    def main(self):
        gtk.main()

    # Callbacks
    def menu_new(self, widget, data=None):
        return None
    def menu_open(self, widget, data=None):
        if self.unsaved and self.warn_unsaved_changes(): return
        chooser = gtk.FileChooserDialog(action=gtk.FILE_CHOOSER_ACTION_OPEN,
                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                           gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            print "Pretending to open", chooser.get_filename()

        chooser.destroy()
        #t = self.temporary_data.append(None, ["131","42 Items", "Image Data"])
        #self.temporary_data.append(t, ["8E31","12 kB","Something"])
        return None
    def menu_save(self, widget, data=None):
        return None
    def menu_save_as(self, widget, data=None):
        return None
    def menu_export(self, widget, data=None):
        return None
    def menu_export_as(self, widget, data=None):
        return None
    def menu_import(self, widget, data=None):
        return None
    def menu_about(self, widget, data=None):
        return None
    def menu_quit(self, widget, data=None):
        print "Quitting"
        if not self.delete_event(widget, None, data): self.destroy(None)
    def menu_get_info(self, widget, data=None):
        return None
    def menu_file_metadata(self, widget, data=None):
        return None
    def menu_create_index(self, widget, data=None):
        return None
    def menu_delete(self, widget, data=None):
        print "Delete"
        return None
    def menu_create_resource(self, widget, data=None):
        return None
    def menu_export_resource(self, widget, data=None):
        return None
    def menu_import_resource(self, widget, data=None):
        return None
    def menu_cut(self, widget, data=None):
        return None
    def menu_copy(self, widget, data=None):
        return None
    def menu_paste(self, widget, data=None):
        return None
    def menu_select_base(self, widget, data=None):
        return None
    def menu_save_patch(self, widget, data=None):
        return None
    def menu_save_patch_as(self, widget, data=None):
        return None
    def menu_apply(self, widget, data=None):
        return None
    def menu_resource_editor(self, widget, data=None):
        return None
    def menu_hex_editor(self, widget, data=None):
        return None
    def menu_check_compatibility(self,widget,data=None):
        return None
    # stub
    def menu_(self, widget, data=None):
        return None

    def destroy(self, widget, data=None):
        gtk.main_quit()
    def delete_event(self, widget, event, data=None):
        if not self.unsaved: return False
        return self.warn_unsaved_changes()

     # helpers
    def warn_unsaved_changes(self):
        dialog = gtk.MessageDialog(self.window, 
            gtk.DIALOG_MODAL , 
            gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
            "This action will lose unsaved changes; are you sure?")
        rv= gtk.RESPONSE_YES != dialog.run()
        dialog.destroy()
        return rv
