#!/usr/bin/env python
# Copyright 2016 Bryce Schroeder, www.bryce.pw, bryce.schroeder@gmail.com
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
import delv.ddasm
import gtk
import editors
class ScheduleEditor(editors.Editor):
    name = "Schedule Editor"
    default_size = 620,400
    def editor_setup(self):
        self.library = self.redelv.get_library()
        self.load()
    def gui_setup(self):
        pbox = gtk.VBox(False,0)
        self.set_default_size(*self.default_size)
        menu_items = (
            #("/File/Import CSV", "<control>I", self.file_import, 0, None),
            #("/File/Export CSV", "<control>E", self.file_export, 0, None),
            ("/File/Save Resource", "<control>S", self.file_save, 0, None),
            ("/File/Revert", None, self.load, 0, None),
            ("/Edit/Cut", "<control>X", self.edit_cut, 0, None),
            ("/Edit/Copy", "<control>C", self.edit_copy, 0, None),
            ("/Edit/Paste","<control>V", self.edit_paste, 0, None),
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
        dc.set_title("Character ID")
        c = gtk.CellRendererText()
        c.set_property('editable',False)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",0)
        self.data_view.append_column(dc)
        
        dc = gtk.TreeViewColumn()
        dc.set_title("Name")
        c = gtk.CellRendererText()
        c.set_property('editable',False)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",1)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Hour")
        c = gtk.CellRendererText()
        c.set_property('editable',True)
        c.connect('edited', self.editor_cb_hour)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",2)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Mode")
        c = gtk.CellRendererText()
        c.set_property('editable',True)
        c.connect('edited', self.editor_cb_mode)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",3)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Data")
        c = gtk.CellRendererText()
        c.set_property('editable',True)
        c.connect('edited', self.editor_cb_data)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",4)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Level")
        c = gtk.CellRendererText()
        c.set_property('editable',True)
        c.connect('edited', self.editor_cb_level)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",5)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Level Name")
        c = gtk.CellRendererText()
        c.set_property('editable',False)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",6)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("X")
        c = gtk.CellRendererText()
        c.set_property('editable',True)
        c.connect('edited', self.editor_cb_x)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",7)
        self.data_view.append_column(dc)

        dc = gtk.TreeViewColumn()
        dc.set_title("Y")
        c = gtk.CellRendererText()
        c.set_property('editable',True)
        c.connect('edited', self.editor_cb_y)
        dc.pack_start(c,True)
        dc.add_attribute(c,"text",8)
        self.data_view.append_column(dc)

        self.tree_data = gtk.TreeStore(str,str, str,str,str,str,str,str,str)
        self.data_view.set_model(self.tree_data)

        sw.add(self.data_view)
        pbox.pack_start(sw, True, True, 5)
        self.add(pbox)
    def load(self, *argv):
        self.schedules = delv.schedule.ScheduleList(self.res)
        self.schedules.check_out()
        names = delv.ddasm.DArray(self.library.get_resource(0x0201).as_file())
        names.load(None, True)
        self.names = names
        self.gui_tree_rows = {}
        for charid,schedule in enumerate(self.schedules):
            t=self.tree_data.append(None, [
                "0x%02X"%charid, names[charid], '','','','','','',''])
            self.gui_tree_rows[charid]=t
            for hour, mode, scripting, level, x, y in schedule:
                self.tree_data.append(t, 
                    ["0x%02X"%charid, names[charid], "%2d:00"%hour,
                     '0x%02X'%mode,'0x%04X'%scripting,'0x%02X'%level,
                     delv.hints._RES_HINTS.get(0x8000|level,'???'),
                     '%d'%x,'%d'%y])

    def file_save(self, *argv):
        self.schedules.empty()
        
        schedules = []
        itr = self.tree_data.get_iter_first()
        while itr:
            chd = self.tree_data.iter_children(itr)
            entries = []
            while chd: 
                entries.append([
                   int(self.tree_data.get_value(chd,2).replace(':00','')),
                   int(self.tree_data.get_value(chd,3).replace('0x',''),16),
                   int(self.tree_data.get_value(chd,4).replace('0x',''),16),
                   int(self.tree_data.get_value(chd,5).replace('0x',''),16),
                   int(self.tree_data.get_value(chd,7)),
                   int(self.tree_data.get_value(chd,8)) ])
                chd = self.tree_data.iter_next(chd)
            schedules.append(entries)
            itr = self.tree_data.iter_next(itr)
        self.schedules.schedules=schedules # I laughed.
        self.schedules.write_to_bfile()
        #newdata = self.schedules.get_data()
        #print "set schedules", len(self.schedules.schedules)
        #print repr(self.res), len(newdata)
        #self.res.set_data(newdata)
        self.set_saved()
        self.redelv.set_unsaved()
    def edit_cut(self, *argv):
        self.edit_copy()
        self.edit_delete()
        self.set_unsaved()
    def edit_clear(self, *argv):
        self.tree_data = gtk.TreeStore(str,str, str,str,str,str,str,str,str)
        self.data_view.set_model(self.tree_data)  
        self.set_unsaved()
    def edit_copy(self, *argv):
        tm,row = self.data_view.get_selection().get_selected_rows()
        row = row[-1] if row else '0'
        itr = tm.get_iter(row)
        if tm.get_value(itr,2):
            gtk.clipboard_get().set_text(
                ','.join([tm.get_value(itr,n) for n in xrange(9)]))
    def edit_paste(self, *argv):
        tm,row = self.data_view.get_selection().get_selected_rows()
        row = row[-1] if row else '0'
        itr = tm.get_iter(row)
        data = gtk.clipboard_get().wait_for_text().split(',')
        if tm.get_value(itr,2):
            for n,v in enumerate(data[2:],2):
                self.tree_data.set_value(itr, n, v)
        else: 
            #append
            chrid = tm.get_value(itr,0)
            chrnm = tm.get_value(itr,1)
            tm.insert_after(itr, None, [
             chrid,chrnm]+data[2:])
        self.set_unsaved()
    def edit_delete(self, *argv):
        tm,row = self.data_view.get_selection().get_selected_rows()
        row = row[-1] if row else '0'
        itr = tm.get_iter(row)
        if tm.get_value(itr,2):
            tm.remove(itr)
            self.set_unsaved()
    def edit_insert(self, *argv):
        tm,row = self.data_view.get_selection().get_selected_rows()
        row = row[-1] if row else '0'
        
        itr = tm.get_iter(row)
        chrid = tm.get_value(itr,0)
        chrnm = tm.get_value(itr,1)
        #print '**', repr(itr), str(itr), chrid, chrnm
        if tm.get_value(itr,2):
            p=None
            s=itr
        else:
            p=itr
            s=None

        tm.insert_after(p, s, [
             chrid,chrnm,
             '0:00', '0x00', '0x0000', '0x01', 'Cythera', '0', '0'])
        self.set_unsaved()
    def editor_cb_hour(self, renderer, path, new_text):
        itr = self.tree_data.get_iter(path)
        hour = int(new_text[:new_text.find(':')])
        self.tree_data.set_value(itr, 2, '%2d:00'%hour)
        self.set_unsaved()
        
    def editor_cb_mode(self, renderer, path, new_text):
        mode=int(new_text.replace('0x',''),16)
        itr = self.tree_data.get_iter(path)
        self.tree_data.set_value(itr, 3, '0x%02X'%mode)
        self.set_unsaved()
    def editor_cb_data(self, renderer, path, new_text):
        self.set_unsaved()
        data=int(new_text.replace('0x',''),16)
        itr = self.tree_data.get_iter(path)
        self.tree_data.set_value(itr, 4, '0x%04X'%data)
    def editor_cb_level(self, renderer, path, new_text):
        level=int(new_text.replace('0x',''),16)
        itr = self.tree_data.get_iter(path)
        self.tree_data.set_value(itr, 5, '0x%02X'%level)
        # load level name
        self.tree_data.set_value(itr, 6, 
            delv.hints._RES_HINTS.get(0x8000|level,'???'))
        self.set_unsaved()


    def editor_cb_x(self, renderer, path, new_text):
        self.set_unsaved()
        itr = self.tree_data.get_iter(path)
        x = int(new_text)
        self.tree_data.set_value(itr, 7, '%d'%x)

    def editor_cb_y(self, renderer, path, new_text):
        self.set_unsaved()
        itr = self.tree_data.get_iter(path)
        y = int(new_text)
        self.tree_data.set_value(itr, 8, '%d'%y)

