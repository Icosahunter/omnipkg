import appdirs
from pathlib import Path
import shutil
import subprocess
import json
import shlex
import os
import io
import re

app_name = 'omnipkg'
app_author = 'Nathaniel Markham'
user_data_dir = Path(appdirs.user_data_dir(app_name, app_author))
user_config_dir = Path(appdirs.user_config_dir(app_name, app_author))
user_data_dir.mkdir(exist_ok=True)
user_config_dir.mkdir(exist_ok=True)
pm_defs_dir = user_config_dir / 'pm-defs/'
pkg_cache_path = user_data_dir / 'pkg-cache.json'
cache = None

pkg_managers = []

pm_defs_dir.mkdir(exist_ok=True)

for path in pm_defs_dir.glob('*'):
    with open(path) as f:
        pm_def = json.load(f)
        if shutil.which(pm_def['name']):
            pkg_managers.append(pm_def)

def run(cmd_name, pm_name=None, pkg_name=None, capture_output=False, run_privileged=False):
    result = 0
    pm = get_pm(pm_name)
    cmd = pm[cmd_name]
    filter_results = False

    if type(cmd) is list:
        cmd = cmd[0]
        filter_results = True

    if pkg_name != None:
        cmd = cmd.format(package=pkg_name)
    if run_privileged:
        cmd = "pkexec " + cmd

    result = subprocess.run(shlex.split(cmd), capture_output=capture_output)

    if capture_output:
        result = result.stdout.decode('utf8')
        if filter_results:
            result = filter(result, pm[cmd_name][1])
            for x in result:
                x['pm'] = pm_name
                if 'id' in x and not 'name' in x:
                    x['name'] = id_to_name(x['id'])

    else:
        result = {'return_code':result.returncode, 'pm': pm_name}
    
    return result

def run_for_all_pms(cmd_name, pkg_name=None, capture_output=False, run_privileged=False, only_run_for_first_find=False):
    results = []
    for pm in pkg_managers:
        result = run(cmd_name, pm['name'], pkg_name, capture_output, run_privileged)
        results.extend(result)
        if only_run_for_first_find and is_available(pkg_name):
            break
    return results

def get_pm(pm_name):
    return [pm for pm in pkg_managers if pm['name'] == pm_name][0]

def filter(text, exp):
    res = re.finditer(exp, text)
    res = [x.groupdict() for x in res]
    return res

def id_to_name(id):
    name = id
    
    if '-' in id:
        name = name.replace('-', ' ')
    elif '_' in id:
        name = name.replace('_', ' ')
    elif '.' in id:
        name = name.replace('.', ' ')

    name = name.title()
    return name

def format_info(info):
    paragraph = '          '
    for line in info['info'].split('\n'):
        paragraph += line.strip() + ' '
    info['info'] = paragraph
    return info

def truncate_text(text, size):
    if len(text) > size:
        return text[0:size-3] + '...'
    else:
        return text

def is_available(pkg_name, pm_name=None):
    return package in [pkg['id'] for pkg in search(pkg_name, pm_name)]

def is_updatable(pkg_name, pm_name=None):
    if cache is not None:
        return pkg_name in [pkg['id'] for pkg in cache['updatable']]
    else:
        return pkg_name in [pkg['id'] for pkg in updatable(pm_name)]

def is_installed(pkg_name, pm_name=None):
    if cache is not None:
        return pkg_name in [pkg['id'] for pkg in cache['installed']]
    else:
        return pkg_name in [pkg['id'] for pkg in installed(pm_name)]

def search(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('search', pm_name, pkg_name)
    else:
        return run_for_all_pms('search', pkg_name, capture_output=True)

def info(pkg_name, pm_name=None):
    if pm_name is not None:
        return [format_info(x) for x in run('info', pm_name, pkg_name, capture_output=True)]
    else:
        return [format_info(x) for x in run_for_all_pms('info', pkg_name, capture_output=True)]

def installed(pm_name=None):
    if pm_name is not None:
        return run('installed', pm_name, capture_output=True)
    else:
        return run_for_all_pms('installed', capture_output=True)

def updatable(pm_name=None):
    if pm_name is not None:
        return run('updatable', pm_name, capture_output=True)
    else:
        return run_for_all_pms('updatable', capture_output=True)

def install(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('install', pm_name, pkg_name, run_privileged=True)
    else:
        return run_for_all_pms('install', pkg_name, run_privileged=True, only_run_for_first_find=True)

def uninstall(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('uninstall', pm_name, pkg_name, run_privileged=True)
    else:
        return run_for_all_pms('uninstall', pkg_name, run_privileged=True)

def update(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('update', pm_name, pkg_name, run_privileged=True)
    else:
        return run_for_all_pms('update', pkg_name, run_privileged=True)

def update_all(pkg_name, pm_name=None):
    if pm_name is not None:
        return run('update-all', pm_name, pkg_name, run_privileged=True)
    else:
        return run_for_all_pms('update-all', pkg_name, run_privileged=True)

def update_cache():
    global cache
    data = {
        'installed' : installed(),
        'updatable' : updatable()
    }
    cache = data
    with open(pkg_cache_path, 'w+') as f:
        f.write(json.dumps(data, indent=4))

def load_cache():
    global cache
    if pkg_cache_path.exists():
        with open(pkg_cache_path, 'r') as f:
            cache = json.loads(f.read())