import subprocess
import json
import shlex
import os
import io
from PythonSed import Sed, SedException

pkg_managers = {}

for path in os.listdir('./pm-defs'):
    with open('./pm-defs/' + path) as f:
        pm = json.load(f)
        pkg_managers[pm['name']] = pm

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
    for pm in pkg_managers.values():
        results.extend(search_in_pm(package, pm))
    return results

def search_in_pm(package, pm):
    stdout = run(pm['search'][0], package, capture=True)
    lines = apply_sed(stdout, pm['search'][1])
    return ({'package': line, 'pm': pm['name']} for line in lines)

def installed():
    results = []
    for pm in pkg_managers.values():
        results.extend(installed_in_pm(pm))
    return results

def installed_in_pm(pm):
    stdout = run(pm['installed'][0], capture=True)
    lines = apply_sed(stdout, pm['installed'][1])
    return ({'package': line, 'pm': pm['name']} for line in lines)

def info(package):
    results = []
    for pm in pkg_managers.values():
        results.append(info_in_pm(package, pm))
    return results

def info_in_pm(package, pm):
    stdout = run(pm['info'][0], package, capture=True)
    lines = apply_sed(stdout, pm['info'][1])
    info = '\n'.join(lines)
    return {'info': info, 'pm': pm['name']}

def install(package):
    for pm in pkg_managers.values():
        if is_in_pm(package, pm):
            return run(pm['install'], package, privileged=True)
    print('oof')
    return f'Package "{package}" not found in any repository.'

def uninstall(package):
    for pm in pkg_managers.values():
        if is_in_pm(package, pm):
            run(pm['uninstall'], package, privileged=True)

def update(package):
    for pm in pkg_managers.values():
        if is_in_pm(package, pm):
            run(pm['update'], package, privileged=True)

def is_in_pm(package, pm):
    return package in [pkg['package'] for pkg in search_in_pm(package, pm)]

def apply_sed(text, exp):
    sed = Sed()
    sed.no_autoprint = True
    sed.regexp_extended = True
    sed.load_string(exp)
    return (x.rstrip('\n') for x in sed.apply(io.StringIO(text), output=None))