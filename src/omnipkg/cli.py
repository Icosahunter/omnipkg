import argparse
from omnipkg import Omnipkg
from tabulate import tabulate
import json

def search(args):
    print(format_results(omnipkg.run('search', **vars(args))))

def installed(args):
    print(format_results(omnipkg.run('installed', **vars(args))))

def updatable(args):
    print(format_results(omnipkg.run('updates', **vars(args))))

def install(args):
    print(omnipkg.run('install', **vars(args)))

def uninstall(args):
    omnipkg.run('uninstall', **vars(args))

def update(args):
    omnipkg.run('update', **vars(args))

def update_all(args):
    omnipkg.run('update_all', **vars(args))

def info(args):
    for info in omnipkg.run('info', **vars(args)):
        pm = info['pm']
        print(f'=== From {pm} ===\n')
        print(info['result'])
        print('\n\n')

def format_results(results):
    res = [[x['id'], x['name'], x['pm'], truncate_text(x['summary'], 60)] for x in results]
    return tabulate(res, headers=['id', 'name', 'pm', 'summary'])

def truncate_text(text, length):
    if len(text) <= length:
        return text
    else:
        return text[0:length-3] + '...'

parser = argparse.ArgumentParser(
    prog = 'omnipkg',
    description = 'A simple program for interfacing with multiple package management systems on Linux'
)

subparsers = parser.add_subparsers()
omnipkg = Omnipkg()
parser.set_defaults(func=parser.print_help)

search_parser = subparsers.add_parser('search', aliases=['sr', 'find'])
search_parser.add_argument('package')
search_parser.add_argument('--pm')
search_parser.set_defaults(func=search)

install_parser = subparsers.add_parser('install', aliases=['it'])
install_parser.add_argument('package')
install_parser.add_argument('--pm')
install_parser.set_defaults(func=install)

uninstall_parser = subparsers.add_parser('uninstall', aliases=['ut', 'remove', 'rm'])
uninstall_parser.add_argument('package')
uninstall_parser.add_argument('--pm')
uninstall_parser.set_defaults(func=uninstall)

update_parser = subparsers.add_parser('update', aliases=['up', 'upgrade'])
update_parser.add_argument('package')
update_parser.add_argument('--pm')
update_parser.set_defaults(func=update)

update_all_parser = subparsers.add_parser('update-all', aliases=['ua', 'upgrade-all'])
update_all_parser.add_argument('--pm')
update_all_parser.set_defaults(func=update_all)

info_parser = subparsers.add_parser('info', aliases=['if', 'show'])
info_parser.add_argument('package')
info_parser.add_argument('--pm')
info_parser.set_defaults(func=info)

installed_parser = subparsers.add_parser('installed', aliases=['li', 'list'])
installed_parser.add_argument('--pm')
installed_parser.set_defaults(func=installed)

updatable_parser = subparsers.add_parser('updates', aliases=['lu'])
updatable_parser.add_argument('--pm')
updatable_parser.set_defaults(func=updatable)

def run():
    omnipkg.init()
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    run()
