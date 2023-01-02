import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class OmniWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title='OmniPkg')
        search_box = Gtk.Box()
        search_entry = Gtk.Entry()
        search_button = Gtk.Button(label='Search')
        search_box.pack_start(search_entry, False, True, 0)
        search_box.pack_start(search_button, False, True, 0)

        self.packages = Gtk.ListStore()
        pkg_list_view = Gtk.TreeView(model=self.packages)
        pkg_list_view.get_selection().connect('changed', self.on_packages_selection_change)

        pkg_name_column = Gtk.TreeViewColumn('Package')
        pkg_name_renderer = Gtk.CellRendererText()
        pkg_name_column.pack_start(pkg_name_renderer, True)
        pkg_name_column.add_attribute(pkg_name_renderer, 'text', 0)
        pkg_list_view.append_column(pkg_name_column)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.pack_start(search_box, False, True, 0)
        main_box.pack_start(pkg_list_view, True, True, 0)

        self.add(main_box)
    
    def on_packages_selection_change(selection):
        pass
    


win = OmniWindow()
win.show_all()
Gtk.main()