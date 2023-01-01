import argparse
import common as omni

parser = argparse.ArgumentParser(
    prog = 'omnipkg',
    description = 'A simple program for interfacing with multiple package management systems on Linux'
)

subparsers = parser.add_subparsers()

def search(args):
    for line in omni.search(args.package):
        print(line)

def install(args):
    print(omni.install(args.package))

def uninstall(args):
    omni.uninstall(args.package)

search_parser = subparsers.add_parser('search')
search_parser.add_argument('package')
search_parser.set_defaults(func=search)

search_parser = subparsers.add_parser('install')
search_parser.add_argument('package')
search_parser.set_defaults(func=install)

search_parser = subparsers.add_parser('uninstall')
search_parser.add_argument('package')
search_parser.set_defaults(func=uninstall)

args = parser.parse_args()
args.func(args)