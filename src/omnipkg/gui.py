from pathlib import Path
import time
import threading
from PySide6.QtWidgets import QApplication, QMainWindow
from omnipkg.mainwindow import MainWindow
from omnipkg.omnipkg import Omnipkg
import sys

def run():
    omnipkg = Omnipkg()
    omnipkg.init()
    app = QApplication(sys.argv)
    window = MainWindow(omnipkg)
    window.show()
    app.exec()

if __name__ == '__main__':
    run()