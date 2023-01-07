import common as omni
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class OmniWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title='OmniPkg')

        self.set_default_size(800, 500)

        self.search_box = Gtk.Box()
        self.search_entry = Gtk.Entry()
        self.search_button = Gtk.Button(label='Search')
        self.search_button.connect('clicked', self.on_search_button_click)
        self.search_box.pack_start(self.search_entry, False, True, 0)
        self.search_box.pack_start(self.search_button, False, True, 0)

        self.pkg_list_store = Gtk.ListStore(str, str)
        self.pkg_list_view = Gtk.TreeView(model=self.pkg_list_store)
        self.pkg_list_view_selection = self.pkg_list_view.get_selection()
        self.pkg_list_view_selection.connect('changed', self.on_packages_selection_change)

        self.pkg_name_renderer = Gtk.CellRendererText()
        self.pkg_name_column = Gtk.TreeViewColumn('Package', self.pkg_name_renderer, text=0)
        self.pkg_list_view.append_column(self.pkg_name_column)

        self.pkg_manager_renderer = Gtk.CellRendererText()
        self.pkg_manager_column = Gtk.TreeViewColumn('Package Manager', self.pkg_manager_renderer, text=1)
        self.pkg_list_view.append_column(self.pkg_manager_column)

        self.app_install_button = Gtk.Button(label='Install')
        self.app_install_button.connect('clicked', self.on_install_button_click)
        self.app_uninstall_button = Gtk.Button(label='Uninstall')
        self.app_uninstall_button.connect('clicked', self.on_uninstall_button_click)
        self.app_update_button = Gtk.Button(label='Update')
        self.app_update_button.connect('clicked', self.on_update_button_click)
        self.app_info_button_box = Gtk.Box()
        self.app_info_button_box.pack_end(self.app_install_button, False, True, 5)
        self.app_info_button_box.pack_end(self.app_uninstall_button, False, True, 5)
        self.app_info_button_box.pack_end(self.app_update_button, False, True, 5)
        self.app_info_label = Gtk.Label()
        self.app_info_label.set_halign(Gtk.Align.START)
        self.app_info_label.set_valign(Gtk.Align.START)
        self.app_info_label.set_margin_top(15)
        self.app_info_label.set_margin_left(15)
        self.app_info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.app_info_box.pack_start(self.app_info_button_box, False, True, 0)
        self.app_info_box.pack_start(self.app_info_label, True, True, 0)

        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paned.pack1(self.pkg_list_view)
        self.paned.pack2(self.app_info_box)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.pack_start(self.search_box, False, True, 0)
        self.main_box.pack_start(self.paned, True, True, 0)

        self.add(self.main_box)

    def on_packages_selection_change(self, selection):
        model, i = selection.get_selected()
        self.app_info_label.set_text(omni.info_in_pm(model[i][0], omni.pkg_managers[model[i][1]])['info'])

    def on_search_button_click(self, button):
        self.populate_list(omni.search(self.search_entry.get_text()))
    
    def on_install_button_click(self, button):
        model, i = self.pkg_list_view_selection.get_selected()
        omni.install(model[i][0])
    
    def on_uninstall_button_click(self, button):
        model, i = self.pkg_list_view_selection.get_selected()
        omni.uninstall(model[i][0])
    
    def on_update_button_click(self, button):
        model, i = self.pkg_list_view_selection.get_selected()
        omni.update(model[i][0])
    
    def populate_list(self, items):
        self.pkg_list_store.clear()
        for item in items:
            self.pkg_list_store.append([item['package'], item['pm']])

win = OmniWindow()
win.connect('destroy', Gtk.main_quit)
win.show_all()
Gtk.main()