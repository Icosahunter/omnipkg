import subprocess
import json
import shlex
import os
import io
from enum import Enum
from PythonSed import Sed, SedException

pkg_managers = []
CaptureType = Enum('CaptureType', ['NONE', 'ALL', 'LINES'])

for path in os.listdir('./pm-defs'):
    with open('./pm-defs/' + path) as f:
        pkg_managers.append(json.load(f))

def run(cmd_name, pm_name=None, pkg_name=None, capture_type=CaptureType.NONE, run_privileged=False):
    result = 0
    pm = get_pm(pm_name)

    filter = type(pm[cmd_name]) == list
    if filter:
        cmd = pm[cmd_name][0]
    else:
        cmd = pm[cmd_name]

    if pkg_name != None:
        cmd = cmd.format(package=pkg_name)
    if run_privileged:
        cmd = "pkexec " + cmd

    result = subprocess.run(shlex.split(cmd), capture_output=(capture_type != CaptureType.NONE))

    if capture_type != CaptureType.NONE:
        result = result.stdout.decode('utf8')
        if filter:
            result = apply_sed(result, pm[cmd_name][1])
        if capture_type == CaptureType.ALL:
            result = {'result':'\n'.join(result), 'pm': pm_name}
        elif capture_type == CaptureType.LINES:
            result = [{'result':line, 'pm': pm_name} for line in result]
    else:
        result = {'result':result.returncode, 'pm': pm_name}
    
    return result

def run_for_all_pms(cmd_name, pkg_name=None, capture_type=CaptureType.NONE, run_privileged=False, only_run_for_first_find=False):
    results = []
    for pm in pkg_managers:
        result = run(cmd_name, pm['name'], pkg_name, capture_type, run_privileged)
        if capture_type == CaptureType.LINES:
            results.extend(result)
        else:
            results.append(result)
        
        if only_run_for_first_find and is_available(pkg_name):
            break
    return results

def get_pm(pm_name):
    return [pm for pm in pkg_managers if pm['name'] == pm_name][0]

def apply_sed(text, exp):
    sed = Sed()
    sed.no_autoprint = True
    sed.regexp_extended = True
    sed.load_string(exp)
    return (x.rstrip('\n') for x in sed.apply(io.StringIO(text), output=None))

def is_available(pkg_name, pm_name=None):
    return package in [pkg['result'] for pkg in search(pkg_name, pm_name)]

def is_updatable(pkg_name, pm_name=None):
    return pkg_name in [pkg['result'] for pkg in updatable(pm_name)]

def is_installed(pkg_name, pm_name=None):
    return pkg_name in [pkg['result'] for pkg in installed(pm_name)]

def search(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('search', pm_name, pkg_name, capture_type=CaptureType.LINES)
    else:
        return run_for_all_pms('search', pkg_name, capture_type=CaptureType.LINES)

def info(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('info', pm_name, pkg_name, capture_type=CaptureType.ALL)
    else:
        return run_for_all_pms('info', pkg_name, capture_type=CaptureType.ALL)

def installed(pm_name=None):
    if pm_name is not None:
        return run('installed', pm_name, capture_type=CaptureType.LINES)
    else:
        return run_for_all_pms('installed', capture_type=CaptureType.LINES)

def updatable(pm_name=None):
    if pm_name is not None:
        return run('updatable', pm_name, capture_type=CaptureType.LINES)
    else:
        return run_for_all_pms('updatable', capture_type=CaptureType.LINES)

def install(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('install', pm_name, pkg_name, capture_type=CaptureType.NONE, run_privileged=True)
    else:
        return run_for_all_pms('install', pkg_name, capture_type=CaptureType.NONE, run_privileged=True, only_run_for_first_find=True)

def uninstall(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('uninstall', pm_name, pkg_name, capture_type=CaptureType.NONE, run_privileged=True)
    else:
        return run_for_all_pms('uninstall', pkg_name, capture_type=CaptureType.NONE, run_privileged=True)

def update(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('update', pm_name, pkg_name, capture_type=CaptureType.NONE, run_privileged=True)
    else:
        return run_for_all_pms('update', pkg_name, capture_type=CaptureType.NONE, run_privileged=True)

def update_all(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('update-all', pm_name, pkg_name, capture_type=CaptureType.NONE, run_privileged=True)
    else:
        return run_for_all_pms('update-all', pkg_name, capture_type=CaptureType.NONE, run_privileged=True)