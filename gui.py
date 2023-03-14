import common as omni
import gi
import asyncio
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject, Pango

class OmniWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title='OmniPkg')

        self.pause_selection_updating = False
        self.gio_async = GioAsyncHandler()
        omni.load_cache()
        self.update_cache()

        self.set_default_size(1000, 700)

        self.top_bar_box = Gtk.Box()

        self.search_box = Gtk.Box()
        self.search_box.get_style_context().add_class("linked")
        self.search_entry = Gtk.Entry()
        self.search_entry.connect('activate', self.on_search_entry_activate)
        self.search_term = ''
        self.search_button = Gtk.Button(label='Search')
        self.search_button.connect('clicked', self.on_search_button_click)
        self.search_box.pack_start(self.search_entry, False, True, 0)
        self.search_box.pack_start(self.search_button, False, True, 0)
        self.search_button.set_margin_end(10)

        self.search_all_button = Gtk.RadioButton.new_with_label_from_widget(None, 'All')
        self.search_all_button.connect('toggled', self.on_search_radio_button_toggle, 'all')
        self.search_updatable_button = Gtk.RadioButton.new_with_label_from_widget(self.search_all_button, 'Updatable')
        self.search_updatable_button.connect('toggled', self.on_search_radio_button_toggle, 'updatable')
        self.search_installed_button = Gtk.RadioButton.new_with_label_from_widget(self.search_all_button, 'Installed')
        self.search_installed_button.connect('toggled', self.on_search_radio_button_toggle, 'installed')
        self.search_installed_button.set_margin_end(10)
        self.search_mode = 'all'

        self.search_update_all_button = Gtk.Button(label='Update All')
        self.search_update_all_button.connect('clicked', self.on_update_all_button_click)

        self.top_bar_box.pack_start(self.search_box, False, True, 0)
        self.top_bar_box.pack_start(self.search_all_button, False, True, 0)
        self.top_bar_box.pack_start(self.search_updatable_button, False, True, 0)
        self.top_bar_box.pack_start(self.search_installed_button, False, True, 0)
        self.top_bar_box.pack_start(self.search_update_all_button, False, True, 0)

        self.pkg_list_store = Gtk.ListStore(str, str, str, str)
        self.search_filter = self.pkg_list_store.filter_new()
        self.search_filter.set_visible_func(self.search_filter_func)
        self.pkg_list_view = Gtk.TreeView(model=self.search_filter)
        self.pkg_list_view_selection = self.pkg_list_view.get_selection()
        self.pkg_list_view_selection.connect('changed', self.on_packages_selection_change)
        self.pkg_list_scrolled_window = Gtk.ScrolledWindow()
        self.pkg_list_scrolled_window.add(self.pkg_list_view)
        self.pkg_list_scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.pkg_name_renderer = Gtk.CellRendererText()
        self.pkg_name_column = Gtk.TreeViewColumn('Package', self.pkg_name_renderer, text=2)
        self.pkg_name_column.set_resizable(True)
        self.pkg_list_view.append_column(self.pkg_name_column)

        self.pkg_manager_renderer = Gtk.CellRendererText()
        self.pkg_manager_column = Gtk.TreeViewColumn('Package Manager', self.pkg_manager_renderer, text=1)
        self.pkg_manager_column.set_resizable(True)
        self.pkg_list_view.append_column(self.pkg_manager_column)

        self.pkg_summary_renderer = Gtk.CellRendererText()
        self.pkg_summary_column = Gtk.TreeViewColumn('Summary', self.pkg_summary_renderer, text=3)
        self.pkg_summary_column.set_resizable(True)
        self.pkg_list_view.append_column(self.pkg_summary_column)

        self.app_install_button = Gtk.Button(label='Install')
        self.app_install_button.connect('clicked', self.on_install_button_click)
        self.app_uninstall_button = Gtk.Button(label='Uninstall')
        self.app_uninstall_button.connect('clicked', self.on_uninstall_button_click)
        self.app_update_button = Gtk.Button(label='Update')
        self.app_update_button.connect('clicked', self.on_update_button_click)
        self.app_info_button_box = Gtk.Box()
        self.app_info_button_box.set_margin_top(10)
        self.app_info_button_box.pack_end(self.app_install_button, False, True, 5)
        self.app_info_button_box.pack_end(self.app_uninstall_button, False, True, 5)
        self.app_info_button_box.pack_end(self.app_update_button, False, True, 5)
        self.app_info_title = Gtk.Label()
        self.app_info_label = Gtk.Label()
        self.app_info_label.set_line_wrap(True)
        self.app_info_label.set_halign(Gtk.Align.START)
        self.app_info_label.set_valign(Gtk.Align.START)
        self.app_info_label.set_margin_top(15)
        self.app_info_label.set_margin_start(15)
        self.app_scrolled_window = Gtk.ScrolledWindow()
        self.app_scrolled_window.add(self.app_info_label)
        self.app_scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.app_info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.app_info_box.pack_start(self.app_info_button_box, False, True, 0)
        self.app_info_box.pack_start(self.app_info_title, False, True, 0)
        self.app_info_box.pack_start(self.app_scrolled_window, True, True, 0)
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paned.pack1(self.pkg_list_scrolled_window, True, True)
        self.paned.pack2(self.app_info_box, True, True)
        self.paned.set_position(self.get_default_size().width//2)

        self.stat_bar_spinner = Gtk.Spinner()
        self.stat_bar_label = Gtk.Label()
        self.stat_bar_box = Gtk.Box()
        self.stat_bar_box.set_margin_top(5)
        self.stat_bar_box.set_margin_bottom(5)
        self.stat_bar_box.set_margin_start(5)
        self.stat_bar_box.set_margin_end(5)
        self.stat_bar_box.pack_start(self.stat_bar_spinner, False, True, 0)
        self.stat_bar_box.pack_start(self.stat_bar_label, False, True, 0)

        self.main_box_separator = Gtk.Separator()
        self.main_box_separator2 = Gtk.Separator()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.pack_start(self.top_bar_box, False, True, 0)
        self.main_box.pack_start(self.main_box_separator, False, True, 0)
        self.main_box.pack_start(self.paned, True, True, 0)
        self.main_box.pack_start(self.main_box_separator2, False, True, 0)
        self.main_box.pack_start(self.stat_bar_box, False, True, 0)

        self.add(self.main_box)
    
    def update_cache(self):
        self.gio_async.run_async(omni.update_cache, [], None)

    def on_window_show(self):
        self.app_install_button.hide()
        self.app_uninstall_button.hide()
        self.app_update_button.hide()

    def on_packages_selection_change(self, selection):
        model, i = selection.get_selected()

        if (not self.pause_selection_updating
            and model is not None 
            and i is not None
            and model[i] is not None):

            package = model[i][0]
            pm = model[i][1]
            self.set_info_box(package, pm)
        else:
            self.clear_info()

    def set_info_box(self, package, pm):
        self.stat_bar_start_task('Getting package info...')
        self.gio_async.run_async(omni.info, [package, pm], self.set_info_box_callback)
        self.gio_async.run_async(omni.is_installed, [package, pm], self.set_install_button_callback)
        self.gio_async.run_async(omni.is_updatable, [package, pm], self.set_update_button_callback)
    
    def set_info_box_callback(self,result):
        if len(result) > 0:
            self.app_info_title.set_markup('<span font_weight="bold" size="large">' + result[0]['name'] + '</span>')
            self.app_info_label.set_text(result[0]['info'])
            self.stat_bar_end_task()
        else:
            self.app_info_title.set_text('')
            self.app_info_label.set_text('')
            self.stat_bar_end_task()
    
    def clear_info(self):
        self.app_info_title.set_text('')
        self.app_info_label.set_text('')
        self.stat_bar_end_task()
        self.app_update_button.hide()
        self.app_install_button.hide()
        self.app_uninstall_button.hide()
    
    def set_update_button_callback(self, result):
        if result:
            self.app_update_button.show()
        else:
            self.app_update_button.hide()

    def set_install_button_callback(self, result):
        if result:
            self.app_install_button.hide()
            self.app_uninstall_button.show()
        else:
            self.app_install_button.show()
            self.app_uninstall_button.hide()

    def on_search_button_click(self, button):
        self.search_term = self.search_entry.get_text()
        self.update_list()

    def on_search_entry_activate(self, entry):
        self.search_term = entry.get_text()
        self.update_list()
    
    def on_install_button_click(self, button):
        model, i = self.pkg_list_view_selection.get_selected()
        self.gio_async.run_async(omni.install, model[i], None)
        self.update_cache()
    
    def on_uninstall_button_click(self, button):
        model, i = self.pkg_list_view_selection.get_selected()
        self.gio_async.run_async(omni.uninstall, model[i], None)
        self.update_cache()
    
    def on_update_button_click(self, button):
        model, i = self.pkg_list_view_selection.get_selected()
        self.gio_async.run_async(omni.update, model[i], None)
        self.update_cache()
    
    def on_update_all_button_click(self, button):
        self.gio_async.run_async(omni.update_all, None, None)
        self.update_cache()

    def on_search_radio_button_toggle(self, button, name):
        if button.get_active():
            self.search_mode = name
            self.update_list()

    def update_list(self):
        match self.search_mode:
            case 'all':
                if self.search_term.isspace() or self.search_term == '':
                    self.clear_list()
                else:
                    self.stat_bar_start_task('Fetching packages matching search...')
                    self.gio_async.run_async(omni.search, [self.search_term], self.populate_list_callback)
            case 'updatable':
                self.stat_bar_start_task('Fetching updatable packages matching search...')
                self.gio_async.run_async(omni.updatable, [], self.populate_list_callback)
            case 'installed':
                self.stat_bar_start_task('Fetching installed packages matching search...')
                self.gio_async.run_async(omni.installed, [], self.populate_list_callback)

    def populate_list_callback(self, result):
        self.stat_bar_end_task()
        self.populate_list(result)
        self.search_filter.refilter()

    def clear_list(self):
        self.pause_selection_updating = True
        self.pkg_list_store.clear()
        self.pause_selection_updating = False

    def populate_list(self, items):
        self.clear_list()
        for item in items:
            self.pkg_list_store.append([item['id'], item['pm'], item['name'], truncate_text(item['summary'], 40)])
    
    def stat_bar_start_task(self, task_str):
        self.stat_bar_spinner.start()
        self.stat_bar_label.set_text(task_str)
    
    def stat_bar_end_task(self):
        self.stat_bar_spinner.stop()
        self.stat_bar_label.set_text('')

    def search_filter_func(self, model, iter, data):
        return self.search_mode == 'all' or self.search_term.isspace() or self.search_term in model[iter][0]

class GioAsyncHandler(GObject.Object):

    def __init__(self):
        super().__init__()
        self.workers = []
    
    def run_async(self, func, args, callback):
        worker = GioAsyncWorker()
        self.workers.append(worker)
        worker.run_async(func, args, callback, self._callback)
    
    def _callback(self, source, result, data):
        res = None
        if Gio.Task.is_valid(result, source):
            res = result.propagate_value().value
        if source.callback is not None:
            source.callback(res)
        self.workers.remove(source)

class GioAsyncWorker(GObject.Object):

    def __init__(self):
        super().__init__()
        self.func = None
        self.args = None
        self.callback = None

    def run_async(self, func, args, callback, _callback):
        self.func = func
        self.args = args
        self.callback = callback
        task = Gio.Task.new(self, None, _callback, None)
        task.set_task_data(None, None)
        task.run_in_thread(self._async_thread_func)
    
    def _async_thread_func(self, task, source, data, cancellable):
        result = self.func(*self.args)
        task.return_value(result)

def truncate_text(text, size):
    if len(text) > size:
        return text[0:size-3] + '...'
    else:
        return text

win = OmniWindow()
win.connect('destroy', Gtk.main_quit)
win.show_all()
win.on_window_show()
Gtk.main()