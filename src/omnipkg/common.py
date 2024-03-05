import appdirs
from pathlib import Path
from warnings import warn
import shutil
import subprocess
import json
import shlex
import os
import io
import re

# App info
app_name = 'omnipkg'
app_author = 'Nathaniel Markham'

# File paths
user_data_dir = Path(appdirs.user_data_dir(app_name, app_author))
user_config_dir = Path(appdirs.user_config_dir(app_name, app_author))
pm_defs_dir = user_config_dir / 'pm-defs/'
pkg_cache_path = user_data_dir / 'pkg-cache.json'
installed_path = Path(__file__).parent

# Other globals
cmd_options = {
    'install': {'run_privileged': True, 'only_run_for_first_find': True},
    'uninstall': {'run_privileged': True},
    'update': {'run_privileged': True},
    'update_all': {'run_privileged': True},
    'installed': {'capture_output': True},
    'updatable': {'capture_output': True},
    'info': {'capture_output': True},
    'search': {'capture_output': True}
}
cache = None
pkg_managers = []

for path in pm_defs_dir.glob('*'):
    with open(path) as f:
        pm_def = json.load(f)
        if shutil.which(pm_def['name']):
            pkg_managers.append(pm_def)

for path in (installed_path / 'data/pm-defs').glob('*'):
    pm_names = [pm['name'] for pm in pkg_managers]
    with open(path) as f:
        pm_def = json.load(f)
        if not pm_def['name'] in pm_names:
            if shutil.which(pm_def['name']):
                pkg_managers.append(pm_def)

def _run(cmd_name, pkg_name, pm_name, capture_output=False, run_privileged=False, only_run_for_first_find=False):
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
            result = _filter(result, pm[cmd_name][1])
            for x in result:
                x['pm'] = pm_name
                if cmd_name != 'installed':
                    x['installed'] = is_installed(x['id'], x['pm'])
                else:
                    x['installed'] = True
                if cmd_name != 'updatable':
                    x['updatable'] = is_updatable(x['id'], x['pm'])
                if 'id' in x and not 'name' in x:
                    x['name'] = _id_to_name(x['id'])
    else:
        result = {'return_code':result.returncode, 'pm': pm_name}

    return result

def _run_for_all_pms(cmd_name, pkg_name, capture_output=False, run_privileged=False, only_run_for_first_find=False):
    results = []
    for pm in pkg_managers:
        result = _run(cmd_name, pkg_name, pm['name'], capture_output, run_privileged)
        results.extend(result)
        if only_run_for_first_find and is_available(pkg_name):
            break
    return results

def run(cmd, pkg=None, pm=None):
    if pm is None:
        return _run_for_all_pms(cmd, pkg, **cmd_options[cmd])
    else:
        return _run(cmd, pkg, pm, **cmd_options[cmd])

def get_pm(pm_name):
    return [pm for pm in pkg_managers if pm['name'] == pm_name][0]

def _filter(text, exp):
    res = re.finditer(exp, text)
    res = [x.groupdict() for x in res]
    return res

def _id_to_name(id):
    name = id
    
    if '-' in id:
        name = name.replace('-', ' ')
    elif '_' in id:
        name = name.replace('_', ' ')
    elif '.' in id:
        name = name.replace('.', ' ')

    name = name.title()
    return name

def _format_info(info):
    paragraph = '          '
    for line in info['info'].split('\n'):
        paragraph += line.strip() + ' '
    info['info'] = paragraph
    return info

def _truncate_text(text, size):
    if len(text) > size:
        return text[0:size-3] + '...'
    else:
        return text

def is_available(pkg_name, pm_name=None):
    return pkg_name in [pkg['id'] for pkg in search(pkg_name, pm_name)]

def is_updatable(pkg_name, pm_name=None):
    if cache is not None:
        return pkg_name in [pkg['id'] for pkg in cache['updatable']]
    else:
        warn('Cache not set. Update the cache for accurate is_updatable values.')
        return None

def is_installed(pkg_name, pm_name=None):
    if cache is not None:
        return pkg_name in [pkg['id'] for pkg in cache['installed']]
    else:
        warn('Cache not set. Update the cache for accurate is_installed values.')
        return None

def update_cache():
    global cache
    data = {
        'installed' : run('installed'),
        'updatable' : run('updatable')
    }
    cache = data
    with open(pkg_cache_path, 'w+') as f:
        f.write(json.dumps(data, indent=4))

def load_cache():
    global cache
    if pkg_cache_path.exists():
        with open(pkg_cache_path, 'r') as f:
            cache = json.loads(f.read())

def _create_directories():
    user_data_dir.mkdir(exist_ok=True)
    user_config_dir.mkdir(exist_ok=True)
    pm_defs_dir.mkdir(exist_ok=True)

def init():
    _create_directories()
    update_cache()
