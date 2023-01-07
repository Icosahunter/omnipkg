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

def install(args):
    print(omni.install(args.package))

def uninstall(args):
    omni.uninstall(args.package)

def update(args):
    omni.update(args.package)

def info(args):
    for info in omni.info(args.package):
        pm = info['pm']
        print(f'=== From {pm} ===\n')
        print(info['info'])
        print('\n\n')

search_parser = subparsers.add_parser('search')
search_parser.add_argument('package')
search_parser.set_defaults(func=search)

search_parser = subparsers.add_parser('install')
search_parser.add_argument('package')
search_parser.set_defaults(func=install)

search_parser = subparsers.add_parser('uninstall')
search_parser.add_argument('package')
search_parser.set_defaults(func=uninstall)

search_parser = subparsers.add_parser('update')
search_parser.add_argument('package')
search_parser.set_defaults(func=update)

search_parser = subparsers.add_parser('info')
search_parser.add_argument('package')
search_parser.set_defaults(func=info)

search_parser = subparsers.add_parser('installed')
search_parser.set_defaults(func=installed)

args = parser.parse_args()
args.func(args)