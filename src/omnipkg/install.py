from pathlib import Path
import shutil
import os
import subprocess
import shlex

linux_appfiles = [
    ('data/appfiles/omnipkg.desktop', '/usr/share/applications/omnipkg.desktop'),
    ('data/appfiles/omnipkg.xpm', '/usr/share/pixmaps/omnipkg.xpm'),
    ('data/appfiles/omnipkg.png', '/usr/share/icons/hicolor/48x48/apps/omnipkg.png'),
    ('data/appfiles/omnipkg.svg', '/usr/share/icons/hicolor/scalable/apps/omnipkg.svg')
]

def install_files(files):
    cmds = 'pkexec sh -c \''
    for file in files:
        cmds += f'cp "{str(Path(__file__).parent / file[0])}" "{Path(file[1]).parent}"; '
    cmds += '\''
    subprocess.run(shlex.split(cmds))

def uninstall_files(files):
    cmds = 'pkexec sh -c \''
    for file in files:
        cmds += f'sudo rm "{file[1]}"; '
    cmds += '\''
    subprocess.run(shlex.split(cmds))