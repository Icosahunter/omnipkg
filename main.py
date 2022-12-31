import argparse
import subprocess
import json
import shlex
import re
import os

pkg_managers = []

for path in os.listdir('./pm-defs'):
    with open('./pm-defs/' + path) as f:
        pkg_managers.append(json.load(f))

parser = argparse.ArgumentParser(
    prog = 'omnipkg',
    description = 'A simple GUI for interfacing with multiple package management systems on Linux'
)

subparsers = parser.add_subparsers()

def run(cmd, pkg=None):
    command = cmd
    if pkg != None:
        command = command.format(package=pkg)
    result = subprocess.run(shlex.split(command), capture_output=True)
    return result.stdout.decode('ascii')

def search(args):
    for pm in pkg_managers:
        stdout = run(pm['search'][0], args.package)
        regex = re.compile(pm['search'][1])
        for line in stdout.split('\n'):
            print(regex.search(line).group(0))

search_parser = subparsers.add_parser('search')
search_parser.add_argument('package')
search_parser.set_defaults(func=search)

args = parser.parse_args()
args.func(args)