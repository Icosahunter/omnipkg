import omnipkg.common as omni
from omnipkg.ui_mainwindow import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.installButton.clicked.connect(self.install_click)
        self.ui.uninstallButton.clicked.connect(self.uninstall_click)
        self.ui.updateButton.clicked.connect(self.update_click)
        self.ui.searchLineEdit.returnPressed.connect(self.search_enter)
        self.ui.packageListTable.cellClicked.connect(self.package_click)
        self.package_list = []
        self.selected_package = None

    def install_click(self):
        self.run_action('install', self.selected_package)

    def uninstall_click(self):
        self.run_action('uninstall', self.selected_package)

    def update_click(self):
        self.run_action('update', self.selected_package)

    def search_enter(self):
        self.package_list = self.run_action('search', self.ui.searchLineEdit.text())
        self.update_table()

    def update_table(self):
        header_labels = ['name', 'pm', 'summary', 'installed']
        self.ui.packageListTable.setRowCount(len(self.package_list))
        self.ui.packageListTable.setColumnCount(4)
        self.ui.packageListTable.setHorizontalHeaderLabels(header_labels)
        for i in range(len(self.package_list)):
            for j in range(len(header_labels)):
                self.ui.packageListTable.setItem(i, j, QTableWidgetItem(str(self.package_list[i][header_labels[j]])))
    
    def update_details(self):

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
    
    def run_action(self, action, package):
        self.ui.statusbar.showMessage(action + 'ing' + package + '...')
        result = omni.run(action, package)
        self.ui.statusbar.clearMessage()
        return result