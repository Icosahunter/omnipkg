import subprocess
import json
import shlex
import re
import os

pkg_managers = []

for path in os.listdir('./pm-defs'):
    with open('./pm-defs/' + path) as f:
        pkg_managers.append(json.load(f))

def run(cmd, pkg=None):
    command = cmd
    if pkg != None:
        command = command.format(package=pkg)
    result = subprocess.run(shlex.split(command), capture_output=True)
    return result.stdout.decode('ascii')

def search(package):
    results = []
    for pm in pkg_managers:
        stdout = run(pm['search'][0], package)
        regex = re.compile(pm['search'][1])
        results.extend((regex.search(line).group(0) for line in stdout.split('\n')))
    return results