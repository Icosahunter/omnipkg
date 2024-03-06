import omnipkg.common as omni
from pathlib import Path
import time
import threading

action_queue = []
id_counter = 0

@eel.expose
def install(pkgs):
    for pkg, pm in pkgs:
        add_action(('install', pkg, pm))

@eel.expose
def uninstall(pkgs):
    for pkg, pm in pkgs:
        add_action(('uninstall', pkg, pm))

@eel.expose
def update(pkgs):
    for pkg, pm in pkgs:
        add_action(('update', pkg, pm))

@eel.expose
def search(query):
    return omni.run('search', query)

@eel.expose
def is_installed(pkg, pm):
    return omni.is_installed(pkg, pm)

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
    action_thread = threading.Thread(target=action_thread_target)
    action_thread.start()
    eel.init(str(Path(__file__).parent / 'eel-gui'))
    eel.start('index.html', mode='')

if __name__ == '__main__':
    run()