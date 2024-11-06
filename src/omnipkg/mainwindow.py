from omnipkg.ui_mainwindow import Ui_MainWindow
import omnipkg.dirs as dirs
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem
from PySide6.QtCore import Signal, QThreadPool, QRunnable, QObject
from PySide6.QtGui import QIcon
from PySide6.QtAsyncio import asyncio
import subprocess
import json
import glob
import os
import sys

class MainWindow(QMainWindow):
    def __init__(self, omnipkg):
        super(MainWindow, self).__init__()
        self.omnipkg = omnipkg
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.installButton.clicked.connect(self.install_click)
        self.ui.uninstallButton.clicked.connect(self.uninstall_click)
        self.ui.updateButton.clicked.connect(self.update_click)
        self.ui.searchLineEdit.returnPressed.connect(self.search_enter)
        self.ui.packageListTable.cellClicked.connect(self.package_click)
        self.ui.searchComboBox.currentTextChanged.connect(self.search_combo_changed)
        self.ui.updateAllButton.clicked.connect(self.update_all_click)
        self.ui.clearPackageIndexesAction.triggered.connect(self.omnipkg.pkg_cache.clear)
        self.ui.clearIconCacheAction.triggered.connect(self.omnipkg.icon_cache.clear)
        self.ui.openConfigAction.triggered.connect(self.open_config)
        self.ui.resetConfigAction.triggered.connect(self.omnipkg.reset_all_config)
        self.package_list = []
        self.selected_package = None
        self.action_queue = []
        self.item_update_queue = []
        self.setWindowIcon(QIcon(str(dirs.installed_dir / 'data/appfiles/omnipkg.png')))

    def open_config(self):
        if sys.platform == 'win32':
            subprocess.run(['start', dirs.config_dir])
        elif sys.platform == 'darwin':
            subprocess.run(['open', dirs.config_dir])
        elif sys.platform == 'linux':
            subprocess.run(['xdg-open', dirs.config_dir])

    def update_all_click(self):
        self.run_action('update-all')

    def search_combo_changed(self, option):
        if option == 'All':
            self.run_action('search', self.ui.searchLineEdit.text())
        elif option == 'Updates':
            self.run_action('updates')
        elif option == 'Installed':
            self.run_action('installed')

    def install_click(self):
        self.run_action('install', self.selected_package['id'], self.selected_package['pm'])

    def uninstall_click(self):
        self.run_action('uninstall', self.selected_package['id'], self.selected_package['pm'])

    def update_click(self):
        self.run_action('update', self.selected_package['id'], self.selected_package['pm'])

    def search_enter(self):
        if self.ui.searchComboBox.currentText() == 'All':
            self.run_action('search', self.ui.searchLineEdit.text())
        elif self.ui.searchComboBox.currentText() == 'Updates':
            self.run_action('updates')
            self.filter_package_list(self.ui.searchLineEdit.text())
        elif self.ui.searchComboBox.currentText() == 'Installed':
            self.run_action('installed')
            self.filter_package_list(self.ui.searchLineEdit.text())

    def filter_package_list(self, query):
        self.package_list = [x for x in self.package_list if query in json.dumps(x, default=str)]
        self.update_table()

    def set_package_list(self, packages):
        self.package_list = packages
        self.update_table()

    def update_table(self):
        self.ui.packageListTable.setRowCount(len(self.package_list))
        self.ui.packageListTable.setColumnCount(len(self.omnipkg.config['columns']))
        self.ui.packageListTable.setHorizontalHeaderLabels(self.omnipkg.config['columns'])
        for i in range(len(self.package_list)):
            for j in range(len(self.omnipkg.config['columns'])):
                item = QTableWidgetItem()
                self.ui.packageListTable.setItem(i, j, item)
                col = self.omnipkg.config['columns'][j]
                if col in self.package_list[i].data or col == 'name':
                    self.set_item(item, col, self.package_list[i][col])
                else:
                    self.queue_item_update(item, col, self.package_list[i])
            self.package_list[i].save()
        self.start_item_updates()

    def start_item_updates(self):
        QThreadPool.globalInstance().start(self.item_update_queue.pop(0))

    def queue_item_update(self, item, field, pkg):
        item_update_task = Task(self.item_update_do_work, item=item, pkg=pkg, field=field)
        item_update_task.taskComplete.connect(self.item_update_complete)
        self.item_update_queue.append(item_update_task)

    def item_update_do_work(self, item, pkg, field):
        return item, field, pkg[field]

    def item_update_complete(self, result):
        self.set_item(*result)
        if len(self.item_update_queue) > 0:
            QThreadPool.globalInstance().start(self.item_update_queue.pop(0))

    def set_item(self, item, field, value):
        if field == 'icon':
            if value is not None:
                item.setIcon(QIcon(str(value)))
        else:
            item.setText(str(value))

    def update_details(self):
        if self.selected_package is not None:
            formatted_details = self.omnipkg.package_details_template.format_map(self.selected_package)
            self.ui.packageDetailsTextBrowser.setMarkdown(formatted_details)

            if self.selected_package['installed']:
                self.ui.installButton.setEnabled(False)
                self.ui.uninstallButton.setEnabled(True)
            else:
                self.ui.installButton.setEnabled(True)
                self.ui.uninstallButton.setEnabled(False)

            if self.selected_package['updatable']:
                self.ui.updateButton.setEnabled(True)
            else:
                self.ui.updateButton.setEnabled(False)

    def package_click(self, row, col):
        self.selected_package = self.package_list[row]
        self.update_details()

    def action_complete(self):
        self.ui.statusbar.clearMessage()
        self.action_queue.pop()
        if len(self.action_queue) > 0:
            self.start_action_task(self.action_queue[-1])
        self.update_details()

    def run_action(self, action, package=None, pm=None):
        omni_action = Task(self.omnipkg.run, command=action, package=package, pm=pm)
        self.action_queue.append(omni_action)
        if len(self.action_queue) == 1:
            self.start_action_task(omni_action)

    def start_action_task(self, omni_action):

        text = omni_action.kwargs['command'] + 'ing'
        if omni_action.kwargs['package'] is not None:
            text += ' ' + omni_action.kwargs['package']
        if omni_action.kwargs['pm'] is not None:
            text += ' from ' + str(omni_action.kwargs['pm'])
        text += '...'

        self.ui.statusbar.showMessage(text)
        omni_action.taskComplete.connect(self.action_complete)

        if omni_action.kwargs['command'] in ['search', 'updates', 'installed']:
            omni_action.taskComplete.connect(self.set_package_list)

        QThreadPool.globalInstance().start(omni_action)

class TaskSignals(QObject):
    taskComplete = Signal(object)

class Task(QRunnable):

    def __init__(self, function, *args, **kwargs):
        super(Task, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = TaskSignals()
        self.taskComplete = self.signals.taskComplete

    def run(self):
        result = self.function(*self.args, **self.kwargs)
        self.taskComplete.emit(result)
