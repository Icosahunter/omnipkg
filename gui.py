import common as omni
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class OmniWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title='OmniPkg')
        self.search_box = Gtk.Box()
        self.search_entry = Gtk.Entry()
        self.search_button = Gtk.Button(label='Search')
        self.search_button.connect('clicked', self.on_search_button_click)
        self.search_box.pack_start(self.search_entry, False, True, 0)
        self.search_box.pack_start(self.search_button, False, True, 0)

        self.packages_list_store = Gtk.ListStore(str)
        self.pkg_list_view = Gtk.TreeView(model=self.packages_list_store)
        self.pkg_list_view.get_selection().connect('changed', self.on_packages_selection_change)

        self.pkg_name_column = Gtk.TreeViewColumn('Package')
        self.pkg_name_renderer = Gtk.CellRendererText()
        self.pkg_name_column.pack_start(self.pkg_name_renderer, True)
        self.pkg_name_column.add_attribute(self.pkg_name_renderer, 'text', 0)
        self.pkg_list_view.append_column(self.pkg_name_column)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.pack_start(self.search_box, False, True, 0)
        self.main_box.pack_start(self.pkg_list_view, True, True, 0)

        self.add(self.main_box)
    
    def on_packages_selection_change(self, selection):
        pass

    def on_search_button_click(self, button):
        self.populate_list(omni.search(self.search_entry.get_text()))
    
    def populate_list(self, items):
        self.packages_list_store.clear()
        for item in items:
            self.packages_list_store.append([item])
    

win = OmniWindow()
win.show_all()
Gtk.main()