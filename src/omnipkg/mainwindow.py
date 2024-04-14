from omnipkg.ui_mainwindow import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem
from PySide6.QtCore import Signal, QThreadPool, QRunnable, QObject
from PySide6.QtGui import QIcon

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
        self.package_list = []
        self.selected_package = None
        self.action_queue = []

    def install_click(self):
        self.run_action('install', self.selected_package['id'], self.selected_package['pm'])

    def uninstall_click(self):
        self.run_action('uninstall', self.selected_package['id'], self.selected_package['pm'])

    def update_click(self):
        self.run_action('update', self.selected_package['id'], self.selected_package['pm'])

    def search_enter(self):
        self.run_action('search', self.ui.searchLineEdit.text())
    
    def set_package_list(self, packages):
        self.package_list = packages
        self.update_table()

    def update_table(self):
        header_labels = ['icon', 'name', 'id', 'pm', 'summary', 'installed']
        self.ui.packageListTable.setRowCount(len(self.package_list))
        self.ui.packageListTable.setColumnCount(4)
        self.ui.packageListTable.setHorizontalHeaderLabels(header_labels)
        for i in range(len(self.package_list)):
            for j in range(len(header_labels)):
                item = QTableWidgetItem()
                if header_labels[j] == 'icon':
                    icon = self.omnipkg.get_icon(self.package_list[i])
                    if icon is not None:
                        item.setIcon(QIcon(str(icon)))
                else:
                    text = str(self.package_list[i][header_labels[j]])
                    item.setText(text)
                self.ui.packageListTable.setItem(i, j, item)
    
    def update_details(self):
        if self.selected_package is not None:
            self.ui.packageNameLabel.setText(self.selected_package['name'])
            self.ui.packageDescriptionLabel.setText(self.selected_package['summary'])

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
        omni_action = Task(self.omnipkg.run, action, package, pm)
        self.action_queue.append(omni_action)
        if len(self.action_queue) == 1:
            self.start_action_task(omni_action)
    
    def start_action_task(self, omni_action):

        text = omni_action.args[0] + 'ing'
        if omni_action.args[1] is not None:
            text += ' ' + omni_action.args[1]
        if omni_action.args[2] is not None:
            text += ' from ' + omni_action.args[2]
        text += '...'

        self.ui.statusbar.showMessage(text)
        omni_action.taskComplete.connect(self.action_complete)
        if omni_action.args[0] == 'search':
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