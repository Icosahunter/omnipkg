import omnipkg.common as omni
from pathlib import Path
import time
import threading
from PySide6.QtWidgets import QApplication, QMainWindow
from omnipkg.mainwindow import MainWindow
import sys

action_queue = []
id_counter = 0

def add_action(action):
    action_queue.append(action)
    eel.populate_actions(action_queue)

def action_thread_target():
    while True:
        if len(action_queue) > 0:
            action = action_queue.pop()
            omni.run(*action)
            eel.populate_actions(action_queue)
            if action[0] == 'install':
                eel.update_entry(action[1], action[2], 'installed', True)
            elif action[0] == 'uninstall':
                eel.update_entry(action[1], action[2], 'installed', False)
            elif action[0] == 'update':
                eel.update_entry(action[1], action[2], 'updatable', False)
        else:
            time.sleep(0.01)

def run():

    omni.init()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

    action_thread = threading.Thread(target=action_thread_target)
    action_thread.start()

if __name__ == '__main__':
    run()