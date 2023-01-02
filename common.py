import subprocess
import json
import shlex
import re
import os

pkg_managers = []

for path in os.listdir('./pm-defs'):
    with open('./pm-defs/' + path) as f:
        pkg_managers.append(json.load(f))

def run(cmd, pkg=None, capture=False, privileged=False):
    command = cmd
    if pkg != None:
        command = command.format(package=pkg)
    if privileged:
        command = "pkexec " + command
    result = subprocess.run(shlex.split(command), capture_output=capture)
    if capture:
        return result.stdout.decode('utf8')
    else:
        return result.returncode
    
def search(package):
    results = []
    for pm in pkg_managers:
        results.extend(search_in_pm(package, pm))
    return results

def search_in_pm(package, pm):
    stdout = run(pm['search'][0], package, capture=True)
    regex = re.compile(pm['search'][1])
    return ((regex.search(line).group(0) for line in stdout.split('\n')))

def installed():
    results = []
    for pm in pkg_managers:
        results.extend(installed_in_pm(pm))
    return results

def installed_in_pm(pm):
    stdout = run(pm['installed'][0], capture=True)
    regex = re.compile(pm['installed'][1])
    return ((regex.search(line).group(0) for line in stdout.split('\n')))

def install(package):
    for pm in pkg_managers:
        if package in search_in_pm(package, pm):
            return run(pm['install'], package, privileged=True)
    return f'Package "{package}" not found in any repository.'

def uninstall(package):
    for pm in pkg_managers:
        if package in installed_in_pm(pm):
            run(pm['uninstall'], package, privileged=True)