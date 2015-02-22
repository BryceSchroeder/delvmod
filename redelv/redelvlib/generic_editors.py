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
#
# "Cythera" and "Delver" are trademarks of either Glenn Andreas or 
# Ambrosia Software, Inc. 
import csv
import gtk
import editors
import delv.store
class HexEditor(editors.Editor):
    name = "Unimplemented (Hex Editor)"

class TileNameListEditor(editors.Editor):
    name = "Tile Name List Editor"
    default_size = 512,400
    def editor_setup(self):
        self.load()
    def gui_setup(self):
        pbox = gtk.VBox(False,0)
        self.set_default_size(*self.default_size)
        menu_items = (
            ("/File/Import CSV", "<control>I", self.file_import, 0, None),
            ("/File/Export CSV", "<control>E", self.file_export, 0, None),
            ("/File/Save Resource", "<control>S", self.file_save, 0, None),
            ("/File/Revert", None, self.load, 0, None),
            #("/Edit/Cut", "<control>X", self.edit_cut, 0, None),
            #("/Edit/Copy", "<control>C", self.edit_copy, 0, None),
            #("/Edit/Paste","<control>V", self.edit_paste, 0, None),
            ("/Edit/Delete Entry", None, self.edit_delete, 0, None),
            ("/Edit/Insert New Entry", None, self.edit_insert, 0, None),
            ("/Edit/Clear", None, self.edit_clear, 0, None),)
        accel = gtk.AccelGroup()
        ifc = gtk.ItemFactory(gtk.MenuBar, "<main>", accel)
        self.add_accel_group(accel)
        ifc.create_items(menu_items)
        self.menu_bar = ifc.get_widget("<main>")
        pbox.pack_start(self.menu_bar, False, True, 0)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        self.data_view = gtk.TreeView()
        dc = gtk.TreeViewColumn()
        dc.set_title("Tile Index Cutoff")
        c = gtk.CellRendererText()
        c.set_property('editable',True)
        c.connect('edited', self.editor_callback_cutoff)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",0)
        self.data_view.append_column(dc)
        
        dc = gtk.TreeViewColumn()
        dc.set_title("Tile Name Code")
        c = gtk.CellRendererText() 
        c.set_property('editable',True)
        c.connect('edited', self.editor_callback_namecode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",1)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Singular")
        c = gtk.CellRendererText() 
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",2)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Plural")
        c = gtk.CellRendererText() 
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",3)
        self.data_view.append_column(dc)


        self.tree_data = gtk.ListStore(str,str,str,str,int)
        self.data_view.set_model(self.tree_data)

        sw.add(self.data_view)
        pbox.pack_start(sw, True, True, 5)
        self.add(pbox)
    def editor_callback_cutoff(self, renderer, path, new_text):
        try:
            ival = int(new_text.replace('0x','').replace('$',''), 16)
        except:
            return
        itr = self.tree_data.get_iter(path)
        self.tree_data.set_value(itr, 0, "0x%04X"%ival)
        self.tree_data.set_value(itr, 4, ival)

        self.tree_data.set_sort_column_id(4, gtk.SORT_ASCENDING)
        self.unsaved = True
    def editor_callback_namecode(self, renderer, path, new_text):
        itr = self.tree_data.get_iter(path)
        self.tree_data.set_value(itr, 1, new_text)
        self.tree_data.set_value(itr,2,self.tilenames.namecode(new_text,False))
        if '\\' in new_text:
            self.tree_data.set_value(itr, 3, self.tilenames.namecode(
                new_text, True))
        else:
            self.tree_data.set_value(itr, 3, '')
        
        self.unsaved = True
    def load(self, *argv):
        self.tilenames = delv.store.TileNameList(self.res)
        for cutoff, name in self.tilenames.items():
            self.tree_data.append([
                "0x%04X"%cutoff, name, self.tilenames.get_name(cutoff,False),
                self.tilenames.get_name(cutoff,True) if '\\' in name else '', 
                cutoff])
    def file_import(self, *argv):
        path = "<undefined>"
        try:
            path = self.ask_open_path()
            if not path: return
            csvfile = csv.reader(open(path,'rb'))
        except Exception,e:
            self.error_message("Couldn't open '%s': %s"%(path,
                repr(e)))
            return
        self.tree_data = gtk.ListStore(str,str,str,str,int)
        self.data_view.set_model(self.tree_data)        
        for cutoff, name in csvfile:
            cutoff = int(cutoff[2:],16)
            self.tree_data.append([
                "0x%04X"%cutoff, name, self.tilenames.namecode(name,False),
                self.tilenames.namecode(name,True) if '\\' in name else '', 
                cutoff])
        self.unsaved = True

    def file_export(self, *argv):
        path = self.ask_save_path(default = "Data%04X.csv"%self.res.resid) 
        if not path: return
        try:
            csvfile = csv.writer(open(path,'wb'))
        except Exception,e:
            self.error_message("Couldn't open '%s': %s"%(path,
                repr(e)))
            return
        itr = self.tree_data.get_iter_first()
        while itr:
            csvfile.writerow([
                self.tree_data.get_value(itr, n) for n in xrange(2)])
            itr = self.tree_data.iter_next(itr) #barbaric... what is this C++
        
    def file_save(self, *argv):
        self.tilenames.empty()
        itr = self.tree_data.get_iter_first()
        while itr:
            self.tilenames.append(self.tree_data.get_value(itr, 4),
                                  self.tree_data.get_value(itr, 1))
            itr = self.tree_data.iter_next(itr)
        self.res.set_data(self.tilenames.get_data())
        self.unsaved = False
        self.redelv.unsaved = True
    def edit_cut(self, *argv):
        pass
    def edit_copy(self, *argv):
        pass
    def edit_paste(self, *argv):
        pass
    def edit_clear(self, *argv):
        self.tree_data = gtk.ListStore(str,str,str,str,int)
        self.data_view.set_model(self.tree_data)  
        self.unsaved = True
    def edit_delete(self, *argv):
        tm,row = self.data_view.get_selection().get_selected_rows()
        row = row[-1] if row else '0'
        tm.remove(tm.get_iter(row))
        self.unsaved = True
    def edit_insert(self, *argv):
        tm,row = self.data_view.get_selection().get_selected_rows()
        row = row[-1] if row else '0'
        
        itr = tm.get_iter(row)
        nidx = tm.get_value(itr,4)+1
        tm.insert_after(itr, ["0x%04X"%nidx, "Nothing", "Nothing","",nidx])
        self.unsaved = True
