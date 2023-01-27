import argparse
import common as omni
from tabulate import tabulate

parser = argparse.ArgumentParser(
    prog = 'omnipkg',
    description = 'A simple program for interfacing with multiple package management systems on Linux'
)

subparsers = parser.add_subparsers()

def search(args):
    print(tabulate(omni.search(args.package)))

def installed(args):
    print(tabulate(omni.installed()))

def updatable(args):
    print(tabulate(omni.updatable()))

def install(args):
    print(omni.install(args.package))

def uninstall(args):
    omni.uninstall(args.package)

def update(args):
    omni.update(args.package)

def update_all(args):
    omni.update_all(args.package)

def info(args):
    for info in omni.info(args.package):
        pm = info['pm']
        print(f'=== From {pm} ===\n')
        print(info['result'])
        print('\n\n')

search_parser = subparsers.add_parser('search', aliases=['sr'])
search_parser.add_argument('package')
search_parser.set_defaults(func=search)

install_parser = subparsers.add_parser('install', aliases=['it'])
install_parser.add_argument('package')
install_parser.set_defaults(func=install)

uninstall_parser = subparsers.add_parser('uninstall', aliases=['ut'])
uninstall_parser.add_argument('package')
uninstall_parser.set_defaults(func=uninstall)

update_parser = subparsers.add_parser('update', aliases=['up'])
update_parser.add_argument('package')
update_parser.set_defaults(func=update)

update_all_parser = subparsers.add_parser('update-all', aliases=['ua'])
update_all_parser.set_defaults(func=update_all)

info_parser = subparsers.add_parser('info', aliases=['if'])
info_parser.add_argument('package')
info_parser.set_defaults(func=info)

installed_parser = subparsers.add_parser('installed', aliases=['li'])
installed_parser.set_defaults(func=installed)

updatable_parser = subparsers.add_parser('updatable', aliases=['lu'])
updatable_parser.set_defaults(func=updatable)

args = parser.parse_args()
args.func(args)