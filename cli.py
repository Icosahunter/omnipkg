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

search_parser = subparsers.add_parser('install', aliases=['it'])
search_parser.add_argument('package')
search_parser.set_defaults(func=install)

search_parser = subparsers.add_parser('uninstall', aliases=['ut'])
search_parser.add_argument('package')
search_parser.set_defaults(func=uninstall)

search_parser = subparsers.add_parser('update', aliases=['up'])
search_parser.add_argument('package')
search_parser.set_defaults(func=update)

search_parser = subparsers.add_parser('update-all', aliases=['ua'])
search_parser.set_defaults(func=update_all)

search_parser = subparsers.add_parser('info', aliases=['if'])
search_parser.add_argument('package')
search_parser.set_defaults(func=info)

search_parser = subparsers.add_parser('installed', aliases=['li'])
search_parser.set_defaults(func=installed)

search_parser = subparsers.add_parser('updatable', aliases=['lu'])
search_parser.set_defaults(func=updatable)

args = parser.parse_args()
args.func(args)