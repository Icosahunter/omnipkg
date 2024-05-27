from parse import parse
from omnipkg.command import Command
from omnipkg.package import Package
import omnipkg.dirs as dirs
from pathlib import Path
import string

class PackageManager():

    def __init__(self, pm_def, omnipkg_instance):
        self.commands = {}
        self.privileged_commands = [ 'install', 'uninstall', 'update', 'update_all' ]
        self.rev_dns = None
        for k, v in pm_def.items():
            if k=='name':
                self.name = v
            elif k=='rev-dns':
                self.rev_dns = v
            else:
                self._add_command(k, v)
        self.installed_pkgs = None
        self.updatable_pkgs = None
        self.omnipkg = omnipkg_instance
        self.remotes = [x['remote'] for x in self.commands['remotes']()]
    
    def __str__(self):
        return self.name

    def _add_command(self, name, data):
        cmd = None
        parser = None
        privileged = name in self.privileged_commands
        if type(data) is list:
            cmd = data[0]
            parser = data[1]
        else:
            cmd = data
        self.commands[name] = Command(cmd, parser, privileged)
        #if not self.hasattr(name):
        #    self.setattr(name, self.commands[name])

    def index_packages(self):
        for query in string.ascii_letters + string.digits:
            for package in self.run('search', query):
                package._fill_missing_info()
        for package in self.run('installed'):
            package._fill_missing_info()

    def package_installed(self, id):
        if self.installed_pkgs == None:
            self.installed_pkgs = [x['id'] for x in self.commands['installed']()]
        return id in self.installed_pkgs
    
    def package_updatable(self, id):
        if self.updatable_pkgs == None:
            self.updatable_pkgs = [x['id'] for x in self.commands['updatable']()]
        return id in self.updatable_pkgs
    
    def package_exists(self, id):
        return id in [x.id for x in self.commands['search'](id=id)]
    
    def run(self, cmd, package):
        if cmd in ['install', 'uninstall']:
            self.installed_pkgs = None
        if cmd in ['install', 'uninstall', 'update', 'update-all']:
            self.updatable_pkgs = None
        result = self.commands[cmd](id=package)
        if cmd == 'search':
            if self.omnipkg.config['filter_search']: 
                result = [x for x in result if package in repr(x).lower()]
            if len(result) > self.omnipkg.config['search_results_limit']:
                result = result[0:self.omnipkg.config['search_results_limit']-1]
        result = [Package({'pm':self, **x}) for x in result if x['id'] != 'Name']
        return result