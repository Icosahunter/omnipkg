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
        self.rev_dns = pm_def.get('rev_dns', None)
        self.name = pm_def['name']
        for x in pm_def['commands']:
            self._add_command(x)
        self.installed_pkgs = None
        self.updatable_pkgs = None
        self.omnipkg = omnipkg_instance

    def __str__(self):
        return self.name

    def _add_command(self, data):
        privileged = data.get('privileged', data['name'] in self.privileged_commands)
        self.commands[data['name']] = Command(cmd=data['command'], parser=data.get('parser', None), skip_lines=data.get('skip_lines', 0), privileged=privileged)
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
        result = [Package({'pm':self, **x}) for x in result]
        if self.omnipkg.config['prefetch']:
            for key in self.omnipkg.config['columns']:
                for pkg in result:
                    pkg._fill_missing_info(key)
        #if self.omnipkg.config['prefetch_details_info']:
        #    for key in [x[1] for x in string.Formatter().parse(self.omnipkg.config[]) if not x[1] in [None, '']]
        return result
