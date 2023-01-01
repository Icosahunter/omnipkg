import argparse
import common as omni

parser = argparse.ArgumentParser(
    prog = 'omnipkg',
    description = 'A simple GUI for interfacing with multiple package management systems on Linux'
)

subparsers = parser.add_subparsers()

def search(args):
    for line in omni.search(args.package):
        print(line)

search_parser = subparsers.add_parser('search')
search_parser.add_argument('package')
search_parser.set_defaults(func=search)

args = parser.parse_args()
args.func(args)