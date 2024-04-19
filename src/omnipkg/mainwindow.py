from omnipkg.ui_mainwindow import Ui_MainWindow
import omnipkg.dirs as dirs
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem
from PySide6.QtCore import Signal, QThreadPool, QRunnable, QObject
from PySide6.QtGui import QIcon
import json
import glob
import os

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
        self.ui.clearPackageIndexesAction.triggered.connect(self.omnipkg.clear_package_indexes)
        self.ui.clearIconCacheAction.triggered.connect(self.omnipkg.clear_icon_cache)
        self.ui.indexPackagesAction.triggered.connect(self.index_packages)
        self.package_list = []
        self.selected_package = None
        self.action_queue = []
        self.load_package_details_template()

    def update_all_click():
        self.run_action('update-all')

    def load_package_details_template(self):
        details_template_path = dirs.installed_dir / 'data/package-details-template.md'
        if (dirs.config_dir / '/package-details-template.md').exists():
            details_template_path = dirs.config_dir / 'data/package-details-template.md'
        with open(details_template_path, 'r') as f:
            self.package_details_template = f.read()

    def search_combo_changed(self, option):
        if option == 'All':
            self.run_action('search', self.ui.searchLineEdit.text())
        elif option == 'Updates':
            self.run_action('updatable')
        elif option == 'Installed':
            self.run_action('installed')
    
    def index_packages(self):
        self.omnipkg.index_packages()

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
            self.run_action('updatable')
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
        header_labels = ['icon', 'name', 'id', 'pm', 'summary', 'installed']
        self.ui.packageListTable.setRowCount(len(self.package_list))
        self.ui.packageListTable.setColumnCount(len(header_labels))
        self.ui.packageListTable.setHorizontalHeaderLabels(header_labels)
        for i in range(len(self.package_list)):
            for j in range(len(header_labels)):
                item = QTableWidgetItem()
                if header_labels[j] == 'icon':
                    icon = self.package_list[i][header_labels[j]]
                    if icon is not None:
                        item.setIcon(QIcon(str(icon)))
                else:
                    text = str(self.package_list[i][header_labels[j]])
                    item.setText(text)
                self.ui.packageListTable.setItem(i, j, item)
    
    def update_details(self):
        if self.selected_package is not None:
            formatted_details = self.package_details_template.format_map(self.selected_package)
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
            text += ' from ' + omni_action.kwargs['pm']
        text += '...'

        self.ui.statusbar.showMessage(text)
        omni_action.taskComplete.connect(self.action_complete)

        if omni_action.kwargs['command'] in ['search', 'updatable', 'installed']:
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