import pygtk
pygtk.require('2.0')
import gtk, os, sys
import images

class Receiver(gtk.Window):
    pass

class FileMetadata(Receiver):
    def __init__(self,redelv, *args,**argk):
        gtk.Window.__init__(self, *args, **argk)
        self.redelv = redelv
        self.set_title('File Metadata for "%s"'%redelv.opened_file)
        self.set_default_size(320,128)
        self.set_icon(gtk.gdk.pixbuf_new_from_file(images.inspect_path))
        self.redelv.filechange.append(self)
        self.connect("delete_event", (lambda *x: self.hide() or True))

	pbox = gtk.VBox(False,2)
        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Scenario Title:"),False,True,0)
        self.scenario_title = gtk.Entry(255)
        trow.pack_start(self.scenario_title, True,True,0)
        pbox.pack_start(trow,False,True,0)

        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Unknown 0x40:"),False,True,0)
        self.unknown_40 = gtk.Entry(4)
        self.unknown_40.set_editable(False)
        trow.pack_start(self.unknown_40,True,True,0)
        trow.pack_start(gtk.Label("Unknown 0x42:"),False,True,0)
        self.unknown_42 = gtk.Entry(4)
        self.unknown_42.set_editable(False)
        trow.pack_start(self.unknown_42,True,True,0)
        trow.pack_start(gtk.Label("Unknown 0x48:"),False,True,0)
        self.unknown_48 = gtk.Entry(4)
        self.unknown_48.set_editable(False)
        trow.pack_start(self.unknown_48,True,True,0)
        pbox.pack_start(trow,False,True,0)

        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Master Index Offset:"),False,True,0)
        self.master_index_offset = gtk.Entry(10)
        self.master_index_offset.set_editable(False)
        trow.pack_start(self.master_index_offset,True,True,0)
        trow.pack_start(gtk.Label("Master Index Length:"),False,True,0)
        self.master_index_length = gtk.Entry(10)
        self.master_index_length.set_editable(False)
        trow.pack_start(self.master_index_length,True,True,0)
        pbox.pack_start(trow,False,True,0)

        trow = gtk.HBox(False,0)
        trow.pack_start(gtk.Label("Source:"),False,True,0)
        self.source_string = gtk.Entry()
        self.source_string.set_editable(False)
        trow.pack_start(self.source_string,True,True,0)
        pbox.pack_start(trow,False,True,0)
 	self.add(pbox)

        self.scenario_title.connect("changed", self.edit_scenario_title)

        self.signal_filechange(None)
    def edit_scenario_title(self,w,data=None):
        newtitle = self.scenario_title.get_text()
        self.redelv.unsaved = newtitle !=  self.redelv.archive.scenario_title
        self.redelv.archive.scenario_title = newtitle

    def signal_filechange(self, d=None):
        if not self.redelv.archive:
            for box in [self.scenario_title,self.unknown_40,self.unknown_42,
                        self.unknown_48,self.master_index_length, 
                        self.master_index_offset]: 
                box.set_text("")
                box.set_editable(False)
            self.source_string.set_text("[No File Opened]")
        else:
            for box in [self.scenario_title]:
                box.set_editable(True)
            self.scenario_title.set_text(self.redelv.archive.scenario_title)
            self.unknown_40.set_text("0x%02X"%self.redelv.archive.unknown_40)
            self.unknown_42.set_text("0x%02X"%self.redelv.archive.unknown_42)
            self.unknown_48.set_text("0x%02X"%self.redelv.archive.unknown_48)
            self.master_index_offset.set_text(
                "0x%08X"%self.redelv.archive.master_index_offset)
            self.master_index_length.set_text(
                "0x%08X"%self.redelv.archive.master_index_length)
            self.source_string.set_text(self.redelv.archive.source_string)

